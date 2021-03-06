# -*- coding:utf-8 -*- #
#
# Anomaly Detection Framework
# Copyright (C) 2018 Bluekiri BigData Team <bigdata@bluekiri.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import os
import unittest
from datetime import datetime

from unittest.mock import patch
from rx import Observable

from anomalydetection.backend.entities.input_message import InputMessage
from anomalydetection.backend.stream.agg.functions import AggregationFunction
from anomalydetection.backend.stream.kafka import KafkaStreamConsumer
from anomalydetection.backend.stream.kafka import SparkKafkaStreamConsumer
from anomalydetection.backend.stream.kafka import KafkaStreamProducer
from anomalydetection.common.concurrency import Concurrency
from anomalydetection.common.logging import LoggingMixin


class TestKafkaStreamBackend(unittest.TestCase, LoggingMixin):

    MESSAGE = """{"test": "test"}"""

    def __init__(self, methodName='runTest'):
        super().__init__(methodName)
        self.kafka_broker = os.environ.get("KAFKA_BROKER", "localhost:9092")

    def test_kafka_stream_backend(self):

        is_passed = False

        topic = "test1"
        group_id = "test1"

        kafka_consumer = KafkaStreamConsumer(self.kafka_broker, topic, group_id)
        kafka_producer = KafkaStreamProducer(self.kafka_broker, topic)

        def push(_):
            kafka_producer.push(self.MESSAGE)

        def completed():
            kafka_consumer.unsubscribe()
            self.assertEqual(is_passed, True)

        Observable.interval(1000) \
            .take(20) \
            .map(push) \
            .subscribe(on_completed=completed)

        # Poll
        messages = kafka_consumer.poll()
        if messages:
            for message in messages:
                self.assertEqual(message, self.MESSAGE)
                kafka_consumer.unsubscribe()
                is_passed = True
                break
            self.assertEqual(is_passed, True)
        else:
            raise Exception("Cannot consume published message.")

    @patch("anomalydetection.backend.stream.kafka.SparkKafkaStreamConsumer.unsubscribe")
    @patch("anomalydetection.common.concurrency.Concurrency.run_process")
    def test_kafka_stream_backend_spark(self, run_process, unsubscribe):

        is_passed = False

        unsubscribe.return_value = None
        run_process.side_effect = Concurrency.run_thread

        topic = "test2"
        group_id = "test2"

        kafka_producer = KafkaStreamProducer(self.kafka_broker, topic)

        agg_consumer = SparkKafkaStreamConsumer(
            self.kafka_broker,
            topic,
            group_id,
            AggregationFunction.AVG,
            10 * 1000,
            spark_opts={"timeout": 30},
            multiprocessing=False)

        def push(_):
            kafka_producer.push(InputMessage("app", 1.5, datetime.now()).to_json())

        def completed():
            agg_consumer.unsubscribe()

        Observable.interval(1000) \
            .take(30) \
            .map(push) \
            .subscribe(on_completed=completed)

        messages = agg_consumer.poll()
        if messages:
            for message in messages:
                self.logger.info(message)
                is_passed = True
                break

        else:
            raise Exception("Cannot consume published message.")

        Concurrency.get_thread(agg_consumer.pid).join(30.0)
        self.assertEqual(is_passed, True)
