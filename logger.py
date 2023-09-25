import json
from datetime import datetime

class Logger:
    def __init__(self):
        self.logs = []
        self.builtin = (
            str,
            int,
            float,
            list,
            dict
        )

    def __get_date__(self):
        return (datetime.now().strftime("%H:%M:%S"))

    def __get_attributes__(self, data):
        attributes = {}

        if (isinstance(data, self.builtin) == False):
            attributes = json.dumps(data, default=lambda o: o.__dict__, sort_keys=True, indent=4)
        else:
            attributes = data

        return (attributes)

    def log(self, message):
        attributes = self.__get_attributes__(message)
        record = "[{}] {}".format(
            self.__get_date__(),
            attributes
        )

        self.logs.append(record)
        print(record)

    def request(self, _request):
        record = "[{}] ({}) {}".format(
            self.__get_date__(),
            _request.status_code,
            _request.url
        )

        self.logs.append(record)
        print(record)

    def dump(self, path: str):
        with open(path, "w+") as f:
            f.writelines(self.logs)