from unittest import TestCase
import logging
import unittest

from feed.testinterfaces import MongoTestInterface


from src.main.actionsmanager import ActionsManager

crawling = logging.getLogger('feed.actionchains')


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
    "name": "DoneDealCars"
}

class TestActionsManager(MongoTestInterface, TestCase):
    def setUp(cls):
        cls.actionsManager = ActionsManager()
        cls.mongo_client['actionChains']['actionChainDefinitions'].insert_one(chain)

    def tearDown(cls):
        cls.mongo_client.drop_database('actionChains')

    def test__verifyAction(self):
        isValid = self.actionsManager._verifyAction(chain)
        self.assertTrue(isValid)
        chain.pop('actions')

    def test_getActionChains(self):
        chains = self.actionsManager.getActionChains()
        self.assertEqual(chains.json, ['DoneDealCars'])

    def test_getActionChain(self):
        chainReq = self.actionsManager.getActionChain('DoneDealCars')
        chainReq.json.pop('_id', None)
        chain.pop('_id', None)
        self.assertDictEqual(chainReq.json, chain)

    def deleteAction(self):
        self.actionsManager.deleteActionChain('DoneDealCars')
        donedeal = self.mongo_client['actionChains']['actionChainDefinitions'].find_one({'name': 'DoneDealCars'})
        self.assertIsNone(donedeal)

    # TODO need a way to mock the request object

