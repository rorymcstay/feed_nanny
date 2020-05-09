import json
import os

from flask import Response, request
from flask_classy import FlaskView, route

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from feed.settings import mongo_params
from feed.actiontypes import ActionTypes, ReturnTypes, get_mandatory_params
from feed.actionchains import ClickAction, CaptureAction, InputAction, PublishAction, Action
from feed.logger import getLogger

logging = getLogger(__name__)

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
            'inputString': 'Example Search input'
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
        if chains is None:
            chains = [{'name': 'NewAction'}]
        return Response(json.dumps([chain.get('name') for chain in chains]), mimetype='application/json')

    def getActionChain(self, name):
        res = self.actionChains.find_one({'name': name})
        if res is None:
            return Response(json.dumps(baseActionParams), mimetype='application/json')
        res.pop('_id')
        return Response(json.dumps(res), mimetype='application/json')

    def getActionTypes(self, name):
        return Response(json.dumps(ActionTypes), mimetype='application/json')

    def getActionParameters(self, name):
        params = get_mandatory_params(name)
        return Response(json.dumps(params), mimetype='application/json')

    def getPossibleValues(self):
        possible_values = {
            'actionType': ActionTypes,
            'returnType': ReturnTypes,
            'isSingle': [True, False],
            'attr': ['class', 'href', 'src', 'img']

        }
        return Response(json.dumps(possible_values), mimetype='application/json')

    @route('setActionChain/', methods=['PUT'])
    def setActionChain(self):
        actionChain = request.get_json()
        logging.info(f'request to set actionChain for {actionChain.get("name")}, have {len(actionChain.get("actions"))} actions')
        if self._verifyAction(actionChain):
            self.actionChains.replace_one({'name': actionChain.get('name')}, actionChain, upsert=True)
            return Response('ok', status=200)
        else:
            return Response('action chain was invalid')

    @route('deleteActionChain/<string:name>', methods=['DELETE'])
    def deleteActionChain(self, name):
        self.actionChains.delete_one({'name': name})
        return 'ok'

    def queryActionChain(self, name, field):
        it = self.actionChains.find_one({'name': name}, projection=[field])
        if it is None:
            return Response(json.dumps({field: None}), status=200, mimetype='application/json')
        else:
            it.pop('_id')
            return Response(json.dumps(it), mimetype='application/json')

    def listActionChains(self):
        ret = self.actionChains.find_all({}, project=['name'])
        return Response(json.dumps([name for name in ret]), mimetype='application/json')

    def _verifyAction(self, actionChain):
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
        if len(actionChain.get('actions', [])) == 0:
            logging.warning(f'{type(self).__name__}::_verifyAction(): No actions provided. params=[{actionChain}]')
            return False
        if not (actionChain.get('startUrl') and actionChain.get('name')):
            logging.warning(f'invalid request to update {actionChain.get("name")}, {json.dumps(actionChain)}')
            return False
        for action in actionChain.get('actions'):
            actionTypes = {
                "ClickAction": ClickAction,
                "InputAction": InputAction,
                "CaptureAction": CaptureAction,
                "PublishAction": PublishAction
            }
            const = actionTypes.get(action.get('actionType'), Action)
            try:
                const(position=0, **action)
            except Exception as ex:
                logging.warning(f'{type(self).__name__}::_verifyAction(): invalid action for actionType=[{action.get("actionType")}], used constructor=[{const.__name__}], excep=[{type(ex).__name__}] reason=[{ex.args}], params=[{action}]')
                return False
        return True

