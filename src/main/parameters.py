import os
from datetime import datetime
from time import time

import bson.json_util as json
import checksumdir
import pymongo
from pymongo.database import Database

from feed.settings import mongo_params


class ParameterManager:
    """
    The ParameterManager controls the parameters. It delivers them to the client.

    """
    client = pymongo.MongoClient(**mongo_params)
    feed_params: Database = client[os.getenv("PARAMETER_DATABASE", "params")]
    feed_stats: Database = client[os.getenv("PARAMETER_STATS", "param_stats")]

    def getFeeds(self):
        return [feed.get("name") for feed in  self.feed_params["leader"].find({})]

    def getParameter(self, collection, name):
        param = self.feed_params[collection].find_one(filter={"name": name})
        return param

    def reportParam(self, feedName, parameter_key, component):
        now = time()
        event = {
            "time": now,
            "parameter": parameter_key,
            "feed": feedName,
            "component": component
        }

        self.feed_stats[component].insert_one(event)
        return "ok"
