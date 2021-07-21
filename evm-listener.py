import os
import json
from flask import Flask
from web3 import Web3, HTTPProvider
from flask_sqlalchemy import SQLAlchemy
from werkzeug.exceptions import HTTPException


class Config(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = "postgresql://" + os.getenv("USER") + ":" + os.getenv("PASSWORD") + "@" + os.getenv("SERVER") + ":5432/" + os.getenv("DB")


app = Flask(__name__)
app.config.from_object(Config())
db = SQLAlchemy(app)

# VRF provider contract
provider_contract_address = "0xD1785fd50c2DBF77bF5F376ECc960BB0E9c19f14"

provider_abi_file = open("./Provider.json")
provider_abi = json.load(provider_abi_file)
db.create_all()

class UnableToConnect(HTTPException):
    code = 500
    description = "Unable to connect"

def handle_500(e):
    return "Unable to connect, ", 500
app.register_error_handler(UnableToConnect, handle_500)

class Vrf(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    caller = db.Column(db.String, nullable=False)
    seed = db.Column(db.String, nullable=True)
    task_key = db.Column(db.String, nullable=True)
    bounty = db.Column(db.String, nullable=True)
    time = db.Column(db.Integer, nullable=True)
    block_no = db.Column(db.Integer, nullable=False)


def request_data(w3):

    provider_contract = w3.eth.contract(
        address=provider_contract_address, abi=provider_abi)

    from_block = db.session.query(Vrf).order_by(Vrf.id.desc()).first()

    myfilter = provider_contract.events.RandomDataRequested.createFilter(
        fromBlock=from_block.block_no, toBlock="latest")

    event_list = myfilter.get_all_entries()
   
    for event in event_list:
        print('block number ', event.blockNumber)
        request_info = event.args
        # Insert data
        request = Vrf(caller=request_info.caller, seed=request_info.seed, task_key=request_info.taskKey,
                        bounty=request_info.bounty, time=request_info.time, block_no=event.blockNumber)
        db.session.add(request)

    db.session.commit()

@app.route("/")
def main():
    w3 = Web3(HTTPProvider(os.getenv("RPC_ENDPOINT")))

    if w3.isConnected():
        request_data(w3)
    else:
        raise UnableToConnect()
    return ""