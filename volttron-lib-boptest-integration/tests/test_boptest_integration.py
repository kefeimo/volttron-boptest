"""
Note: in order to run this test suit,
    a local boptest simulation server needs to be running (including for .github/workflows)
Note: the TESTCASE environment variable needs to be defined
    i.e., TESTCASE=testcase1 docker-compose up
"""

import pytest
from boptest_integration.boptest_integration import BopTestSimIntegrationLocal
import random


# @pytest.mark.skip(reason="for local testing. Assuming a local testcase is running")
class TestBopTestSimIntegrationLocal:
    """
    Testing BopTestSimIntegrationLocal
    Note: assume using testcase1
    """

    def test_init(self):
        boptest_sim = BopTestSimIntegrationLocal()
        print(boptest_sim)
        assert boptest_sim

    def test_get_name(self):
        boptest_sim = BopTestSimIntegrationLocal()
        res = boptest_sim.get_name()
        print(res)
        assert res
        assert res == "testcase1"

    def test_put_initialize(self):
        boptest_sim = BopTestSimIntegrationLocal()
        res = boptest_sim.put_initialize(start_time=31 * 24 * 3600, warmup_period=7 * 24 * 3600)
        print(res)
        assert res

    def test_retrieve_time_info(self):
        """
        test init (for PUT/INITIALIZE)
        """
        boptest_sim = BopTestSimIntegrationLocal()
        res = boptest_sim.retrieve_time_info()
        print(res)
        res_1 = boptest_sim.put_initialize(start_time=31 * 24 * 3600, warmup_period=7 * 24 * 3600)
        res_2 = boptest_sim.retrieve_time_info()
        print(res_2)
        assert res
        assert res_2
        assert res != res_2

    def test_retrieve_time_info_init_scenario(self):
        """
        test init for PUT/SCENARIO
        """
        boptest_sim = BopTestSimIntegrationLocal()
        res = boptest_sim.retrieve_time_info()
        print(res)
        # Note: the scenario argument `time_period` is specific to testcase1
        scenario = {"time_period": "test_day", "electricity_price": "dynamic"}
        res_1 = boptest_sim.put_scenario(**scenario)
        res_2 = boptest_sim.retrieve_time_info()
        print(res_2)
        assert res
        assert res_2
        assert res != res_2

    def test_retrieve_time_info_advance(self):
        """
        test after advance (for PUT/INITIALIZE)
        """
        boptest_sim = BopTestSimIntegrationLocal()
        res = boptest_sim.retrieve_time_info()
        print(res)
        res_1 = boptest_sim.put_initialize(start_time=31 * 24 * 3600, warmup_period=7 * 24 * 3600)
        res_time_info = boptest_sim.retrieve_time_info()
        print(res_time_info)
        # advance 1 step
        step = boptest_sim.get_step()
        print(step)
        _ = boptest_sim.post_advance()
        res_time_info_2 = boptest_sim.retrieve_time_info()
        print(res_time_info_2)

        assert res_time_info["current_time"] + step == res_time_info_2["current_time"]

    def test_retrieve_time_info_advance_scenario(self):
        """
        test after advance (for PUT/SCENARIO)
        """
        boptest_sim = BopTestSimIntegrationLocal()
        res = boptest_sim.retrieve_time_info()
        print(res)
        # Note: the scenario argument `time_period` is specific to testcase1
        scenario = {"time_period": "test_day", "electricity_price": "dynamic"}
        res_1 = boptest_sim.put_scenario(**scenario)
        res_time_info = boptest_sim.retrieve_time_info()
        print(res_time_info)
        # advance n (1-10) random steps
        step = boptest_sim.get_step()
        # print(step)
        n = random.randint(1, 10)
        print(f"advanced n: {n} steps with length {step}, total time elapsed n * step = {n * step}.")
        for _ in range(n):
            _ = boptest_sim.post_advance()
        res_time_info_2 = boptest_sim.retrieve_time_info()
        print(res_time_info_2)

        assert res_time_info["current_time"] + step * n == res_time_info_2["current_time"]

    def test_put_scenario(self):
        boptest_sim = BopTestSimIntegrationLocal()
        # Note: the scenario argument `time_period` is specific to testcase1
        res = boptest_sim.put_scenario(time_period="test_day", electricity_price="dynamic")
        print(res)
        assert res

    def test_get_scenario(self):
        boptest_sim = BopTestSimIntegrationLocal()
        res = boptest_sim.get_scenario()
        print(res)
        assert res == "scenario is NOT set."
        res_1 = boptest_sim.put_initialize(start_time=31 * 24 * 3600, warmup_period=7 * 24 * 3600)
        res_2 = boptest_sim.retrieve_time_info()
        print(res_2)
        assert res_2 != res

    def test_get_measurements(self):
        boptest_sim = BopTestSimIntegrationLocal()
        res = boptest_sim.get_measurements()
        print(res)
        assert res

    def test_get_inputs(self):
        boptest_sim = BopTestSimIntegrationLocal()
        res = boptest_sim.get_inputs()
        print(res)
        assert res

    def test_get_step(self):
        boptest_sim = BopTestSimIntegrationLocal()
        res = boptest_sim.get_step()
        print(res)
        assert res

    def test_put_step(self):
        boptest_sim = BopTestSimIntegrationLocal()
        res = boptest_sim.put_step(7200)
        print(res)
        res_2 = boptest_sim.get_step()
        print(res_2)
        assert res_2 == 7200

    def test_post_advance(self):
        boptest_sim = BopTestSimIntegrationLocal()
        res = boptest_sim.post_advance()
        print(res)
        assert res

        try:
            boptest_sim = BopTestSimIntegrationLocal()
            # Note: the input data is only guaranteed to work for testcase1
            u = {'oveHeaPumY_u': 0.5, 'oveHeaPumY_activate': 1}
            res = boptest_sim.post_advance(data=u)
            print(res)
            assert res
        except Exception as e:
            print(e)

    def test_get_results(self):
        boptest_sim = BopTestSimIntegrationLocal()
        measures = boptest_sim.get_measurements()
        res = boptest_sim.put_results(point_names=[measures[0]])
        print(res)
        assert res

    def test_get_kpi(self):
        boptest_sim = BopTestSimIntegrationLocal()
        res = boptest_sim.get_kpi()
        print(res)
        assert res
