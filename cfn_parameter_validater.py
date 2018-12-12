import json
import yaml
import sys
import re
import logging
from logging import getLogger, StreamHandler, Formatter


def initLogger():
    logger = getLogger()
    logger.setLevel(logging.DEBUG)
    stream_handler = StreamHandler()
    handler_format = Formatter("%(levelname)s - %(message)s")
    stream_handler.setFormatter(handler_format)
    logger.addHandler(stream_handler)


class MyException(Exception):
    def __init__(self):
        self.message = "error occured"

    def __str__(self) -> str:
        return self.message


class InvalidExtensionException(MyException):
    pass


class FileLoader:
    def __init__(self):
        self._loaders = {}
        for func_name in dir(self):
            extension = re.match(r"_load_(.*)_file", func_name)
            if extension:
                self._loaders[extension.group(1)] = eval(f"self.{func_name}")

    def load(self, file_name):
        extension = file_name.split(".")[-1]
        if extension not in self._loaders.keys():
            raise InvalidExtensionException
        return self._loaders[extension](open(file_name, "r").read())

    def _load_yaml_file(self, yaml_text):
        # ToDo: 短縮記法対応
        return yaml.load(yaml_text)

    def _load_json_file(self, json_text):
        return json.loads(json_text)


class Cfn:
    def __init__(self, file_name):
        self._data = FileLoader().load(file_name)
        self.params = self._data["Parameters"]
        self.refs = self._extract_refs()

    def _extract_refs(self):
        ret = set([])
        self.__extract_refs(self._data, ret)
        return ret - set(self._data["Resources"].keys())

    def __extract_refs(self, data, ret):
        if type(data) is dict:
            ret |= set([v for k, v in data.items() if k == "Ref"])
            [self.__extract_refs(data[k], ret)
             for k, v in data.items() if not k == "Parameters"]
        if type(data) is list:
            [self.__extract_refs(_data, ret) for _data in data]


class Params:
    def __init__(self, file_name):
        self._data = FileLoader().load(file_name)
        self.params = [_data["ParameterKey"] for _data in self._data]


class CfnParamValidater:
    def __init__(self, cfn_file, params_file):
        self._logger = getLogger()
        self._cfn = Cfn(cfn_file)
        self._param = Params(params_file)

    def validate(self):
        self._cfn_internal_checker()
        self._cfn_params_outernal_checker()

    def _cfn_internal_checker(self):
        # Todo: minmaxとかpatternとかそのうち書くかも
        for ref in self._cfn.refs:
            if ref not in self._cfn.params.keys():
                self._logger.error(f"ref: {ref} is not defined at cfn file")

    def _cfn_params_outernal_checker(self):
        for internal_param in self._cfn.params:
            if internal_param not in self._param.params:
                self._logger.error(
                    f"param: {internal_param} is not defined at param file")


def main():
    CfnParamValidater(sys.argv[1], sys.argv[2]).validate()


if __name__ == "__main__":
    main()
