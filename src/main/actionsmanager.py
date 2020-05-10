import json
import os

from flask import Response, request
from flask_classy import FlaskView, route

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from feed.settings import mongo_params
from feed.actiontypes import ActionTypes, ReturnTypes, get_mandatory_params
from feed.actionchains import ClickAction, CaptureAction, InputAction, PublishAction, Action, ActionTypesMap
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
        response = Response()
        res = self._verifyAction(actionChain, response)
        if res.get('valid'):
            self.actionChains.replace_one({'name': actionChain.get('name')}, actionChain, upsert=True)
        return Response(json.dumps(res), mimetype='application/json')

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

    def _verifyAction(self, actionChain, response: Response):
        """
        TODO: look into proper json validation libraries
        """
        chain_mandatory_params = ['startUrl', 'name', 'actions', 'isRepeating']
        # first test costruct all the different Actions
        if isinstance(actionChain.get('actions'), list):
            # Test construct each type of action
            for pos, action in enumerate(actionChain.get('actions')):
                # TODO remove this into an imported dict
                const = ActionTypesMap.get(action.get('actionType')) # if not found then we will fail
                try:
                    const(position=0, **action)
                except KeyError as ex:
                    response = {'valid': False, 'reason': f'Missing mandatory parameters for {const.__name__}', 'keys': [ex.args[0]], 'position': pos}
                    logging.warning(f'{type(self).__name__}::_verifyAction(): missing default parameters for actionType=[{action.get("actionType")}], used constructor=[{const.__name__}], excep=[{type(ex).__name__}] reason=[{ex.args}], params=[{action}]')
                    return response
                except TypeError as ex:
                    response.json = {f'valid': False, 'reason': 'Unsupported Action', 'actionType': action.get('type'), position: pos}
                    return response
        else:
            response = {'valid': False, 'reason': '"actions" should be a list', 'key': 'actions'}
            logging.warning(f'invalid request to update {actionChain.get("name")}, {json.dumps(actionChain)}')
        # makesure we didn't skip through
        if len(actionChain.get('actions', [])) == 0:
            logging.warning(f'{type(self).__name__}::_verifyAction(): No actions provided. params=[{actionChain}]')
            response = {'valid': False, 'reason': 'No actions provided'}
        # next validate the mandatory parameters for the chain
        if not all(actionChain.get(key) for key in chain_mandatory_params):
            logging.warning(f'invalid request to update {actionChain.get("name")}, {json.dumps(actionChain)}')
            response = {'valid': False, 'reason': 'Missing mandatory params', 'keys': list(filter(lambda key: actionChain.get(key) is None, chain_mandatory_params))}
            return response
        response = {'valid': True}
        return response

