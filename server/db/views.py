from webargs.flaskparser import use_args
from ..services import OutputService
from ..services import BlockService
from .args import page_args
from flask import Blueprint
from .. import utils
from pony import orm

db = Blueprint("db", __name__, url_prefix="/v2/")

@db.route("/latest", methods=["GET"])
@orm.db_session
def info():
    block = BlockService.latest_block()

    return utils.response({
        "time": block.created.timestamp(),
        "blockhash": block.blockhash,
        "height": block.height,
        "chainwork": block.chainwork,
        "difficulty": block.difficulty,
        "reward": float(block.reward)
    })

@db.route("/transactions", defaults={"token": "AOK"}, methods=["GET"])
@db.route("/transactions/<string:token>", methods=["GET"])
@use_args(page_args, location="query")
@orm.db_session
def transactions(args, token):
    transactions = OutputService.token_transactions(args["page"], token)
    result = []

    for entry in transactions:
        transaction = entry[0]
        amount = entry[1]

        result.append({
            "height": transaction.block.height,
            "blockhash": transaction.block.blockhash,
            "timestamp": transaction.block.created.timestamp(),
            "txhash": transaction.txid,
            "amount": float(amount)
        })

    return utils.response(result)

@db.route("/chart", methods=["GET"])
@orm.db_session
def chart():
    data = BlockService.chart()
    result = {}

    for entry in data:
        height = entry[0]
        count = entry[1]

        result[height] = count

    return utils.response(result)
