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

app = init_app(Feed)
ParameterController.register(app)
MappingManager.register(app)
Service.register(app)
SamplePages.register(app)
ActionsManager.register(app)
RunningManager.register(app)
CORS(app)

