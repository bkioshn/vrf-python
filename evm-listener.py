import os
from web3 import Web3, HTTPProvider
import psycopg2
import json
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, inspect
import time

# Starting block of the smart contract
FROM_BLOCK = 25040009

class Config(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://bkioshn:@localhost:5432/postgres"

app = Flask(__name__)
app.config.from_object(Config())
db = SQLAlchemy(app)


class Vrf(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    caller = db.Column(db.String, nullable=False)
    seed = db.Column(db.String, nullable=False)
    task_key = db.Column(db.String, nullable=False)
    bounty = db.Column(db.String, nullable=False)
    time = db.Column(db.Integer, nullable=False)


def request_data(w3, cursor):
    global FROM_BLOCK
    # VRF provider contract
    provider_contract_id = "0xD1785fd50c2DBF77bF5F376ECc960BB0E9c19f14"

    provider_abi_file = open("./Provider.json")
    provider_abi = json.load(provider_abi_file)

    provider_contract = w3.eth.contract(
        address=provider_contract_id, abi=provider_abi)

    while (True):
        print("timer start")
        print(FROM_BLOCK)
        time.sleep(60)
        myfilter = provider_contract.events.RandomDataRequested.createFilter(
            fromBlock=FROM_BLOCK, toBlock="latest")

        event_list = myfilter.get_all_entries()
        if (len(event_list) > 0):
            print("check len'")
            insert_to_db(event_list, cursor)

def insert_to_db(event_list, cursor):
    global FROM_BLOCK

    if not (db.engine.has_table("vrf")):
        db.create_all()
    for event in event_list:
        FROM_BLOCK = event.blockNumber

        print('block number ', event.blockNumber)
        request_info = event.args
        # Insert data
        try:
            request = Vrf(caller=request_info.caller, seed=request_info.seed, task_key=request_info.taskKey, bounty=request_info.bounty, time=request_info.time)
            db.session.add(request)
            db.session.commit()
        except:
            print("Cant insert")

        # cursor.execute("""SELECT * FROM vrf where time = 12345678""")
        # rows = cursor.fetchall()
        # print(rows)
    
    

def main():
    w3 = Web3(HTTPProvider(
        "https://kovan.infura.io/v3/" + os.getenv("PROJECTID")))

    connection = psycopg2.connect(user="postgres",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="postgres")
    if w3.isConnected() and connection.status:
        cursor = connection.cursor()
        request_data(w3, cursor)


if __name__ == '__main__':
    main()

