# -*- coding: utf-8 -*-
import sys
import json
from datetime import datetime

from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, decode, from_json, to_timestamp
from pyspark.sql.types import *


# 처리를 위해 필요한 스키마 1. Tweet 2. User 3. Quoted
tweet_schema = [
    'id',
    'text',
    'author_id',
    'created_at',
    'lang',

    # 시간 정보
    "timestamp",

    # 따로 처리해야하는 내용들
    'hashtags',  # hashtags.tag
    "retweet_count",  # public_metrics.retweet_count
    "reply_count",  # public_metrics.reply_count
    "like_count",  # public_metrics.like_count
    "quote_count",  # public_metrics.quote_count
]  # user, quoted_status, in_reply_to_status_id 은 따로 처리

schema = StructType([
    StructField("id", LongType(), False),
    StructField("text", StringType(), False),
    StructField("author_id", LongType(), False),
    StructField("created_at", StringType(), False),
    StructField("lang", StringType(), True),
    StructField("timestamp", TimestampType(), False),
    StructField("hashtags", StringType(), True),
    StructField("retweet_count", IntegerType(), True),
    StructField("reply_count", IntegerType(), True),
    StructField("like_count", IntegerType(), True),
    StructField("quote_count", IntegerType(), True),
])


if __name__ == "__main__":
    spark = SparkSession.builder\
        .master("spark://spark-master:7077")\
        .appName("Streamer") \
        .config("spark.executor.memory", "512m")\
        .config("spark.cassandra.connection.host", "cassandra") \
        .config("spark.cassandra.connection.port", "9042") \
        .config("spark.cassandra.auth.password", "cassandra") \
        .config("spark.cassandra.auth.username", "cassandra") \
        .config("spark.sql.catalog.mycatalog", "com.datastax.spark.connector.datasource.CassandraCatalog") \
        .getOrCreate()
    sc = spark.sparkContext

    # Initialize namespace and table
    spark.sql("CREATE DATABASE IF NOT EXISTS mycatalog.test WITH DBPROPERTIES (class='SimpleStrategy',replication_factor='1')")
    spark.sql("drop table mycatalog.test.testtable")
    spark.sql("""CREATE TABLE mycatalog.test.testtable (
                    id bigint,
                    text string,
                    author_id bigint,
                    created_at string,
                    lang string,
                    timestamp timestamp,
                    hashtags string,
                    retweet_count int,
                    reply_count int,
                    like_count int,
                    quote_count int
                )
                USING cassandra
                PARTITIONED BY (id)""")
    spark.sql("SHOW NAMESPACES FROM mycatalog").show()
    spark.sql("SHOW TABLES FROM mycatalog.test").show()

    # https://spark.apache.org/docs/latest/structured-streaming-kafka-integration.html
    df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:9092") \
        .option("subscribe", "tweets") \
        .load()
    ds = df \
        .withColumn("value", decode("value", "utf8")) \
        .withColumn("value", from_json("value", schema)) \
        .select("value.*") \
        .withColumn("created_at", to_timestamp("created_at", "yyyy-MM-dd HH:mm:ss Z")) \
        .withColumn("timestamp", current_timestamp()) \
        .writeStream \
        .format("org.apache.spark.sql.cassandra") \
        .outputMode("append") \
        .options(table="testtable", keyspace="test", checkpointLocation="./cassandra_checkpoints") \
        .start() \
        .awaitTermination()
