from flask_classy import FlaskView
from flask import g
import os
from flask import request, session
from flask_classy import route
import json
from feed.settings import nanny_params, routing_params
import requests as r
from datetime import datetime
from json.decoder import JSONDecodeError
from flask import Response
import time
from queue import Queue, Empty
from feed.logger import getLogger
from src.main.domain import Feed

logging = getLogger(__name__)


class RunningManager(FlaskView):

    @staticmethod
    def _get_toRun():
        return g.toRun

    def getNextFeed(self):
        try:
            nextItem = RunningManager._get_toRun().get(block=True, timeout=60)
        except Empty as e:
            logging.info(f'timed out waiting for next feed to run.')
            return Response(json.dumps({'name': None}), status=200)
        logging.info(f'feed order of next to run: {nextItem}')
        if nextItem.needs_mapping and not self._hasMapping(nextItem.name):
            logging.info(f'Needs a mapping: {nextItem}')
            self.getNextFeed()
        name = nextItem.name
        RunningManager._get_toRun().task_done()
        return Response(json.dumps({'name': name}), status=200)

    def getStatus(self, name):
        if session.name is None:
            return Response(json.dumps({'registered': False}), mimetype='application/json',status=200 )
        if session.isDisabled:
            return Response(json.dumps({'registered': False, 'status': session.small_dict()}), mimetype='application/json', status=200)
        req = session["routing"].get(f'/routingcontroller/getLastPage/{name}', resp=True, error=False)
        if req:
            logging.info(f'status: {session.name}, last_page={last_page.get("url")}, pages_processed={last_page.get("pagesProcessed")}')
            session.last_page = last_page.get('url')
            session.pages_processed = last_page.get('pagesProcessed')
        else:
            logging.warning(f'No history for {session.name}')
            session.last_page = None
            session.pages_processed = 0
        return Response(json.dumps({'status': session.small_dict(), 'registered': True}), mimetype='application/json',status=200)

    def markDone(self, name):
        session.stop()
        RunningManager._get_toRun().put(session.name)
        return 'ok'

    def refreshHistory(self, name):
        session["router"].delete(f'/routingcontroller/clearHistory/{name}')
        return 'ok'

    def addFeed(self, name):
        if session.name is not None:
            session.run()
            session.enable()
            RunningManager._get_toRun().put(session.name)
            return Response('not adding duplicate feed', status=200)
        else:
            session.setName(name)
            session.run()
            RunningManager._get_toRun().put(session.name)
            return Response('ok', status=200)

    def disableFeed(self, name):
        if session.name is None:
            return Response('cant disable unknown feed', status=200)
        else:
            session.markDisabled()
            return Response('ok', status=200)

    def markRunning(self, name):
        if session.name is None:
            return Response('cant mark unknown feed as running')
        session.run()
        return Response('ok', status=200)



