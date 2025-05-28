from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import FlinkKafkaConsumer, FileSink, OutputFileConfig, RollingPolicy, BucketAssigner
from pyflink.common.serialization import SimpleStringSchema, Encoder
from pyflink.common.typeinfo import Types
from pyflink.common import Configuration
from pyflink.datastream.functions import MapFunction
import json, psycopg2, requests, datetime, os, re
from urllib.parse import quote
from consumer.preprocess import Preprocess
from dotenv import load_dotenv
from dateutil import parser as date_parser
from hdfs import InsecureClient


load_dotenv()


# ✅ 날짜 기반 버킷 디렉토리 분기 클래스
class DateBucketAssigner(BucketAssigner):
    def get_bucket_id(self, element, context):
        try:
            data = json.loads(element)
            write_date = date_parser.parse(data["write_date"])
            return f"{write_date.year}/{write_date.month:02}/{write_date.day:02}"
        except Exception:
            return "unknown"

    def get_serializer(self):
        return SimpleStringSchema()


# ✅ Kafka → PG/ES → HDFS JSON 반환
class PgThenEs(MapFunction):

    def open(self, runtime_context):
        self.conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD")
        )
        self.cursor = self.conn.cursor()
        self.session = requests.Session()
        self.es_url = "http://localhost:9200/news/_doc/"
        self.HDFS_CLIENT = InsecureClient("http://localhost:9870", user="ssafy")

    def close(self):
        self.cursor.close()
        self.conn.close()
        self.session.close()

    def extract_writer(self, content):
        match = re.search(r'([가-힣]{2,4})\s?기자', content)
        return match.group(1) if match else "연합뉴스"

    def map(self, value):
        processed_json = {}
        try:
            data = json.loads(value)
            gpt = Preprocess()

            title = data.get("title", "제목 없음").strip()
            write_date_str = data.get("write_date", "2025-04-18 00:00:00")
            origin_content = data.get("content", "").strip()
            url = data.get("url", "")

            # 날짜 파싱
            for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%a, %d %b %Y %H:%M:%S %z'):
                try:
                    write_date = date_parser.parse(write_date_str)
                    break
                except:
                    write_date = datetime.datetime(1990, 1, 1)

            # 전처리
            content = gpt.preprocess_content(origin_content)
            writer = self.extract_writer(content)
            keywords = gpt.transform_extract_keywords(content)
            category = gpt.transform_classify_category(content)
            embedding = gpt.transform_to_embedding(content)

            # PG INSERT
            self.cursor.execute("""
                INSERT INTO news_article
                (title, writer, write_date, category, content, url, keywords, embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (url) DO NOTHING
            """, (title, writer, write_date, category, content, url, keywords, json.dumps(embedding)))
            self.conn.commit()

            if self.cursor.rowcount > 0:
                # ES 전송
                doc_id = quote(url, safe='')
                doc = {
                    "title": title,
                    "writer": writer,
                    "write_date": write_date.isoformat(),
                    "category": category,
                    "content": content,
                    "url": url,
                    "keywords": keywords,
                    "updated_at": datetime.datetime.utcnow().isoformat()
                }
                resp = self.session.put(self.es_url + doc_id, json=doc)
                if resp.ok:
                    print("✅ PG + ES 완료:", title)
                else:
                    print("❌ ES 실패:", resp.status_code, resp.text)

                # HDFS로 넘길 JSON
                processed_json = {
                    "title": title,
                    "writer": writer,
                    "write_date": write_date.isoformat(),
                    "category": category,
                    "content": content,
                    "url": url,
                    "keywords": keywords,
                    "embedding": embedding
                }
                try:
                    hdfs_path = f"/user/hadoop/news/{datetime.datetime.now().strftime('%Y/%m/%d')}/news_{datetime.datetime.now().strftime('%H%M%S_%f')}.json"
                    self.HDFS_CLIENT.write(hdfs_path, data=json.dumps(processed_json, ensure_ascii=False), overwrite=True)
                    print(f"✅ HDFS 저장 완료: {hdfs_path}")
                except Exception as e:
                    print(f"❌ HDFS 저장 실패: {e}")

                return json.dumps(processed_json, ensure_ascii=False)

            else:
                print("⚠️ 중복 URL로 PG 삽입 안 됨")
                return None

        except Exception as e:
            print("❌ 전체 처리 중 오류:", e)
            return json.dumps(processed_json)



# ✅ Flink 환경 구성
config = Configuration()
config.set_string("pipeline.jars", "file:///usr/local/kafka/flink-sql-connector-kafka-3.0.1-1.18.jar")

env = StreamExecutionEnvironment.get_execution_environment(configuration=config)
env.set_parallelism(1)

# ✅ Kafka Consumer
kafka_consumer = FlinkKafkaConsumer(
    topics='news-topic',
    deserialization_schema=SimpleStringSchema(),
    properties={'bootstrap.servers': 'localhost:9092', 'group.id': 'flink-combined'}
)


# ✅ 스트림 구성 및 실행
stream = env.add_source(kafka_consumer) \
    .map(PgThenEs(), output_type=Types.STRING()) \
    .filter(lambda x: x not in [None, "", "{}"])

# stream.print()

env.execute("Kafka → PG → ES → HDFS (날짜별)")
