from flask.sessions import SessionMixin
import os
import time
from flask import session, g
import logging

class Feed(dict, SessionMixin):

    def __init__(self, **kwargs):
        logging.info(f'creating Feed session {kwargs.get("name")})')
        self.name = kwargs.get('name')
        self.last_ran = kwargs.get('last_ran', time.time())
        self.running = kwargs.get('running', False)
        self.isDisabled = kwargs.get('isDisabled', False)
        self.last_page = kwargs.get('lastPage', None)
        self.needs_mapping = kwargs.get('needsMapping', False)
        self.pages_processed = kwargs.get('pagesProcessed', 0)
        self.userID = str(kwargs.get('userID', None))
        #self.example_sources = kwargs.get('exampleSources', [])
        self.sample_pending = False
        self.num_examples = kwargs.get('numExamples', 0)

    def run(self):
        self.running = True
        self.modified = True

    def setPending(self):
        self.sample_pending = True
        self.modified = True

    def setNeedsMapping():
        self.needs_mapping = True
        self.modified = True


    def setExampleSource(self, source, position):
        self.num_examples += 1
        logging.info(f'setting sample source of length={len(source)} for {self.name}')
        session['chain_db']['sample_pages'].replace_one({'name': session.name, 'position': position, 'userID': session.userID}, {'position': position ,'name': session.name, 'source': source, 'userID': session.userID}, upsert=True)
        self.modified=True

    def markDisabled(self):
        self.isDisabled = True
        self.modified = True

    def enable(self):
        self.isDisabled = False
        self.modified = True

    def getLastRan(self):
        self.modified=False
        return self.last_ran

    def stop(self):
        self.running = False
        self.last_ran = time.time()
        self.modified = True

    def setName(self, name):
        self.name = name
        self.modified = True

    def __dict__(self):
        self.modified=False
        return dict(name=self.name,
                    lastRan=self.last_ran,
                    running=self.running,
                    needsMapping=self.needs_mapping,
                    userID=self.userID,
                    samplePending=self.sample_pending,
                    isDisabled=self.isDisabled,
                    lastPage=self.last_page,
                    numExamples=self.num_examples,
                    pagesProcessed=self.pages_processed)

    def small_dict(self):
        self.modified=False
        return dict(name=self.name,
                    lastRan=self.last_ran,
                    running=self.running,
                    needsMapping=self.needs_mapping,
                    samplePending=self.sample_pending,
                    userID=self.userID,
                    isDisabled=self.isDisabled,
                    lastPage=self.last_page,
                    #exampleSources=self.example_sources,
                    pagesProcessed=self.pages_processed)
    def __repr__(self):
        return f'name={self.name}, lastRan={self.last_ran}, running={self.running}, disabled={self.isDisabled}'

