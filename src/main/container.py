import logging
import os
from typing import List, Union

import docker
from docker.errors import APIError
from docker.models.containers import Container as Browser
from feed.settings import browser_params, BrowserConstants
from time import time


class Container:
    name = None

    def __repr__(self):
        return "Container {} is {} and {}".format(self.port,
                                                  "active" if self.active else "not active", self.status)

    def __str__(self):
        return str(self.port)

    def __eq__(self, other):
        return type(self) == type(other) and self.port == other.name

    def __init__(self, port=None, active=True, status=None):
        self.port = port
        self.active = active
        self.status = status


class ContainerManager:
    client = docker.client.from_env()
    workerPorts = {int(browser_params.get("base_port", 4444)) + port: Container(
        port=int(browser_params.get("base_port", 4444)) + port, active=False, status="not started") for port in
                   range(browser_params.get("max", 10))}

    def resetContainers(self):
        for port in self.workerPorts:
            try:
                self.client.containers.get("worker-{}".format(port)).kill()
            except APIError as e:
                logging.info("couldn't kill worker-{} {} - {}".format(port, e.explanation, e.status_code))
            self.workerPorts.update({port: Container(port=port, active=False, status='reset')})
        status = self.getContainerStatus()
        return status

    def getMainContainer(self, port):
        """
        return the main port associated with a running browser container. Intended to be called by
        the feed
        :return: string of the main port
        """
        try:
            browser: Union[Browser, bool] = self.client.containers.run(
                image=self.client.images.get(browser_params['image']),
                detach=True,
                name='worker-{}'.format(port),
                ports={'4444/tcp': port},
                restart_policy={"Name": 'always'},
                network=os.getenv("NETWORK", "feed_default"))
            self.wait_for_log(browser, BrowserConstants().CONTAINER_SUCCESS)
            status = browser.status + ' new'
        except APIError as e:
            if e.status_code == 409:
                browser = self.client.containers.get('worker-{port}'.format(port=port))
                browser.restart()
                self.wait_for_log(browser, BrowserConstants().CONTAINER_SUCCESS)
                status = browser.status + ' restarted'
            else:
                browser = False
                status = "error"

        self.workerPorts.update(key=port, value=Container(port, active=True, status=status))
        return str(port)

    def getContainer(self):
        """
        return a port associated with a running browser container which is not the mainPort

        :return:
        """

        unused: List[Container] = list(filter(lambda port: self.workerPorts[port].active, self.workerPorts))

        if len(unused) == 0:
            return "max containers reached"
        else:
            port = self.workerPorts[unused[0]].port
            try:
                browser: Browser = self.client.containers.get('worker-{port}'.format(port=port))
                self.workerPorts[unused[0]].update(key=port, value=Container(port=port, active=True,
                                                                             status=browser.status)).result()
                browser.restart()
            except APIError as e:
                if e.status_code == 404:
                    browser = self.client.containers.run(self.client.images.get(browser_params['image']),
                                                         detach=True,
                                                         name='worker-{}'.format(port),
                                                         ports={'4444/tcp': port},
                                                         network=os.getenv("NETWORK", "car_default"))
                    self.workerPorts[unused[0]].update({port: Container(port, active=False, status=browser.status)})
                else:
                    return str(port)
            logging.info(msg='started browser named worker-{port}'.format(port=port))
            self.workerPorts[unused[0]].name = 'worker-{}'.format(port)
            self.wait_for_log(browser, BrowserConstants().CONTAINER_SUCCESS)
            return str(port)

    def getContainerStatus(self):

        return [str(self.workerPorts[item]) for item in self.workerPorts]

    def freeContainer(self, port):
        item = Container(port=port, active=False)
        self.workerPorts.update({port: item})
        try:
            browser: Browser = self.client.containers.get('worker-{port}'.format(port=port))
            browser.kill()
            browser.remove()
            logging.info("killed container {}".format(browser.name))
        except APIError as e:
            logging.info("couldn't kill container {} - {}".format(e.explanation, e.status_code))
        # TODO handle restarting container here - test that you can use a container after running for some time
        return "ok"

    def cleanUpContainer(self, port):
        try:
            res = self.client.containers.get("worker-{}".format(port))
            res.kill()
            res.remove()
            logging.info("killed container {}".format(res))
        except APIError as e:
            if e.status_code == 404:
                logging.info("container not found, moving on")
        self.workerPorts.update({port: Container(port, False)})
        return "ok"

    def wait_for_log(self, hub, success_criteria):
        """
        Wait until the partial_url returns in the logs
        :type hub: docker.client.containers
        :param hub:
        :param success_criteria:
        :return:
        """
        timeMax = time() + BrowserConstants().CONTAINER_TIMEOUT
        line = 'error'
        while line not in BrowserConstants().CONTAINER_SUCCESS or time() < timeMax:
            for line in hub.logs().decode().split('\n'):
                if success_criteria in line:
                    logging.debug(line)
                    return

        # TODO handle RemoteDisconnected
        # TODO check for running containers before creation/worker to store running containers
