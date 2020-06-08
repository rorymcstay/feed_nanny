from unittest import TestCase
from feed.testinterfaces import MongoTestInterface
import logging
from flask import Flask
import unittest
import time
import os
from pymongo import MongoClient
from feed.settings import mongo_params

from src.main.samplepages import SamplePages
from src.main.app import app

class TestSamplePages(TestCase, MongoTestInterface):

    @classmethod
    def setUpClass(cls):
        print('setting up containers for SamplePages')
        cls.createMongo()

    @classmethod
    def setUp(cls):
        print('Setting up test classes and app')
        cls.samplePages = SamplePages()
        cls.app = app

    @unittest.skip
    def test_htmlSourceRemoveCookies(self):
        with self.app.test_request_context(data='<div>Hello world</div>'):
            src = self.example_sources.find_one({'name':'DoneDealCars', 'position': 0}, projection=['source'])
            ##html_src = HtmlSource(src)


if __name__ == '__main__':
    unittest.main()
