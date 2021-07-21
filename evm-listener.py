import os
import json
from flask import Flask
from web3 import Web3, HTTPProvider
from flask_sqlalchemy import SQLAlchemy


class Config(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = "postgresql://bkioshn:@localhost:5432/postgres"


app = Flask(__name__)
app.config.from_object(Config())
db = SQLAlchemy(app)


class Vrf(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    caller = db.Column(db.String, nullable=False)
    seed = db.Column(db.String, nullable=True)
    task_key = db.Column(db.String, nullable=True)
    bounty = db.Column(db.String, nullable=True)
    time = db.Column(db.Integer, nullable=True)
    block_no = db.Column(db.Integer, nullable=False)


def request_data(w3):
    # VRF provider contract
    provider_contract_id = "0xD1785fd50c2DBF77bF5F376ECc960BB0E9c19f14"

    provider_abi_file = open("./Provider.json")
    provider_abi = json.load(provider_abi_file)

    provider_contract = w3.eth.contract(
        address=provider_contract_id, abi=provider_abi)

    from_block = db.session.query(Vrf).order_by(Vrf.id.desc()).first()

    myfilter = provider_contract.events.RandomDataRequested.createFilter(
        fromBlock=from_block.block_no, toBlock="latest")

    event_list = myfilter.get_all_entries()
    if (len(event_list) > 0):
        print("check len'")
        if not (db.engine.has_table("vrf")):
            db.create_all()
        for event in event_list:
            FROM_BLOCK = event.blockNumber

            print('block number ', event.blockNumber)
            request_info = event.args
            # Insert data
            try:
                request = Vrf(caller=request_info.caller, seed=request_info.seed, task_key=request_info.taskKey,
                              bounty=request_info.bounty, time=request_info.time, block_no=event.blockNumber)
                db.session.add(request)
                db.session.commit()
            except:
                print("Cant insert")

@app.route("/")
def main():
    w3 = Web3(HTTPProvider(
        "https://kovan.infura.io/v3/" + os.getenv("PROJECTID")))

    if w3.isConnected():
        request_data(w3)
    return ''
