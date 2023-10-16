from __future__ import annotations
# -*- coding: utf-8 -*- {{{
# ===----------------------------------------------------------------------===
#
#                 Installable Component of Eclipse VOLTTRON
#
# ===----------------------------------------------------------------------===
#
# Copyright 2022 Battelle Memorial Institute
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# ===----------------------------------------------------------------------===

from pathlib import Path
from pprint import pformat
from typing import Callable, Dict

from volttron.client.messaging import (headers)
from volttron.utils import (format_timestamp, get_aware_utc_now, load_config,
                            setup_logging, vip_main)

import logging
import sys
import gevent

from volttron.client.vip.agent import Agent, Core, RPC
import subprocess
from volttron import utils
# from ._boptest_integration import BopTestSimIntegrationLocal
from boptest_integration.boptest_integration import BopTestSimIntegrationLocal
# import time
# import numpy as np
# from boptest_integration.controllers import PidController, SupController, PidTwoZonesController
from boptest_integration.interface import Interface


setup_logging()
_log = logging.getLogger(__name__)
__version__ = "1.0"


# def boptest_example(config_path, **kwargs) -> BopTestAgent:
#     """Parses the Agent configuration and returns an instance of
#     the agent created using that configuration.
#
#     :param config_path: Path to a configuration file.
#
#     :type config_path: str
#     :returns: BopTestAgent
#     :rtype: BopTestAgent
#     """
#     _log.debug("CONFIG PATH: {}".format(config_path))
#     try:
#         config = utils.load_config(config_path)
#     except Exception:
#         config = {}
#     #_log.debug("CONFIG: {}".format(config))
#     if not config:
#         _log.info("Using Agent defaults for starting configuration.")
#
#     return BopTestAgent(config, **kwargs)


class BopTestAgent(Agent):
    """This is class is a subclass of the Volttron Agent;
        This agent is an implementation of a Boptest outstation;
        The agent overrides @Core.receiver methods to modify agent life cycle behavior;
        The agent exposes @RPC.export as public interface utilizing RPC calls.
    """

    def __init__(self, config_path: str, **kwargs) -> None:
        super().__init__(enable_web=True, **kwargs)

        self.bp_sim = BopTestSimIntegrationLocal()
        self.config: dict = self._parse_config(config_path)
        # TODO: design config template
        # TODO: create config data class (with validation)
        logging.debug(f"================ config: {self.config}")

        # Init the result data
        self._results = None
        self._kpi = None
        # self._custom_kpi_result = None
        self._forecasts = None

        self._is_onstart_completed = False



    # @staticmethod
    # def boptest_up(testcase: str, docker_compose_file_path: str, is_verbose: bool = True) -> str:
    #     """
    #     EXAMPLE
    #     boptest_up(testcase="testcase1", docker_compose_file_path="/home/kefei/project/project1-boptest_integration/docker-compose.yml")
    #     """
    #     if is_verbose:
    #         verbose = "--verbose"
    #     else:
    #         verbose = ""
    #     cmd = f"TESTCASE={testcase} docker-compose {verbose} -f {docker_compose_file_path} up -d"
    #     res = subprocess.run([cmd], shell=True, stdout=subprocess.PIPE)
    #     return res.stdout.decode("utf-8")

    @Core.receiver("onstart")
    def onstart(self, sender, **kwargs):
        """
        This is method is called once the Agent has successfully connected to the platform.
        This is a good place to setup subscriptions if they are not dynamic or
        do any other startup activities that require a connection to the message bus.
        Called after any configurations methods that are called at startup.
        Usually not needed if using the configuration store.
        """
        pass
        interface = Interface(config=self.config)
        kpi, res, forecasts, custom_kpi_result = interface.run_workflow()
        print(f"======= kpi {kpi}")

        logging.info("=========== refactoring onstart")


        # VIEW RESULTS
        # -------------------------------------------------------------------------
        # Report KPIs
        kpi = self.bp_sim.get_kpi()
        for key in kpi.keys():

            # return kpi, res, custom_kpi_result, forecasts  # Note: originally publish these
            # TODO: refactor topic value to config
            default_prefix = "PNNL/BUILDING/UNIT/"
            self.vip.pubsub.publish(peer='pubsub', topic=default_prefix + "kpi", message=str(kpi))
            # self.vip.pubsub.publish(peer='pubsub', topic=default_prefix + "result", message=str(res))
            # TODO: publish custom_kpi_result forecasts

            # Store the result data
            self._results = res
            self._kpi = kpi
            # self._custom_kpi_result = custom_kpi_result
            self._forecasts = forecasts

            self._is_onstart_completed = True

        logging.info("======== onstart completed.======")


    def _parse_config(self, config_path: str) -> Dict:
        """Parses the agent's configuration file.

        :param config_path: The path to the configuration file
        :return: The configuration
        """
        try:
            config = load_config(config_path)
        except NameError as err:
            _log.exception(err)
            raise err
        except Exception as err:
            _log.error("Error loading configuration: {}".format(err))
            config = {}
        # print(f"============= def _parse_config config {config}")
        if not config:
            raise Exception("Configuration cannot be empty.")
        return config

    @RPC.export
    def rpc_dummy(self) -> str:
        """
        For testing rpc call
        """
        return "This is a dummy rpc call"

    # TODO: verify if onstart hook needs to finish first before evoke rpc call.
    @RPC.export
    def get_kpi_results(self):
        if self._is_onstart_completed:
            return self._kpi
        else:
            logging.info("Onstart process not finished")
            return

    @RPC.export
    def get_simulation_results(self):
        if self._is_onstart_completed:
            return self._results
        else:
            logging.info("Onstart process not finished")
            return None


def main():
    """Main method called to start the agent."""
    vip_main(BopTestAgent)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
