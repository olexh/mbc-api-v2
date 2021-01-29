from datetime import datetime
from decimal import Decimal
from pony import orm

db = orm.Database("sqlite", "../service.db", create_db=True)

class Block(db.Entity):
    _table_ = "chain_blocks"

    reward = orm.Required(Decimal, precision=20, scale=8)
    signature = orm.Optional(str, nullable=True)
    blockhash = orm.Required(str, index=True)
    height = orm.Required(int, index=True)
    created = orm.Required(datetime)
    difficulty = orm.Required(float)
    merkleroot = orm.Required(str)
    chainwork = orm.Required(str)
    version = orm.Required(int)
    weight = orm.Required(int)
    stake = orm.Required(bool)
    nonce = orm.Required(int)
    size = orm.Required(int)
    bits = orm.Required(str)

    previous_block = orm.Optional("Block")
    transactions = orm.Set("Transaction")
    next_block = orm.Optional("Block")

class Transaction(db.Entity):
    _table_ = "chain_transactions"

    amount = orm.Required(Decimal, precision=20, scale=8)
    txid = orm.Required(str, index=True)
    created = orm.Required(datetime)
    locktime = orm.Required(int)
    size = orm.Required(int)

    block = orm.Required("Block")
    outputs = orm.Set("Output")
    inputs = orm.Set("Input")

class Input(db.Entity):
    _table_ = "chain_inputs"

    sequence = orm.Required(int, size=64)
    n = orm.Required(int)

    transaction = orm.Required("Transaction")
    vout = orm.Required("Output")

class Output(db.Entity):
    _table_ = "chain_outputs"

    amount = orm.Required(Decimal, precision=20, scale=8)
    currency = orm.Required(str, default="AOK")
    timelock = orm.Required(int, default=0)
    address = orm.Required(str, index=True)
    category = orm.Optional(str)
    raw = orm.Optional(str)
    n = orm.Required(int)

    transaction = orm.Required("Transaction")
    vin = orm.Optional("Input")

    orm.composite_index(transaction, n)


db.generate_mapping(create_tables=True)
