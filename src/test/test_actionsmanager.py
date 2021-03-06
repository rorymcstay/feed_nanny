from unittest import TestCase
import logging
import unittest

from feed.testinterfaces import MongoTestInterface
from flask import Response



from src.main.actionsmanager import ActionsManager

crawling = logging.getLogger('feed.actionchains')
logging.getLogger().setLevel(logging.DEBUG)


chain = {
    "startUrl": "https://www.donedeal.co.uk/cars",
    "isRepeating": True,
    "actions": [
        {
            "actionType": "CaptureAction",
            "css": ".card__body",
            "xpath": "//*[contains(concat( \" \", @class, \" \" ), concat( \" \", \"card__body\", \" \" ))]",
            "text": "",
            "inputString": "Example Search input",
            "undefined": "",
            "captureName": "donedeal_cars",
            "isSingle": False
        },
        {
            "actionType": "ClickAction",
            "css": ".ng-isolate-scope",
            "xpath": "//*[contains(concat( \" \", @class, \" \" ), concat( \" \", \"ng-isolate-scope\", \" \" ))]",
            "text": "Next",
            "undefined": "",
            "isSingle": True
        }
    ],
    'userID': '1',
    "name": "DoneDealCars"
}

class TestActionsManager(TestCase, MongoTestInterface):

    @classmethod
    def setUp(cls):
        print('setting up class for ActionManager tests')
        cls.actionsManager = ActionsManager()
        cls.mongo_client['actionChains']['actionChainDefinitions'].replace_one({'name': chain.get('name')}, replacement=chain, upsert=True)
        from src.main.app import app
        cls.app = app

    @classmethod
    def setUpClass(cls):
        print('setting up containers for TestActionsManager')
        cls.createMongo()
        print('Complete setting up containers for TestActionsManager')

    def test__verifyAction(self):
        isValid = self.actionsManager._verifyAction(chain)
        self.assertTrue(isValid.get('valid'))
        chain.pop('actions')

    def tearDown(cls):
        cls.mongo_client.drop_database('actionChains')

    def test_getActionChains(self):
        with self.app.test_request_context(headers={'userID': 1}):
            chains = self.actionsManager.getActionChains()
            self.assertEqual(chains.json, ['DoneDealCars'])

    def test_getActionChain(self):
        with self.app.test_request_context(headers={'userID': 1}):
            chainReq = self.actionsManager.getActionChain('DoneDealCars')
            chainReq.json.pop('_id', None)
            chain.pop('_id', None)
            self.assertDictEqual(chainReq.json, chain)

    def deleteAction(self):
        self.actionsManager.deleteActionChain('DoneDealCars')
        donedeal = self.mongo_client['actionChains']['actionChainDefinitions'].find_one({'name': 'DoneDealCars'})
        self.assertIsNone(donedeal)


if __name__ == '__main__':
    unittest.main()
