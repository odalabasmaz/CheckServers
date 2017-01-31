#
# @author Orhun Dalabasmaz
#

import json

from kafka import KafkaProducer

from config.KafkaConfig import kafka_topic, kafka_bootstrap_servers


class SimpleKafkaProducer:
    def __init__(self):
        self.producer = KafkaProducer(bootstrap_servers=kafka_bootstrap_servers,
                                      key_serializer=lambda v: json.dumps(v, default=lambda o: o.__dict__, sort_keys=True).encode('utf-8'),
                                      value_serializer=lambda v: json.dumps(v, default=lambda o: o.__dict__, sort_keys=True).encode('utf-8'))

    def sendMessage(self, key, msg):
        print "# sending msg: ", key, msg.toJson()
        self.producer.send(kafka_topic, key=key, value=msg)
        self.producer.flush()
        print "# message sent."
