#
# @author Orhun Dalabasmaz
#

import json

from Utils import current_time_millis


class Message:
    def __init__(self):
        self.tags = dict()
        self.fields = dict()
        self.timestamp = current_time_millis()

    def tag(self, key, value):
        self.tags[key] = value

    def field(self, key, value):
        self.fields[key] = value

    def time(self, value):
        self.timestamp = value

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)

    def toJsonIndented(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=2)
