from .methods.transaction import Transaction
from .services import TransactionService
from .methods.general import General
from .services import OutputService
from .services import InputService
from .services import BlockService
from .methods.block import Block
from datetime import datetime
from pony import orm
from . import utils

def log_block(message, block):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    time = block.created.strftime("%Y-%m-%d %H:%M:%S")
    print(f"{now} {message}: hash={block.blockhash} height={block.height} tx={len(block.transactions)} date='{time}'")

def log_message(message):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{now} {message}")

@orm.db_session
def sync_blocks():
    if not BlockService.latest_block():
        data = Block.height(0)["result"]
        created = datetime.fromtimestamp(data["time"])
        signature = data["signature"] if "signature" in data else None

        block = BlockService.create(
            utils.amount(data["reward"]), data["hash"], data["height"], created,
            data["difficulty"], data["merkleroot"], data["chainwork"],
            data["version"], data["weight"], data["stake"], data["nonce"],
            data["size"], data["bits"], signature
        )

        log_block("Genesis block", block)

        orm.commit()

    current_height = General.current_height()
    latest_block = BlockService.latest_block()

    # log_message(f"Current node height: {current_height}, db height: {latest_block.height}")

    while latest_block.blockhash != Block.blockhash(latest_block.height):
        log_block("Found reorg", latest_block)

        reorg_block = latest_block
        latest_block = reorg_block.previous_block

        reorg_block.delete()
        orm.commit()

    for height in range(latest_block.height + 1, current_height + 1):
        block_data = Block.height(height)["result"]
        created = datetime.fromtimestamp(block_data["time"])
        signature = block_data["signature"] if "signature" in block_data else None

        block = BlockService.create(
            utils.amount(block_data["reward"]), block_data["hash"], block_data["height"], created,
            block_data["difficulty"], block_data["merkleroot"], block_data["chainwork"],
            block_data["version"], block_data["weight"], block_data["stake"], block_data["nonce"],
            block_data["size"], block_data["bits"], signature
        )

        log_block("New block", block)

        for index, txid in enumerate(block_data["tx"]):
            if block.stake and index == 0:
                continue

            tx_data = Transaction.info(txid, False)["result"]
            created = datetime.fromtimestamp(tx_data["time"])
            coinbase = block.stake is False and index == 0
            coinstake = block.stake and index == 1

            transaction = TransactionService.create(
                utils.amount(tx_data["amount"]), tx_data["txid"],
                created, tx_data["locktime"], tx_data["size"], block,
                coinbase, coinstake
            )

            for vin in tx_data["vin"]:
                if "coinbase" in vin:
                    continue

                prev_tx = TransactionService.get_by_txid(vin["txid"])
                prev_out = OutputService.get_by_prev(prev_tx, vin["vout"])

                InputService.create(
                    vin["sequence"], vin["vout"], transaction, prev_out
                )

            for vout in tx_data["vout"]:
                if vout["scriptPubKey"]["type"] in ["nonstandard", "nulldata"]:
                    continue

                amount = utils.amount(vout["valueSat"])
                currency = "AOK"
                timelock = 0

                if "token" in vout["scriptPubKey"]:
                    timelock = vout["scriptPubKey"]["token"]["token_lock_time"]
                    currency = vout["scriptPubKey"]["token"]["name"]
                    amount = vout["scriptPubKey"]["token"]["amount"]

                if "timelock" in vout["scriptPubKey"]:
                    timelock = vout["scriptPubKey"]["timelock"]

                OutputService.create(
                    transaction, amount, vout["scriptPubKey"]["type"],
                    vout["scriptPubKey"]["addresses"][0],
                    vout["scriptPubKey"]["hex"],
                    vout["n"], currency,
                    timelock
                )

        orm.commit()


sync_blocks()
