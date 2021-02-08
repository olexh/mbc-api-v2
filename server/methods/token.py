from .. import utils

class Token():
    @classmethod
    def data(cls, name: str):
        return utils.make_request("gettokendata", [name])

    @classmethod
    def list(cls, offset: int, count: int, search=""):
        if count > 200:
            count = 200

        return utils.make_request("listtokens", [f"{search}*", True, count, offset])
