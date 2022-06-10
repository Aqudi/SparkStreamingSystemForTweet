# -*- coding: utf-8 -*-
import argparse
import logging
import os
import json

import tweepy
from kafka import KafkaProducer
from kafka.errors import KafkaError

from dotenv import load_dotenv

load_dotenv(verbose=True)


logger = logging.getLogger("kafka_producer")


class Producer:
    def __init__(self, bootstrap_servers):
        logger.info("Kafka Producer Object Create")
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers,
                max_block_ms=10000,
                retries=0,  # default value
                acks=1,  # default value
                value_serializer=lambda v: json.dumps(
                    v, ensure_ascii=False).encode("utf-8")
            )
        except KafkaError as exc:
            logger.error(
                "kafka producer - Exception during connecting to broker - {}".format(exc))
            return False

    def stop(self):
        self.producer.close()

    def send_data(self, topic, data):
        # Asynchronous by default
        future = self.producer.send(topic, data).add_callback(
            self.on_send_success).add_errback(self.on_send_error)
        # block until all async messages are sent
        self.producer.flush()

    def on_send_success(self, record_metadata):
        logger.info("**********Send Success***********")
        logger.info(f"record_metadata.topic: {record_metadata.topic}")
        logger.info(f"record_metadata.partition: {record_metadata.partition}")
        logger.info(f"record_metadata.offset: {record_metadata.offset}")

    def on_send_error(self, excp):
        logger.info("**********Send Error Occur**********")
        logger.error("I am an errback", exc_info=excp)


class TwitterStreamingClient(tweepy.StreamingClient):
    """ A class to read the twitter stream and push it to Kafka"""

    def __init__(self, **kwargs):
        super(TwitterStreamingClient, self).__init__(**kwargs)
        self.producer = Producer(bootstrap_servers="kafka:9092")

    def parseInt(self, string):
        try:
            return int(string)
        except:
            return 0

    def on_tweet(self, tweet: tweepy.Tweet):
        try:
            hastags = ""
            if "hashtags" in (tweet.entities or {}):
                hastags = ",".join(
                    [tagDict["tag"] for tagDict in tweet.entities.get("hashtags")])
            data = {
                "id": tweet.id,
                "text": tweet.text,
                "author_id": tweet.author_id,
                "created_at": tweet.created_at.strftime("%Y-%M-%d %H:%m:%S %z"),
                "lang": tweet.lang,
                "hashtags": hastags,
                "retweet_count": tweet.public_metrics["retweet_count"],
                "reply_count": tweet.public_metrics["reply_count"],
                "like_count": tweet.public_metrics["like_count"],
                "quote_count": tweet.public_metrics["quote_count"],
            }
            self.producer.send_data("tweets", data)
        except KafkaError as e:
            logger.error(e)
            return False

    def on_errors(self, erros):
        logger.error(erros)
        return True  # Don't kill the stream

    def on_timeout(self):
        return True  # Don't kill the stream


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rules", nargs="+",
                        help="필터링할 rule, hashtag (띄어쓰기로 구분)", default=[])
    args = parser.parse_args()
    logger.info(args)

    logging.basicConfig(
        format="%(asctime)s.%(msecs)s:%(name)s:%(thread)d:%(levelname)s:%(process)d:%(message)s",
        level=logging.INFO
    )

    BEARER_TOKEN = os.getenv("BEARER_TOKEN")

    # Create stream and bind the listener to it
    stream = TwitterStreamingClient(
        bearer_token=BEARER_TOKEN,
    )
    res = stream.get_rules()
    if res.data:
        logger.debug(res.data)
        rule_ids = [rule.id for rule in res.data]
        stream.delete_rules(rule_ids)

    for track in args.rules:
        stream.add_rules(tweepy.StreamRule(track))

    res = stream.get_rules()
    if res.data:
        msg = "\n\n========== Streaming rules ==========\n"
        for rule in res.data:
            msg += str(rule) + "\n"
        msg += "========== Streaming rules end =======\n"
        logger.info(msg)

    stream.filter(
        tweet_fields=[
            "author_id",
            "entities",
            "public_metrics",
            "created_at",
            "lang",
        ]
    )
    # stream.sample()
