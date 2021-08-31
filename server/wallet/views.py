from ..services import TransactionService
from webargs.flaskparser import use_args
from ..services import AddressService
from ..models import Transaction
from .args import history_args
from flask import Blueprint
from .. import utils
from pony import orm

wallet = Blueprint("wallet", __name__, url_prefix="/wallet/")

@wallet.route("/history", methods=["POST"])
@use_args(history_args, location="json")
@orm.db_session
def info(args):
    transactions = None
    addresses = []
    result = []

    for raw_address in args["addresses"]:
        if (address := AddressService.get_by_address(raw_address)):
            addresses.append(address)

    transactions = orm.select(
        t for t in Transaction if (a for a in t.addresses if a in addresses)
    ).order_by(
        orm.desc(Transaction.created)
    )

    if args["before"] and (before := TransactionService.get_by_txid(args["before"])):
        transactions = transactions.filter(lambda t: t.created < before.created)

    transactions = transactions.limit(args["count"])

    for transaction in transactions:
        result.append(transaction.display())

    return utils.response(result)
