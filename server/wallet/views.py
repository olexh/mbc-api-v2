from ..methods.transaction import Transaction as NodeTransaction
from ..models import Transaction, Block, Token
from .args import history_args, broadcast_args
from ..services import TransactionService
from webargs.flaskparser import use_args
from ..services import AddressService
from ..services import OutputService
from ..services import BlockService
from flask import Blueprint
from .. import utils
from pony import orm
import math

wallet = Blueprint("wallet", __name__, url_prefix="/wallet/")

def satoshis(value, decimal=8):
    return int(float(value) * math.pow(10, decimal))

def get_units(name):
    token = Token.get(name=name)

    if not token or name == "AOK":
        return 8

    return token.units

def display_tx(transaction):
    latest_blocks = Block.select().order_by(
        orm.desc(Block.height)
    ).first()

    output_amount = 0
    input_amount = 0
    outputs = []
    inputs = []

    for vin in transaction.inputs:
        units = get_units(vin.vout.currency)

        inputs.append({
            "address": vin.vout.address.address,
            "currency": vin.vout.currency,
            "amount": satoshis(vin.vout.amount, units),
            "units": units
        })

        if vin.vout.currency == "AOK":
            input_amount += satoshis(vin.vout.amount)

    for vout in transaction.outputs:
        units = get_units(vout.currency)

        outputs.append({
            "address": vout.address.address,
            "currency": vout.currency,
            "timelock": vout.timelock,
            "category": vout.category,
            "amount": satoshis(vout.amount, units),
            "units": units,
        })

        if vout.currency == "AOK":
            output_amount += satoshis(vout.amount)

    return {
        "confirmations": latest_blocks.height - transaction.block.height + 1,
        "fee": input_amount - output_amount,
        "timestamp": int(transaction.created.timestamp()),
        "amount": satoshis(transaction.amount),
        "coinstake": transaction.coinstake,
        "height": transaction.block.height,
        "coinbase": transaction.coinbase,
        "txid": transaction.txid,
        "size": transaction.size,
        "outputs": outputs,
        "mempool": False,
        "inputs": inputs
    }


@wallet.route("/balance/<string:address>", methods=["GET"])
@orm.db_session
def test(address):
    address = AddressService.get_by_address(address)
    block = BlockService.latest_block()
    result = []

    if address:
        for balance in address.balances:
            locked_time = OutputService.locked_time(address, block.created.timestamp(), balance.currency)
            locked_height = OutputService.locked_height(address, block.height, balance.currency)

            locked = locked_time + locked_height
            unspent = balance.balance - locked
            units = get_units(balance.currency)

            result.append({
                "currency": balance.currency,
                "balance": satoshis(unspent, units),
                "locked": satoshis(locked, units),
                "units": units
            })

    return utils.response(result)

@wallet.route("/history", methods=["POST"])
@use_args(history_args, location="json")
@orm.db_session
def info(args):
    transactions = None
    addresses = []
    result = []

    for raw_address in args["addresses"]:
        address = AddressService.get_by_address(raw_address)
        if address:
            addresses.append(address)

    transactions = orm.left_join(
        transaction
        for transaction in Transaction for address in transaction.addresses
        if address in addresses
    ).order_by(
        orm.desc(Transaction.created)
    )

    if args["after"]:
        after = TransactionService.get_by_txid(args["after"])
        if after:
            transactions = transactions.filter(lambda t: t.created > after.created)

    if args["before"]:
        before = TransactionService.get_by_txid(args["before"])
        if before:
            transactions = transactions.filter(lambda t: t.created < before.created)

    transactions = transactions.limit(args["count"])

    for transaction in transactions:
        result.append(display_tx(transaction))

    return utils.response(result)

@wallet.route("/broadcast", methods=["POST"])
@use_args(broadcast_args, location="json")
def broadcast(args):
    return NodeTransaction.broadcast(args["raw"])
