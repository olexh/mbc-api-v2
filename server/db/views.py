from ..services import TransactionService
from webargs.flaskparser import use_args
from ..services import AddressService
from ..services import BlockService
from ..models import Transaction
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
@use_args(page_args, location="query")
@orm.db_session
def blocks(args):
    blocks = BlockService.blocks(args["page"])
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
            result.append(transaction.display())

        return utils.response(result)

    return utils.dead_response("Block not found"), 404

@db.route("/transaction/<string:txid>", methods=["GET"])
@orm.db_session
def transaction(txid):
    transaction = TransactionService.get_by_txid(txid)

    if transaction:
        return utils.response(transaction.display())

    return utils.dead_response("Transaction not found"), 404

@db.route("/history/<string:address>", methods=["GET"])
@use_args(page_args, location="query")
@orm.db_session
def history(args, address):
    address = AddressService.get_by_address(address)
    result = []

    if address:
        transactions = address.transactions.order_by(
            orm.desc(Transaction.id)
        ).page(args["page"], pagesize=100)

        for transaction in transactions:
            result.append(transaction.display())

    return utils.response(result)

@db.route("/richlist", defaults={"token": "AOK"}, methods=["GET"])
@db.route("/richlist/<string:token>", methods=["GET"])
@use_args(page_args, location="query")
@orm.db_session
def richlist(args, token):
    addresses = AddressService.richlist(args["page"], token)
    result = []

    for entry in addresses:
        result.append({
            "address": entry[0].address,
            "balance": float(entry[1])
        })

    return utils.response(result)

@db.route("/chart", methods=["GET"])
@orm.db_session
def chart():
    data = BlockService.chart()
    result = {}

    for entry in data:
        result[entry[0]] = entry[1]

    return utils.response(result)
