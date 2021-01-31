from ..services import TransactionService
from webargs.flaskparser import use_args
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
    transactions = TransactionService.transactions(args["page"], token)
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

@db.route("/blocks", methods=["GET"])
@orm.db_session
def blocks():
    blocks = BlockService.blocks()
    result = []

    for block in blocks:
        result.append({
            "height": block.height,
            "blockhash": block.blockhash,
            "timestamp": block.created.timestamp(),
            "tx": len(block.transactions)
        })

    return utils.response(result)

@db.route("/block/<string:bhash>", methods=["GET"])
@orm.db_session
def block(bhash):
    block = BlockService.get_by_hash(bhash)

    if block:
        return utils.response({
            "reward": float(block.reward),
            "signature": block.signature,
            "blockhash": block.blockhash,
            "height": block.height,
            "tx": len(block.transactions),
            "timestamp": block.created.timestamp(),
            "difficulty": block.difficulty,
            "merkleroot": block.merkleroot,
            "chainwork": block.chainwork,
            "version": block.version,
            "weight": block.weight,
            "stake": block.stake,
            "nonce": block.nonce,
            "size": block.size,
            "bits": block.bits
        })

    else:
        return utils.dead_response("Block not found"), 404

@db.route("/block/<string:bhash>/transactions", methods=["GET"])
@use_args(page_args, location="query")
@orm.db_session
def block_transactions(args, bhash):
    block = BlockService.get_by_hash(bhash)

    if block:
        transactions = block.transactions.page(args["page"])
        result = []

        for transaction in transactions:
            output_amount = 0
            input_amount = 0
            outputs = []
            inputs = []
            fee = 0

            for vin in transaction.inputs:
                inputs.append({
                    "address": vin.vout.address,
                    "currency": vin.vout.currency,
                    "amount": float(vin.vout.amount)
                })

                if vin.vout.currency == "AOK":
                    input_amount += vin.vout.amount

            for vout in transaction.outputs:
                outputs.append({
                    "address": vout.address,
                    "currency": vout.currency,
                    "amount": float(vout.amount)
                })

                if vout.currency == "AOK":
                    output_amount += vout.amount

            result.append({
                "fee": float(input_amount - output_amount),
                "timestamp": transaction.created.timestamp(),
                "amount": float(transaction.amount),
                "coinstake": transaction.coinstake,
                "coinbase": transaction.coinbase,
                "txid": transaction.txid,
                "size": transaction.size,
                "outputs": outputs,
                "inputs": inputs
            })

        return utils.response(result)

    else:
        return utils.dead_response("Block not found"), 404

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
