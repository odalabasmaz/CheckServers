#
# @author Orhun Dalabasmaz
#

import json

from Utils import current_time_millis


class Message:
    def __init__(self, time=current_time_millis()):
        self.tags = dict()
        self.fields = dict()
        self.timestamp = time

    def tag(self, key, value):
        if type(value) is not str or value:
            self.tags[key] = str(value)

    def field(self, key, value):
        if type(value) is not str or value:
            self.fields[key] = float(value)

    def string_field(self, key, value):
        if type(value) is str and value:
            self.fields[key] = value

    def time(self, value):
        if value:
            self.timestamp = value

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)

    def toJsonIndented(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=2)
