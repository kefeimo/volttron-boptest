from __future__ import annotations

import datetime
import time
from boptest_integration.controllers import *
import numpy as np

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
from .workflow import Interface
from volttron.utils.scheduling import periodic

logger = logging.getLogger()
logger.setLevel(logging.INFO)

setup_logging()
_log = logging.getLogger(__name__)
_log.setLevel(logging.INFO)
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
        self.interface = Interface(config=self.config)
        # TODO: design config template
        # TODO: create config data class (with validation)
        logging.debug(f"================ config: {self.config}")

        # Init the result data
        self._results = None
        self._kpi = None
        # self._custom_kpi_result = None
        self._forecasts = None

        self._is_onstart_completed = False

        self.cosim_freq = 3  # the frequency of co-simulation, e.g., freq of publish
        self.cosim_types = None
        self._first_time_run_periodic = True

    @Core.receiver("onstart")
    def onstart(self, sender, **kwargs):
        """
        This is method is called once the Agent has successfully connected to the platform.
        This is a good place to setup subscriptions if they are not dynamic or
        do any other startup activities that require a connection to the message bus.
        Called after any configurations methods that are called at startup.
        Usually not needed if using the configuration store.
        """

        if self.config.get("co-simulate"):  # using cosimulation
            self.cosim_freq = self.config.get("co-simulate").get("freq")
            self.cosim_types = self.config.get("co-simulate").get("types")
            rt_periodic = self.core.periodic(self.cosim_freq,
                                             self._run_periodic,
                                             wait=0)
            # logging.info(f"======== _ {_} ======")
        else:
            # periodic testing
            _ = self._publish_final_output()

        self._is_onstart_completed = True
        logging.info("======== onstart completed.======")

        # Example publish to pubsub
        # self.vip.pubsub.publish('pubsub', "some/random/topic", message="HI!")
        #
        # # Example RPC call
        # # self.vip.rpc.call("some_agent", "some_method", arg1, arg2)
        # pass
        # self._create_subscriptions(self.setting2)

    def _publish_final_output(self):
        """
        retrieve and publish the final (i.e., end of the simulation) output (results/measurements, kpis, forecasts.)
        """
        interface = self.interface
        logging.info("=========== run_workflow NEW 2++++++++++++++++++")

        interface.populate_testcase_info()
        interface.config_custom_kpi()
        interface.initialize_testcase()
        kpi, result, forecasts, custom_kpi_result = interface.advance_simulation(is_loop=True)
        interface.populate_output_kpis()
        interface.populate_output_measurements()

        logger.info("======== run workflow completed.======")
        print(f"======= kpi {kpi}")

        # Report KPIs
        kpi: dict = self.bp_sim.get_kpi()
        # return kpi, res, custom_kpi_result, forecasts  # Note: originally publish these
        # TODO: refactor topic value to config
        default_prefix = "PNNL/BUILDING/UNIT/"
        self.vip.pubsub.publish(peer='pubsub', topic=default_prefix + "kpi", message=[kpi])
        # self.vip.pubsub.publish(peer='pubsub', topic=default_prefix + "result", message=str(res))
        # TODO: publish custom_kpi_result forecasts

        # Store the result data
        self._results = result
        self._kpi = kpi
        self._custom_kpi_result = custom_kpi_result
        self._forecasts = forecasts

        return result, kpi, forecasts

    # @Core.schedule(periodic(5))
    def _run_periodic(self):
        """Periodic call

        Used to maintain the time since each topic's last publish.
        Sends an alert if any topics are missing.
        """
        logging.info((f"************** {datetime.datetime.now()} ************** "))
        interface = self.interface
        # logging.info("=========== run_workflow NEW 2++++++++++++++++++")

        if self._first_time_run_periodic:  # init only one time
            interface.populate_testcase_info()
            interface.config_custom_kpi()
            interface.initialize_testcase()
        # advance one step (is_loop=False)
        kpi, result, forecasts, custom_kpi_result = interface.advance_simulation(is_loop=False)
        interface.populate_output_kpis()
        interface.populate_output_measurements()

        # logger.info("======== run workflow completed.======")
        # print(f"======= kpi {kpi}")

        # TODO: refactor topic value to config
        # publish outcome to message bus, depending on co_simulate_outcome_types,
        # support ["measurement", "kpi", "forecast", "custom_kpi"]
        default_prefix = "PNNL/BUILDING/UNIT/"
        co_simulate_outcome_types = self.config.get("co-simulate").get("types")
        if "kpi" in co_simulate_outcome_types:
            self.vip.pubsub.publish(peer='pubsub', topic=default_prefix + "kpi", message=[kpi])
        if "measurement" in co_simulate_outcome_types:
            self.vip.pubsub.publish(peer='pubsub', topic=default_prefix + "measurement", message=[result])
        if "forecast" in co_simulate_outcome_types:
            self.vip.pubsub.publish(peer='pubsub', topic=default_prefix + "forecast", message=[forecasts])
        if "custom_kpi" in co_simulate_outcome_types:
            self.vip.pubsub.publish(peer='pubsub', topic=default_prefix + "custom_kpi", message=[custom_kpi_result])
        # self.vip.pubsub.publish(peer='pubsub', topic=default_prefix + "result", message=str(res))
        # TODO: publish custom_kpi_result forecasts

        # Store the result data
        self._results = result
        self._kpi = kpi
        self._custom_kpi_result = custom_kpi_result
        self._forecasts = forecasts
        self._first_time_run_periodic = False

        return result, kpi, forecasts, custom_kpi_result

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
