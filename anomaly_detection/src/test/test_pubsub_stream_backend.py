# -*- coding:utf-8 -*- #

import os
import unittest

from anomalydetection.stream.pubsub_stream_backend import PubSubStreamBackend


class TestPubSubStreamBackend(unittest.TestCase):

    def test(self):

        MESSAGE = "hello world!"

        pubsub = PubSubStreamBackend(
            "bluekiri-bigd-dev-anomdec",
            os.getenv("HOME") + "/Documents/bluekiri-bigd-dev-anomdec.json",
            "test", "test1")

        # Publish
        pubsub.push(MESSAGE)

        # Poll
        messages = pubsub.poll()
        if messages:
            for msg in messages:
                self.assertEqual(MESSAGE, msg)
        else:
            raise Exception("Cannot consume published message.")

