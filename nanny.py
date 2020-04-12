import json
import logging
import os

from feed.settings import database_parameters, nanny_params, mongo_params
from flask import Flask
from feed.service import Service
from src.main.mapping import MappingManager
from src.main.rest import ContainerController, ParameterController
from flask_cors import CORS

from pymongo import MongoClient

logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))
logging.getLogger("urllib3").setLevel("INFO")

app = Flask(__name__)

logging.info("####### Environment #######")


logging.info("database: {}".format(json.dumps(database_parameters, indent=4, sort_keys=True)))
logging.info("nanny: {}".format(json.dumps(nanny_params, indent=4, sort_keys=True)))

#probing mongo
client = MongoClient(**mongo_params)

def probeMongo():
    try:
        cl = client.server_info()
    except ServerSelectionTimeoutError as ex:
        logging.info(f'trying to connect to mongo with {mongo_params}')
        return False
    return True

while not probeMongo():
    sleep(10)


ParameterController.register(app)
MappingManager.register(app)
Service.register(app)
CORS(app)

if __name__ == '__main__':
    print(app.url_map)
    app.run(port=os.getenv("FLASK_PORT", 5003), host="0.0.0.0")
