import json
import logging

from flask import request, Response
from flask_classy import FlaskView, route
import pymongo
from feed.settings import mongo_params


class MappingManager(FlaskView):
    mongoClient = pymongo.MongoClient(**mongo_params)
    mappings = mongoClient['mapping']

    @route("/getMapping/<string:name>/v/<int:version>")
    def getMapping(self, name, version):
        mapping = self.mappings['values'].find_one({'name': name})
        if mapping is None:
            logging.warning(f'mapping for {name} was not found')
            return Response('No mapping found', status=404, mimetype='application/text')
        mapping.pop('_id', None)
        return Response(json.dumps(mapping), mimetype='application/json')
