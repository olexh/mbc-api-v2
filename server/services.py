from .models import Transaction
from .models import Address
from .models import Balance
from .models import Output
from .models import Input
from .models import Block
from .models import Token
from pony import orm

class BlockService(object):
    @classmethod
    def latest_block(cls):
        return Block.select().order_by(
            orm.desc(Block.height)
        ).first()

    @classmethod
    def create(cls, blockhash, height, created,
               difficulty, merkleroot, chainwork, version,
               weight, nonce, size, bits,
               signature=None):
        return Block(
            blockhash=blockhash, height=height, created=created,
            difficulty=difficulty, merkleroot=merkleroot, chainwork=chainwork, version=version,
            weight=weight, nonce=nonce, size=size, bits=bits,
            signature=signature
        )

    @classmethod
    def get_by_height(cls, height):
        return Block.get(height=height)

    @classmethod
    def get_by_hash(cls, bhash):
        return Block.get(blockhash=bhash)

    @classmethod
    def blocks(cls):
        return Block.select().order_by(
            orm.desc(Block.height)
        )

    @classmethod
    def chart(cls):
        query = orm.select((b.height, len(b.transactions)) for b in Block)
        query = query.order_by(-1)
        return query[:1440]

class TransactionService(object):
    @classmethod
    def get_by_txid(cls, txid):
        return Transaction.get(txid=txid)

    @classmethod
    def create(cls, amount, txid, created, size, block,
               coinbase=False):
        return Transaction(
            amount=amount, txid=txid, created=created,
            size=size, coinbase=coinbase,
            block=block
        )

    @classmethod
    def transactions(cls, page=1, pagesize=10, currency="MBC"):
        query = orm.select((o.transaction, sum(o.amount), o.transaction.id) for o in Output if o.currency == currency).distinct()
        query = query.order_by(-3)
        return query

    @classmethod
    def total_transactions(cls, currency="MBC"):
        query = orm.select((orm.count(o.transaction)) for o in Output if o.currency == currency).distinct()
        return query.first()

class InputService(object):
    @classmethod
    def create(cls, sequence, n, transaction, vout):
        return Input(
            sequence=sequence, transaction=transaction,
            vout=vout, n=n,
        )

class AddressService(object):
    @classmethod
    def get_by_address(cls, address):
        return Address.get(address=address)

    @classmethod
    def create(cls, address):
        return Address(address=address)

class BalanceService(object):
    @classmethod
    def get_by_currency(cls, address, currency):
        return Balance.get(
            address=address, currency=currency
        )

    @classmethod
    def create(cls, address, currency):
        return Balance(
            address=address, currency=currency
        )

class OutputService(object):
    @classmethod
    def get_by_prev(cls, transaction, n):
        return Output.get(transaction=transaction, n=n)

    @classmethod
    def create(cls, transaction, amount, category, address, raw, n,
               currency="MBC"):
        return Output(
            transaction=transaction, amount=amount, category=category,
            address=address, raw=raw, n=n, currency=currency,
        )

class TokenService(object):
    @classmethod
    def get_units(cls, currency):
        token = Token.get(name=currency)

        if not token or currency == "MBC":
            return 8

        return token.units

    @classmethod
    def get_ipfs(cls, currency):
        token = Token.get(name=currency)

        if not token or currency == "MBC":
            return None

        return token.ipfs
