# -*- coding: utf-8 -*-
import sys
import time
import json
from datetime import datetime

from pyspark.streaming import StreamingContext

from pyspark.sql import SparkSession, Row
from pyspark.sql.functions import *
from pyspark.sql.types import *

# import pyspark_cassandra # saveToCassandra 함수, package 추가 필요

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
    'hashtags',  # entities.hashtags.tag
    "retweet_count",  # public_metrics.retweet_count
    "reply_count",  # public_metrics.reply_count
    "like_count",  # public_metrics.like_count
    "quote_count",  # public_metrics.quote_count
]  # user, quoted_status, in_reply_to_status_id 은 따로 처리


# JSON 형태의 RDD 필터링 함수
def tweet_filter(RDD):
    filtered = {}
    try:
        # tweet_schema 처리
        def tweet_lambda(x): return (x in tweet_schema)
        existing_keys = list(filter(tweet_lambda, RDD.keys()))
        for key in existing_keys:
            filtered[key] = RDD[key]

        # time 정보 추가
        filtered["timestamp"] = int(time.time()*1000000)

        # 추가 정보
        filtered['hashtags'] = [hashtag["tag"]
                                for hashtag in RDD["entities"]["hashtags"]]  # entities.hashtags.tag
        # public_metrics.retweet_count
        filtered["retweet_count"] = RDD["public_metrics"]["retweet_count"]
        # public_metrics.reply_count
        filtered["reply_count"] = RDD["public_metrics"]["reply_count"]
        # public_metrics.like_count
        filtered["like_count"] = RDD["public_metrics"]["like_count"]
        # public_metrics.quote_count
        filtered["quote_count"] = RDD["public_metrics"]["quote_count"]

    except:
        print("**********TWEET FILTER ERROR OCCUR**********")
        print("Unexpected error:", sys.exc_info())
        print(RDD)

    return filtered


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

    ds = df.writeStream \
        .foreach(tweet_filter) \
        .format("org.apache.spark.sql.cassandra") \
        .outputMode("append") \
        .options(table="testtable", keyspace="test", checkpointLocation="./cassandra_checkpoints") \
        .start()
