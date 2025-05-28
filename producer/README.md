# 📰 Producer

연합뉴스 RSS 피드에서 뉴스 데이터를 수집하고, 본문 내용을 크롤링하여 Kafka로 전송하는 뉴스 프로듀서입니다.

---

## ✅ 주요 기능

- 연합뉴스의 다양한 카테고리(RSS 피드)에서 뉴스 수집
- 뉴스 기사 본문을 크롤링하여 콘텐츠 보강
- Kafka 토픽으로 실시간 데이터 전송 (`news-topic`)
- 기사 제목, 작성일, 본문, URL 정보를 JSON 형태로 전송

---

## 📦 사용 라이브러리

- `feedparser`: RSS 파싱
- `BeautifulSoup`: HTML 본문 크롤링
- `requests`, `urllib.request`: 웹 요청 처리
- `kafka-python`: Kafka 메시지 전송
- `json`, `time`, `ssl`: 유틸

---

## 🛠️ 설정값

- **Kafka 브로커 주소**: `localhost:9092`  
  → 필요 시 환경 변수 또는 `.env`로 분리 추천
- **Kafka 토픽 이름**: `news-topic`

---

## 🧪 실행 방법
kafka 실행    
1. Zookeeper 실행

    ```bash
    $KAFKA_HOME/bin/zookeeper-server-start.sh $KAFKA_HOME/config/zookeeper.properties
    ```

2. Kafka 브로커 실행

    ```bash
    $KAFKA_HOME/bin/kafka-server-start.sh $KAFKA_HOME/config/server.properties
    ```
    
3. topic 생성

    ```bash
    $KAFKA_HOME/bin/kafka-topics.sh --create \
    --bootstrap-server localhost:9092 \
    --replication-factor 1 \
    --partitions 1 \
    --topic news-topic
    ```

4. produce.py실행
```bash
# Kafka 서버가 실행 중이어야 함
python produce.py
```

---

## 발전 방향

### ✅ 1. 수집 대상 확장
- 연합뉴스 외 **다양한 언론사 RSS 피드 추가**
- 포털 뉴스(네이버, 다음 등) 기반 크롤링 기능 연동
- 해외 뉴스(RSS 또는 API) 추가하여 **다국어 뉴스 수집**

### ✅ 2. Kafka 연동 개선
- **에러 핸들링 및 재전송 로직** 구현 (retry, dead-letter queue 등)
- 전송 성공/실패 **로깅 및 메트릭 수집**
- Kafka 토픽을 **카테고리별로 분리**하여 처리 유연성 증가


### ✅ 3. 스케줄링 자동화
- 현재는 수동 실행 → **Airflow, Cron 등으로 자동화**
- **주기별로 수집된 뉴스 내역 로그화 및 저장**

### ✅ 4. 데이터 유효성 검사 강화
- 기사 본문의 길이, 구조를 기반으로 **불완전한 뉴스 제거**
- `produce.py` 내에서 **제목/본문/URL 누락 여부 체크 후 Kafka 전송 필터링**
- 중복 제거는 `consumer` 또는 저장 단계에서 **DB 기준 비교 후 처리**