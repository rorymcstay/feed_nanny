import json
import logging

from flask import request, Response, session
from flask_classy import FlaskView, route
import pymongo
from feed.settings import mongo_params
import os


class Mapping:

    def __init__(self, **kwargs):
        pass


class MappingManager(FlaskView):
    mongoClient = pymongo.MongoClient(**mongo_params)
    mappings = mongoClient[os.getenv('CHAIN_DB', 'actionChains')]['mappings']

    @route("/getMapping/<string:name>/v/<int:version>")
    def getMapping(self, name, version):
        mapping = self.mappings.find_one({'name': name, 'userID': session.userID})
        if mapping is None:
            logging.warning(f'mapping for {name} was not found')
            return Response('No mapping found', status=404, mimetype='application/text')
        mapping.pop('_id', None)
        return Response(json.dumps(mapping), mimetype='application/json', status=200)

    def setNeedsMapping(self, name):
        if session.name is None:
            return Response(f'{name} not found', status=200)
        session.setNeedsMapping()
        return Response('ok')

    def getMappingNames(self, name):
        out = []
        for i in self.mappings.find({}, projection=['name']):
            out.append({'name': i.get('name'), 'userID': i.get('userID')})
        return Response(json.dumps(out), mimetype='application/json')

    def _hasMapping(self, feedName):
        mapping = self.mappings.find_one({'name': name})

