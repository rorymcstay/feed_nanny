from flask_classy import FlaskView, route
import os
from bs4 import BeautifulSoup
import logging
from feed.settings import nanny_params, ui_server_params
from flask import session, Response, request
import json
import requests as r

class HtmlSource:
    def __init__(self, source):
        self.soup = BeautifulSoup(source)
        self._insertSelector()

    def _get_tag(self, tag_type, resource):
        att = {}
        if tag_type == 'link':
            att.update({'rel': "stylesheet"})
            att.update({'href': resource })
        elif tag_type == 'script':
            att.update({'src':resource})
        return self.soup.new_tag(tag_type, **att)

    def _insertSelector(self):
        gadget = self._get_tag('script', '/samplepages/getSelectorGadget/')
        css = self._get_tag('link', '/samplepages/getSelectorGadgetCss/')
        initialise = self._get_tag('script', '/samplepages/getSelectorGadgetInitialise/')
        button = self.soup.new_tag('input', **dict(type="button", id="sg_toggle_btn", value="Toggle SelectorGadget"))
        self.soup.head.append(gadget)
        logging.info(f'added {gadget} to html')
        self.soup.head.append(css)
        self.soup.body.append(initialise)
        logging.info(f'added {css} to html')
        self.soup.body.append(button)
        logging.info(f'added {button} to html')


class SamplePages(FlaskView):

    @route('getSamplePage/<string:name>/<int:position>')
    def getSamplePage(self, name, position):
        if session.name is None:
            return Response(status=404)
        if len(session.example_sources) <= position:
            position = len(session.example_sources)
        if len (session.example_sources) == 0 or not session.sample_pending and session.example_sources[position] is None:
            logging.info(f'example source {position} is none and status is not pending {name}')
            return Response("<div>RefreshSources</div>", status=200, mimetype='text/html')
        elif session.sample_pending:
            return Response("<div>Loading</div>", status=200, mimetype='text/html')
        else:
            logging.info(f'sending sample source to client, name={name}, sample_source_len={len(session.example_sources[position])}')
            enrichedHtmlFile = HtmlSource(session.example_sources[position])
            return Response(str(enrichedHtmlFile.soup), status=200, mimetype='text/html')

    def requestSamplePages(self, name):
        if session.name is None:
            session.setName(name)
        try:
            data = request.get_json()
            url = data.get('url')
        except Exception:
            url = r.get('http://{host}:{port}/actionsmanager/getActionChain/{name}'.format(name=name, **nanny_params)).json()

        logging.info(f'requesting {url} to be sample')
        r.put('http://{host}:{port}/schedulemanager/scheduleActionChain/{name}'.format(name=name, **ui_server_params), json={
            "url": url,
            "actionName": name,
            "trigger": 'date',
            "increment_size": 2,
            "increment": 'seconds'
            })
        logging.info('added job to collect sample page')
        return 'ok'

    @route('setExampleSource/<string:name>/<int:position>', methods=["POST"])
    def setExampleSource(self, name, position):
        if session is None:
            logging.info(f'{name} requested but not present in memory')
            return Response(f'feed: {name} not found.', status=404)
        source = request.get_data(as_text=True)
        session.setExampleSource(source, position)
        return Response('ok', status=200)

    def getSourceStatus(self, name):
        if session is None:
            return Response(json.dumps([]), mimetype='application/json')
        actions = r.get('http://{host}:{port}/actionsmanager/queryActionChain/{chain}/actions'.format(chain=name,**nanny_params)).json().get('actions', [])
        status =[]
        for i in range(len(actions)):
            if i < len(session.example_sources):
                status.append({'ready': True})
            else:
                status.append({'ready': False})
        return Response(json.dumps(status), mimetype='application/json')

    def _getSelectorComponent(self, filename):
        with open(f'{os.getenv("SELECTOR_GADGET", "./selector")}/{filename}') as jsfile:
            fileTxt = jsfile.read()
        return Response(fileTxt, status=200, mimetype=f'text/{filename.split(".")[-1]}')

    def getSelectorGadget(self):
        return self._getSelectorComponent('selectorgadget_combined.js')

    def getSelectorGadgetCss(self):
        return self._getSelectorComponent('selectorgadget_combined.css')

    def getSelectorGadgetInitialise(self):
        return self._getSelectorComponent('initialise_gadget.js')


