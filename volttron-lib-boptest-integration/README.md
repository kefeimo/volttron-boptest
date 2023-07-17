# boptest-integration

This python library is used for integrating boptest simulation into VOLTTRON platform.

BOPTEST is designed to facilitate
the performance evaluation and benchmarking of building control strategies, which
contains these key components:

1. Run-Time Environment (RTE): Deployed with Docker and accessed with a RESTful HTTP API, use the RTE to set up tests,
   control building emulators, access data, and report KPIs.

1. Test Case Repository: A collection of ready-to-use building emulators representing a range of building types and HVAC
   systems.

1. Key Performance Indicator (KPI) Reporting: A set of KPIs is calculated by the the RTE using data from the building
   emulator being controlled.

For more information, please visit [IBPSA Project 1 - BOPTEST](https://github.com/ibpsa/project1-boptest).

# Prerequisites

* Python 3 (tested with Python3.10)
* Linux OS (tested with Ubuntu 22.04)

## Python

<details>
<summary>To install specific Python version (e.g., Python 3.10), we recommend using <a href="https://github.com/pyenv/pyenv"><code>pyenv</code></a>.</summary>

```shell
# install pyenv
git clone https://github.com/pyenv/pyenv ~/.pyenv

# setup pyenv (you should also put these three lines in .bashrc or similar)
export PATH="${HOME}/.pyenv/bin:${PATH}"
export PYENV_ROOT="${HOME}/.pyenv"
eval "$(pyenv init -)"

# install Python 3.10
pyenv install 3.10

# make it available globally
pyenv global system 3.10
```

</details>

# Installation

The following recipe walks through the steps to install and run use case example.

Note: For the ease of reproducibility, in this demo, we
will git clone the [volttron-boptest](https://github.com/eclipse-volttron/volttron-boptest) repo to the `~/sandbox/`
path. Feel free to modify the workflow as desired.

   ```shell
   kefei@ubuntu-22:~/sandbox$ git clone https://github.com/eclipse-volttron/volttron-boptest.git
   Cloning into 'volttron-boptest'...
   remote: Enumerating objects: 450, done.
   remote: Counting objects: 100% (450/450), done.
   remote: Compressing objects: 100% (242/242), done.
   remote: Total 450 (delta 192), reused 424 (delta 170), pack-reused 0
   Receiving objects: 100% (450/450), 3.66 MiB | 7.06 MiB/s, done.
   Resolving deltas: 100% (192/192), done.
   kefei@ubuntu-22:~/sandbox$ cd volttron-boptest/
   kefei@ubuntu-22:~/sandbox/volttron-boptest$ 
   ```

1. Create and activate a virtual environment.

   It is recommended to use a virtual environment for installing library.

    ```shell
    kefei@ubuntu-22:~/sandbox/volttron-boptest$ python -m venv env
    kefei@ubuntu-22:~/sandbox/volttron-boptest$ source env/bin/activate
    (env) kefei@ubuntu-22:~/sandbox/volttron-boptest$
    ```


1. Install the "volttron-boptest-integration" library.

   There are two options to install "volttron-boptest-integration". You can install this library using the version on
   PyPi or install
   it from the source code (`git clone` might be required.)

    ```shell
    # option 1: install from pypi
    pip install volttron-lib-boptest-integration
    
    # option 2: install from the source code (Note: `-e` option to use editable mode, useful for development.)
    pip install [-e] <path-to-the-source-code-root>/volttron-lib-boptest-integration/
    ```
   
    ```shell
    (env) kefei@ubuntu-22:~/sandbox/volttron-boptest$ pip install volttron-lib-boptest-integration
    Collecting volttron-lib-boptest-integration
      Downloading volttron_lib_boptest_integration-0.1.1a0-py3-none-any.whl (20 kB)
    Collecting pandas>0.0.0
    ...
   
    (env) kefei@ubuntu-22:~/sandbox/volttron-boptest$ pip list | grep volttron
    volttron                         10.0.4rc1
    volttron-lib-boptest-integration 0.1.1a0
    ...
    ```

# Basic Usage

In order to demonstrate the basic usage of volttron-lib-boptest-integration, we need to setup the boptest simulation
server.

### Setup the boptest simulation server locally.

In order to demonstrate the basic usage of volttron-boptest-agent, we need to setup the boptest simulation server.

(Please see more details about boptest quick-start
at [Quick-Start to Deploy a Test Case](https://github.com/ibpsa/project1-boptest#quick-start-to-deploy-a-test-case))

1. Download [IBPSA Project 1 - BOPTEST](https://github.com/ibpsa/project1-boptest) repository to <boptest_repo>. For
   demo purpose, let boptest_repo be `~/project1-boptest`.

   ```shell
   git clone https://github.com/ibpsa/project1-boptest ~/project1-boptest
   ```

1. Install [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/).

   Note: this demo run docker as a non-root user, you can
   follow [Linux post-installation steps for Docker Engine](https://docs.docker.com/engine/install/linux-postinstall/)
   to achieve similar setup.

   (Optional) Verify with `docker-compose version` to verify the installation
   ```shell
   (env) kefei@ubuntu-22:~/sandbox/volttron-boptest$ docker-compose version
   docker-compose version 1.29.2, build unknown
   docker-py version: 5.0.3
   CPython version: 3.10.6
   OpenSSL version: OpenSSL 3.0.2 15 Mar 2022

   ```

1. Build and deploy a test case.

   The basic command to start a test case is by using `TESTCASE=<testcase_name> docker-compose up`.

   For demo purpose, we will build and deploy testcase1, for available testcases please
   see [testcases/](https://github.com/ibpsa/project1-boptest/tree/master/testcases)
   ```shell
   (env) kefei@ubuntu-22:~/sandbox/volttron-boptest$ TESTCASE=testcase1 docker-compose --file ~/project1-boptest/docker-compose.yml up
   Creating network "boptest-net" with the default driver
   Creating project1-boptest_boptest_1 ... done
   Attaching to project1-boptest_boptest_1
   boptest_1 | 07/13/2023 09:59:42 PM UTC root INFO Control step set successfully.
   boptest_1 | 07/13/2023 09:59:42 PM UTC root INFO Test simulation initialized successfully to 0.0s with warmup period of
   0.0s.
   boptest_1 | 07/13/2023 09:59:42 PM UTC root INFO Test case scenario was set successfully.
   ...
   boptest_1  |  * Debug mode: off
   boptest_1  | 07/13/2023 09:59:42 PM UTC werkzeug            INFO         * Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
   ```
   Or use detach mode
   ```shell
   (env) kefei@ubuntu-22:~/sandbox/volttron-boptest$ TESTCASE=testcase1 docker-compose --file ~/project1-boptest/docker-compose.yml up --detach 
   Starting project1-boptest_boptest_1 ... done
   (env) kefei@ubuntu-22:~/sandbox/volttron-boptest$ docker container ls
   CONTAINER ID   IMAGE          COMMAND                  CREATED        STATUS          PORTS                      NAMES
   ddd0f2cc1f99   boptest_base   "/bin/sh -c 'python …"   23 hours ago   Up 12 seconds   127.0.0.1:5000->5000/tcp   project1-boptest_boptest_1
   ```

   Note: Use `docker-compose down` to shut down the service.

   Verify boptest simulation server is running properly:
   ```shell
   (env) kefei@ubuntu-22:~/sandbox/volttron-boptest$ curl http://127.0.0.1:5000/name
   {"message":"Queried the name of the test case successfully.","payload":{"name":"testcase1"},"status":200}
   ```

1. Run example usecases.

   There are several exmaple usecases available at [examples/](examples). In this demo,
   we will run [testcase1.py](examples/tescase1.py).
   ```shell
   (env) kefei@ubuntu-22:~/sandbox/volttron-boptest$ python volttron-lib-boptest-integration/examples/testcase1.py
   INFO:root:=========== run_workflow
   INFO:root:
   TEST CASE INFORMATION
   ---------------------
   INFO:root:Name:                         testcase1
   ...
   INFO:root:======== run workflow completed.======
   ======= kpi {'cost_tot': 0.075149821513246, 'emis_tot': 0.2147137757521314, 'ener_tot': 1.073568878760657, 'idis_tot': 508.47225004790033, 'pdih_tot': None, 'pele_tot': None, 'pgas_tot': 0.09615811655434148, 'tdis_tot': 5.316029375566828, 'time_rat': 1.531114146269157e-05}
   ```

   Note: the example usecase must match the test case that is running. For example when TESTCASE=testcase1, we can
   run [testcase1.py](examples/testcase1.py) and [testcase1_scenario.py](examples/testcase1_scenario.py), but
   not [testcase2.py](examples/testcase2.py).

# Development

Please see the following for contributing
guidelines [contributing](https://github.com/eclipse-volttron/volttron-core/blob/develop/CONTRIBUTING.md).

Please see the following helpful guide
about [developing modular VOLTTRON agents](https://github.com/eclipse-volttron/volttron-core/blob/develop/DEVELOPING_ON_MODULAR.md)

# Disclaimer Notice

This material was prepared as an account of work sponsored by an agency of the
United States Government. Neither the United States Government nor the United
States Department of Energy, nor Battelle, nor any of their employees, nor any
jurisdiction or organization that has cooperated in the development of these
materials, makes any warranty, express or implied, or assumes any legal
liability or responsibility for the accuracy, completeness, or usefulness or any
information, apparatus, product, software, or process disclosed, or represents
that its use would not infringe privately owned rights.

Reference herein to any specific commercial product, process, or service by
trade name, trademark, manufacturer, or otherwise does not necessarily
constitute or imply its endorsement, recommendation, or favoring by the United
States Government or any agency thereof, or Battelle Memorial Institute. The
views and opinions of authors expressed herein do not necessarily state or
reflect those of the United States Government or any agency thereof.
