import json
import os

from flask import Response, request
from flask_classy import FlaskView, route

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from feed.settings import mongo_params
from feed.actiontypes import ActionTypes

baseActionParams = {
    'name': 'NewAction',
    'startUrl': 'https://google.com',
    'isRepeating': False,
    'actions': [
        {
            'actionType': 'InputAction',
            'css': '.gsfi',
            'xpath': '//*[contains(concat( " ", @class, " " ), concat( " ", "gsfi", " " ))]',
            'text': '',
            'searchInput': 'Example Search input'
        },
        {
            'actionType': 'ClickAction',
            'css': '.gNO89b',
            'xpath': '//*[contains(concat( " ", @class, " " ), concat( " ", "gNO89b", " " ))]',
            'text': 'Google Search'
        }
    ]
}

class ActionsManager(FlaskView):
    client = MongoClient(**mongo_params)
    actionsDatabase: Database = client[os.getenv("ACTIONS_DATABASE", "actionChains")]
    actionChains: Collection = actionsDatabase['actionChainDefinitions']

    def newActionSchema(self):
        return Response(json.dumps(baseActionParams), mimetype='application/json')

    def getActionChains(self):
        chains = self.actionChains.find({}, projection=['name'])
        return Response(json.dumps([chain.get('name') for chain in chains]), mimetype='application/json')

    def getActionChain(self, name):
        res = self.actionChains.find_one({'name': name})
        if res is None:
            return Response(json.dumps(baseActionParams), mimetype='application/json')
        res.pop('_id')
        return Response(json.dumps(res), mimetype='application/json')

    def getActionTypes(self, name):
        return Response(json.dumps(ActionTypes), mimetype='application/json')

    @route('setActionChain/', methods=['PUT'])
    def setActionChain(self):
        actionChain = request.json()
        if self._verifyAction(actionChain):
            actionChains.replace_one({'name': actionChain.get('name')}, action, upsert=True)
            return Reponse('ok', status=200)
        else:
            return Reponse('action chain was invalid')

    @route('deleteActionChain/<string:name>', methods=['DELETE'])
    def deleteActionChain(self, name):
        self.actionChains.delete_one({'name': name})
        return 'ok'

    def listActionChains(self):
        ret = self.actionChains.find_all({}, project=['name'])
        return Response(json.dumps([name for name in ret]), mimetype='application/json')

    def _verifyAction(actionChain):
        """
        TODO: look into proper json validation libraries
        """
        chain_mandatory_params = ['', '', '']
        action_mandatory_params = ['actionType', 'css', '']
        if isinstance(actionChain.get('actions'), list):
            for action in actionChain.get('actions'):
                # check the mandatory parameters
                if not ( action.get('actionType') and action.get('css')):
                    logging.warning(f'invalid request to update {actionChain.get("name")}, {json.dumps(actionChain)}')
                    return False
        else:
            logging.warning(f'invalid request to update {actionChain.get("name")}, {json.dumps(actionChain)}')
            return False
        if not (actionChain.get('startUrl') and actionChain.get('name')):
            logging.warning(f'invalid request to update {actionChain.get("name")}, {json.dumps(actionChain)}')
            return False
        return True

