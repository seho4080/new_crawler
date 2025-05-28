import os
import datetime
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import FlinkKafkaConsumer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.typeinfo import Types
from pyflink.datastream.functions import MapFunction, RuntimeContext
from pyflink.common import Configuration
import json
from consumer.preprocess import Preprocess
from dotenv import load_dotenv
import psycopg2
import re


class PreprocessMap(MapFunction):
    def __init__(self):
        self.HOST = os.getenv("DB_HOST")
        self.USERNAME = os.getenv("DB_USERNAME")
        self.DB_NAME = os.getenv("DB_NAME")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD")

    def extract_writer(self, content):
        match = re.search(r'([가-힣]{2,4})\s?기자', content)
        return match.group(1) if match else "연합뉴스"

    def map(self, value):
        data = json.loads(value)
        gpt = Preprocess()

        print(data)
        print()

        title = data.get("title", "제목 없음").strip()
        write_date_str = data.get("write_date", "2025-04-18 00:00:00")
        origin_content = data.get("content", "").strip()
        url = data.get("url", "")
        
        try:
            # 다양한 날짜 형식 처리를 위한 시도
            for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%a, %d %b %Y %H:%M:%S %z'):
                try:
                    write_date = datetime.datetime.strptime(write_date_str, fmt)
                    break  # 성공하면 루프 탈출
                except ValueError:
                    pass
            else:
                # 모든 형식에서 실패한 경우
                print(f"날짜 파싱 실패: {write_date_str}")
                write_date = datetime.datetime(1990, 1, 1)  # 기본 날짜
        except Exception as e:
            print(f"날짜 처리 중 오류 발생: {e}, 원본 날짜: {write_date_str}")
            write_date = datetime.datetime(1990, 1, 1)  # 오류 발생 시 기본 날짜

        content = gpt.preprocess_content(origin_content)
        writer = self.extract_writer(content)
        keywords = gpt.transform_extract_keywords(content)
        category = gpt.transform_classify_category(content)
        embedding = gpt.transform_to_embedding(content)

        # postgreSQL에 저장
        conn = psycopg2.connect(
            host=self.HOST,
            database=self.DB_NAME,
            user=self.USERNAME,
            password=self.DB_PASSWORD
        )
        
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO news_article
                (title, writer, write_date, category, content, url, keywords, embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (url) DO NOTHING
            """, (
                title,
                writer,
                write_date,
                category,
                content,
                url,  
                keywords,
                embedding
            ))
        except Exception as e:
            print(f"{e}, DB 삽입 에러 발생")
        
        conn.commit()
        cursor.close()
        conn.close()

        return (
            title,
            writer,
            write_date,
            category,
            content,
            url,
            keywords,
            embedding
        )



load_dotenv()

config = Configuration()
config.set_string("pipeline.jars", "file:///usr/local/kafka/flink-sql-connector-kafka-3.0.1-1.18.jar")

# Flink 환경 생성
env = StreamExecutionEnvironment.get_execution_environment(configuration=config)
env.set_parallelism(1)


kafka_consumer = FlinkKafkaConsumer(
    topics='news-topic',
    deserialization_schema=SimpleStringSchema(),
    properties={
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'flink-news-group'
    }
)

stream = env.add_source(kafka_consumer).map(PreprocessMap(), output_type=Types.TUPLE([
    Types.STRING(),  # title
    Types.STRING(),  # writer
    Types.SQL_TIMESTAMP(),  # write_date
    Types.STRING(),  # category
    Types.STRING(),  # content
    Types.STRING(),  # url
    Types.STRING(),  # keywords
    Types.LIST(Types.FLOAT()) # embedding (VECTOR 타입은 직접 지원하지 않으므로 LIST<FLOAT>으로 처리)
]))

stream.print()

# 실행
env.execute("Consumer -> Flink -> PostgreSQL")