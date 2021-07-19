import os
from web3 import Web3, HTTPProvider
import psycopg2
import json

w3 = Web3(HTTPProvider(
    "https://kovan.infura.io/v3/" + os.getenv("PROJECTID")))


if w3.isConnected():
    # VRF provider contract
    provider_contract_id = "0xD1785fd50c2DBF77bF5F376ECc960BB0E9c19f14"

    provider_abi_file = open("./Provider.json")
    provider_abi = json.load(provider_abi_file)

    provider_contract = w3.eth.contract(
        address=provider_contract_id, abi=provider_abi)

    # FIXME Should listen to the latest block
    # Now is just trying to get some data
    myfilter = provider_contract.events.RandomDataRequested.createFilter(
        fromBlock=25040009, toBlock=25040009)

    event_list = myfilter.get_all_entries()
    request_info = event_list[0].args

    # Sending to database
    try:
        connection = psycopg2.connect(user="postgres",
                                      host="127.0.0.1",
                                      port="5432",
                                      database="postgres")

        cursor = connection.cursor()

        # Insert data
        try:
            cursor.execute("""INSERT INTO vrf (Caller, Seed, TaskKey, Bounty, Time) VALUES (%s, %s, %s, %s, %s);""", (
                request_info.caller, request_info.seed, request_info.taskKey, request_info.bounty, request_info.time))
        except:
            print("Cant insert")

        # Test whether data is added or not
        cursor.execute("""SELECT * FROM vrf where time = 12345678""")
        rows = cursor.fetchall()
        print(rows)
    except:
        print("Not response")
