## 설치

```
pip install -r requirements.txt
```

## 실행

아래 명령어 읽고 docker-compose 실행

```
python commands.py

usage: commands.py [-h] [--spark-workers] [--hadoop] [--build] {up,down}
```

Twitter -> Kafka로 저장하는 producer 실행

```
cd DataPipeline
cd src
bash producer.sh
```

Kafka -> Spark -> Cassandra로 저장하는 consumer 실행

```
bash consumer.sh
```

TwitterKafkaConsumer.py 파일을 확인하여 spark session을 만든 후 아래 코드로 확인 가능

```
spark.sql("SELECT * FROM mycatalog.test.testtable")
```

## 개발

localhost:8888/lab 에 접속하면 jupyter lab을 통해 server 폴더가서 개발 가능
