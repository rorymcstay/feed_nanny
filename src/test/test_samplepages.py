from unittest import TestCase
from feed.testinterfaces import MongoTestInterface
import logging
import unittest
import time
import os
from pymongo import MongoClient
from feed.settings import mongo_params

from src.main.samplepages import SamplePages

class TestSamplePages(MongoTestInterface):

    def setUp(cls):
        cls.samplePages = SamplePages()
        self.example_sources = cls.mongo_client['sessions']['sample_pages']

    def test_htmlSourceRemoveCookies(self):
        src = self.example_sources.find_one({'name':'DoneDealCars', 'position': 0}, projection=['source'])
        html_src = HtmlSource(src)

