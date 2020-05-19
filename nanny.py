import json
import logging
from logging import logging
from logging import dictConfig
import os
from queue import Queue
from feed.settings import database_parameters, nanny_params, mongo_params
from flask import Flask
from feed.service import Service
from feed.chainsessions import init_app
from src.main.mapping import MappingManager
from src.main.samplepages import SamplePages
from src.main.runningmanager import RunningManager
from src.main.rest import ParameterController
from src.main.actionsmanager import ActionsManager
from flask_cors import CORS
from src.main.domain import Feed
from pymongo import MongoClient
from datetime import timedelta

logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))
logging.getLogger("urllib3").setLevel("INFO")

app = init_app(Feed)

logging.info("####### Environment #######")


logging.info("nanny: {}".format(json.dumps(nanny_params, indent=4, sort_keys=True)))



ParameterController.register(app)
MappingManager.register(app)
Service.register(app)
ActionsManager.register(app)
SamplePages.register(app)
RunningManager.register(app)
CORS(app)

if __name__ == '__main__':
    dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s]%(thread)d: %(module)s - %(levelname)s - %(message)s',
        }},
        'handlers': {'wsgi': {
            'class': 'logging.FileHandler',
            'filename': f'{os.getenv("DEPLOYMENT_ROOT")}/tmp/ci.log',
            'formatter': 'default'
        }},
        'root': {
            'level': 'INFO',
            'handlers': ['wsgi']
        }
    })

    logging.info("\n".join([f'{key}={os.environ[key]}' for key in os.environ]))
    print(app.url_map)
    app.run(port=os.getenv("FLASK_PORT", os.getenv("NANNY_PORT", 5003)), host=os.getenv('NANNY_HOST'))
