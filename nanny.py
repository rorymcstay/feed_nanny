import json
import logging
import os

from feed.settings import database_parameters, nanny_params
from flask import Flask
from feed.service import Service
from src.main.mapping import MappingManager
from src.main.rest import ContainerController, ParameterController
from flask_cors import CORS

logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))
logging.getLogger("urllib3").setLevel("INFO")

app = Flask(__name__)

logging.info("####### Environment #######")


logging.info("database: {}".format(json.dumps(database_parameters, indent=4, sort_keys=True)))
logging.info("nanny: {}".format(json.dumps(nanny_params, indent=4, sort_keys=True)))


ContainerController.register(app)
ParameterController.register(app)
MappingManager.register(app)
Service.register(app)
CORS(app)

if __name__ == '__main__':
    print(app.url_map)
    app.run(port=os.getenv("FLASK_PORT", 5003), host="0.0.0.0")
