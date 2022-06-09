# https://community.datastax.com/questions/6606/errors-when-using-spark-cassandra-connector-30.html

spark-submit \
    --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.0 \
    --jars ./jars/spark-cassandra-connector-assembly_2.12-3.0.0.jar \
    TwitterKafkaConsumer.py
# --jars jars/spark-streaming-kafka-0-10_2.12-3.2.1.jar \
