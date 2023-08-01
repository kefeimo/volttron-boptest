"""
This test suits focus on the exposed RPC calls.
It utilizes a vip agent to evoke the RPC calls.
The volltron instance and boptest-agent will be started.
A boptest simulation is assumed to be running locally, (including for .github/workflows)
Note: several fixtures are used
    volttron_platform_wrapper
    vip_agent
    boptest_agent
"""
import pathlib

import gevent
import pytest
import os
from volttron.client.vip.agent import build_agent
from time import sleep
import datetime
# from boptest_integration.boptest_integration import BopTestSimIntegrationLocal
from boptest.agent import BopTestAgent

import random
import subprocess
from volttron.utils import is_volttron_running
import json
# from utils.testing_utils import *
from volttrontesting.fixtures.volttron_platform_fixtures import volttron_instance

import logging

logging_logger = logging.getLogger(__name__)
logging_logger.setLevel(logging.INFO)

boptest_vip_identity = "volttron_boptest_agent"


@pytest.fixture(scope="module")
def volttron_home():
    """
    VOLTTRON_HOME environment variable suggested to setup at pytest.ini [env]
    """
    volttron_home: str = os.getenv("VOLTTRON_HOME")
    assert volttron_home
    return volttron_home


def test_volttron_home_fixture(volttron_home):
    assert volttron_home
    print(volttron_home)


# def test_testing_file_path():
#     parent_path = os.getcwd()
#     boptest_agent_config_path = os.path.join(parent_path, "testcase1.config")
#     # print(boptest_agent_config_path)
#     logging_logger.info(f"test_testing_file_path {boptest_agent_config_path}")


def test_volttron_instance_fixture(volttron_instance):
    print(volttron_instance)
    logging_logger.info(f"=========== volttron_instance_new.volttron_home: {volttron_instance.volttron_home}")
    logging_logger.info(f"=========== volttron_instance_new.skip_cleanup: {volttron_instance.skip_cleanup}")
    logging_logger.info(f"=========== volttron_instance_new.vip_address: {volttron_instance.vip_address}")


@pytest.fixture(scope="module")
def vip_agent(volttron_instance):
    # build a vip agent
    a = volttron_instance.build_agent()
    print(a)
    return a


def test_vip_agent_fixture(vip_agent):
    print(vip_agent)
    logging_logger.info(f"=========== vip_agent: {vip_agent}")
    logging_logger.info(f"=========== vip_agent.core.identity: {vip_agent.core.identity}")
    logging_logger.info(f"=========== vip_agent.vip.peerlist().get(): {vip_agent.vip.peerlist().get()}")


@pytest.fixture(scope="module")
def boptest_agent(volttron_instance) -> dict:
    """
    Install and start a boptest-agent, return its vip-identity
    """
    # install a boptest-agent
    # TODO: improve the following hacky path resolver
    parent_path = pathlib.Path(__file__)
    boptest_agent_package_path = pathlib.Path(parent_path).parent.parent
    # boptest_agent_config_path = str(os.path.join(parent_path, "testcase1.config"))
    config = {
        "testcase_name": "testcase1",
        "initialize":  # for GET/initialize
            {
                "start_time": 0,
                "warmup_period": 0
            },
        "scenario": None,
        "step": 300,
        "length": 86400,
        "controller":
            {
                "type": "pid",  # currently support "pid", "sup", pidTwoZones"
                "u":
                    {
                        "oveAct_u": 0,
                        "oveAct_activate": 1
                    }
            }
    }
    agent_vip_id = boptest_vip_identity
    uuid = volttron_instance.install_agent(
        agent_dir=boptest_agent_package_path,
        config_file=config,
        start=False,  # Note: for some reason, need to set to False, then start
        vip_identity=agent_vip_id)
    # start agent with retry
    # pid = retry_call(volttron_instance.start_agent, f_kwargs=dict(agent_uuid=uuid), max_retries=5, delay_s=2,
    #                  wait_before_call_s=2)

    # # check if running with retry
    # retry_call(volttron_instance.is_agent_running, f_kwargs=dict(agent_uuid=uuid), max_retries=5, delay_s=2,
    #            wait_before_call_s=2)
    gevent.sleep(5)
    pid = volttron_instance.start_agent(uuid)
    gevent.sleep(5)
    logging_logger.info(
        f"=========== volttron_instance.is_agent_running(uuid): {volttron_instance.is_agent_running(uuid)}")
    # TODO: get retry_call back
    return {"uuid": uuid, "pid": pid}


def test_install_boptest_agent_fixture(boptest_agent, vip_agent, volttron_instance):
    puid = boptest_agent
    print(puid)
    logging_logger.info(f"=========== boptest_agent ids: {boptest_agent}")
    logging_logger.info(f"=========== vip_agent.vip.peerlist().get(): {vip_agent.vip.peerlist().get()}")
    logging_logger.info(f"=========== volttron_instance_new.is_agent_running(puid): "
                        f"{volttron_instance.is_agent_running(boptest_agent['uuid'])}")
    assert boptest_agent


def test_dummy(vip_agent, boptest_agent):
    peer = boptest_vip_identity
    method = BopTestAgent.rpc_dummy
    peer_method = method.__name__  # "rpc_dummy"
    # peer_method = "rpc_dummy"
    rs = vip_agent.vip.rpc.call(peer, peer_method).get(timeout=5)
    print(datetime.datetime.now(), "rs: ", rs)
