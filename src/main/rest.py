import json
from typing import Optional, Any

from flask import request, Response
from flask_classy import FlaskView, route

from src.main.parameters import ParameterManager



class ParameterController(FlaskView):
    parameterManager = ParameterManager()

    @route("/getFeeds")
    def getFeeds(self):
        data = self.parameterManager.getFeeds()
        return Response(json.dumps(data), mimetype="application/json")

    @route("/getParameter/<string:collection>/<string:name>")
    def getParameter(self, collection, name):
        params: dict = self.parameterManager.getParameter(name=name, collection=collection)
        if params is None:
            return Response(status=404)
        params.pop("_id")
        return Response(json.dumps(params), mimetype="application/json")

    def getFeeds(self):
        feeds = [feed.get('name') for feed in self.parameterManager.feed_params['leader'].find({})]
        res = Response(json.dumps(feeds), mimetype='application/json')
        return res

    @route("/reportParameter/<string:collection>/<string:name>")
    def reportParameter(self, collection, name):
        r = request.data
        return self.parameterManager.reportParam(collection, name, r)
