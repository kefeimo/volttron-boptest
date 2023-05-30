.. _Platform-Driver-Agent:

===============
Platform Driver
===============

The Platform Driver Agent manages all device communication. This agent automatically collects publishes data from
configured devices to the message bus, generally on a specified interval. It also features a number of RPC endpoints for
getting and setting points on devices.

How does it work?
=================

Drivers are special-purpose agents for device communication. Unlike most agents, drivers run as separate threads under
the Platform Driver (typically agents are spawned as their own process). The Platform Driver creates a driver instance
for each :ref:`device configuration <Device-Configuration-File>` in the platform driver's configuration store. While
running, the driver periodically polls ("scrapes") data from the device and publishes it to the message bus. The driver
additionally handles ad-hoc read and write requests issued by RPC through the :ref:`Actuator <Actuator-Agent>` or
Platform Driver agents. When device configurations are removed from the store, the corresponding driver instance is also
removed by the Platform Driver.

.. note::

    Earlier versions of VOLTTRON referred to all data collection from a device as "scraping". The word scraping
    most typically connotes the programmatic extraction of data from an unconventional source, such as a web page.
    While a driver might be written to do this, most read data from devices designed with the purpose of answering such
    queries. The documentation has, therefore, been update to use the more precise language. The word "pull" or "query"
    are used for the activity of discretely requesting data from a remote, while the word "polling" is used where the
    data is requested in a periodic loop. For reasons of compatability, most settings and methods which affect polling
    behavior retain the word "scrape" in their names. The words "poll" and "scape", as used here, may be considered
    interchangeable.

Actual communication with devices is handled by the driver's "Interface" class. An Interface is a Python class
which serves as the interface between the driver and the device.  The Interface does this by implementing a set of
well-defined actions using the communication paradigms and protocols (e.g., BACnet, Modbus, or HTTP) used by the
device. Interfaces wrap protocol-specific functionality in standard methods to be used by the driver. Information on
developing new driver interfaces can be found :ref:`here <Driver-Development>`.

.. _Platform-Driver-Configuration:

Configuration and Installation
==============================

Installation
------------

The platform driver agent may be installed using vctl:

.. code-block:: bash

    vctl install volttron-platform-driver --vip-identity platform.driver --tag driver

Additionally, to communicate with any devices, it will be necessary to install one or more interface libraries.
These may be installed from pypi using pip:

.. code-block:: bash

    pip install volttron-lib-fake-driver

Officially maintained driver interfaces (with corresponding package names) include:

* :ref:`Fake Driver <Fake-Driver>`: volttron-lib-fake-driver
* :ref:`BACnet Driver <BACnet-Driver>`: volttron-lib-bacnet-driver
* :ref:`DNP3 Driver <DNP3-Driver>`: volttron-lib-dnp3-driver
* :ref:`PyModbus Driver <Modbus-Driver>`: volttron-lib-modbus-driver
* :ref:`ModbusTk Driver <Modbus-TK-Driver>`: volttron-lib-modbustk-driver

Configuration
-------------

The Platform Driver requires use of the configuration store and expects three types of configuration file:

* **Platform Driver Agent Configuration (one for the agent):** global settings for all drivers.
* **Device Configuration (one per device):** settings for the driver to manage an individual device.
* **Registry (up to one per device):** contains the settings for each individual data point for a device or class of
  device. Some drivers may require one per registry per individual device, but often one registry may be shared by
  multiple devices of the same type.

Platform Driver Agent Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Platform Driver Agent configuration consists of general settings for all devices. The default values of the Platform
Driver should be sufficient for most users. If changes are made to any of the global settings, this configuration should
be saved to the configuration store with the name `config`:

.. code-block:: bash

    vctl config store platform.driver config path/to/edited/config/file

The following example sets the driver_scrape_interval to 0.05 seconds or 20 devices per second:

.. code-block:: json

    {
        "driver_scrape_interval": 0.05,
        "publish_breadth_first_all": false,
        "publish_depth_first": false,
        "publish_breadth_first": false,
        "publish_depth_first_all": true,
        "group_offset_interval": 0.0
    }

* **driver_scrape_interval** - Sets the interval between devices polls. Defaults to 0.02 or 50 devices per second.
  This is useful for when the platform polls too many devices at once resulting in failed polls. To spread polling of n
  devices evenly throughout a polling cycle, this may be set to:

    .. code-block::

        length_of_cycle / n

  If multiple groups are used, n would be the size of the largest group.

* **group_offset_interval** - Sets the delay between when each group of devices begins to be polled. There is no effect
  if all devices are in the same group. Group 0 will begin at ``t=0``. The first device of each subsequent group will
  be polled starting at

  .. code-block::

      t = group_number * group_offset_interval.

.. _Device-Scalability-Settings:

To improve the scalability of the platform unneeded device state publishes for all devices can be turned on and off.
Configured at the agent level, these settings will apply to all devices, but may be overridden on a device-by-device
manner in the :ref:`Device Configuration <Device-Configuration-File>`.

.. note::

    Depth first publishes have topics with the point name at the end (i.e., "campus/building/device/point").
    Breadth first publishes have topics with the point name at the beginnning (i.e., "point/device/building/campus").


* **publish_depth_first_all** (default `True`) - Enable "depth first" publish of all points to a single topic.
* **publish_breadth_first_all** - (default `False`) Enable "breadth first" publish of all points to a single topic.
* **publish_depth_first** - (default `False`) Enable separate "depth first" device state publishes for each point.
* **publish_breadth_first** - (default `False`) Enable separate "breadth first" device state publishes for each point.

An example `platform driver configuration file <https://raw.githubusercontent.com/eclipse-volttron/volttron-platform-driver/main/config>`_, with default settings can be found in the volttron-platform-driver
repository.

.. _Device-Configuration-File:

Device Configuration
^^^^^^^^^^^^^^^^^^^^

Each device must have a corresponding device configuration in the platform driver configuration store.
The topic used to reference the device is derived from the name of this device configuration. For instance,
to follow the common topic convention of ``{campus}/{building}/{unit}``, the device configuration file should be given
the name ``devices/{campus}/{building}/{unit}`` in the configuration store:

.. code-block:: bash

    vctl config store platform.driver devices/PNNL/Building1/AHU2 path/to/config/file.json

Each device configuration has the following form:

.. code-block:: json

    {
        "driver_config": {"device_address": "10.1.1.5",
                          "device_id": 500},
        "driver_type": "bacnet",
        "registry_config":"config://registry_configs/vav.csv",
        "interval": 60,
        "heart_beat_point": "heartbeat",
        "group": 0
    }

The following settings are required for all device configurations:

    - **driver_config** - Interface specific settings. See documentation for each interface type.
    - **driver_type** - Driver interface to use for this device: bacnet, modbus, fake, etc.
    - **registry_config** - Reference to a configuration file in the configuration store for points
      on the device. See the `Registry-Configuration-File`_ section below.

These settings are optional:

    - **interval** - Period (in seconds) on which to poll the device and publish the results. Defaults to 60 seconds.
    - **heart_beat_point** - A Point which to toggle to indicate a heartbeat to the device. A point with this ``Volttron
      Point Name`` must exist in the registry.  If this setting is missing the driver will not send a heart beat signal
      to the device.  Heart beats are triggered by the :ref:`Actuator Agent <Actuator-Agent>` which must be running to
      use this feature.
    - **group** - Group this device belongs to. (Defaults to 0)

Device Grouping
"""""""""""""""

Devices may be assigned to groups to separate them logically when they are polled. This is done by configuration of two
settings:

#. Each device configuration may have a `group` setting, which should be an integer greater than or equal to 0.
#. `group_offset_interval`, in the platform driver agent configuration is the number of seconds to delay the start of
each group from the previous group. When using this setting, assign devices only consecutive `group` values starting
from 0.

An independent polling schedule is created for each group, where the first is polled at `group_offset_interval` * `group`
seconds after the first devices of group 0. Each device within the group will then be polled `driver_scrape_interval`
seconds apart.

This is most commonly useful in two cases:

* To ensure that certain devices are polled in close proximity to each other, you can put them in their own
  group. They are then guaranteed to be polled `driver_scrape_interval` seconds apart.
* You may poll devices on different networks in parallel for performance.  For instance BACnet devices behind a single
  MSTP router need to be polled slowly and serially, but devices behind different routers may be polled in parallel.
  Grouping devices by router will do this automatically.


.. _Registry-Configuration-File:

Registry Configuration File
---------------------------
Registry configuration files setup each individual point on a device. Typically this file will be in CSV format, but the
exact format is driver specific.  See the section for a particular driver for the registry configuration format.

The following is a simple example of a Modbus registry configuration file:

.. csv-table:: Catalyst 371
    :header: Reference Point Name,Volttron Point Name,Units,Units Details,Modbus Register,Writable,Point Address,Default Value,Notes

    CO2Sensor,ReturnAirCO2,PPM,0.00-2000.00,>f,FALSE,1001,,CO2 Reading 0.00-2000.0 ppm
    CO2Stpt,ReturnAirCO2Stpt,PPM,1000.00 (default),>f,TRUE,1011,1000,Setpoint to enable demand control ventilation
    HeatCall2,HeatCall2,On / Off,on/off,BOOL,FALSE,1114,,Status indicator of heating stage 2 need


.. _Adding-Devices-To-Config-Store:

Adding Device Configurations to the Configuration Store
-------------------------------------------------------

Configurations are added to the Configuration Store using the command line:

.. code-block:: bash

    volttron-ctl config store platform.driver <name> <file name> <file type>

* **name** - The name used to refer to the file from the store.
* **file name** - A file containing the contents of the configuration.
* **file type** - ``--raw``, ``--json``, or ``--csv``. Indicates the type of the file. Defaults to ``--json``.

The main configuration must have the name ``config``

Device configuration but **not** registry configurations must have a name prefixed with ``devices/``.  Scripts that
automate the process will prefix registry configurations with ``registry_configs/``, but that is not a requirement for
registry files.

The name of the device's configuration in the store is used to create the topic used to reference the device. For
instance, a configuration named `devices/PNNL/ISB1/vav1` will publish scrape results to `devices/PNNL/ISB1/vav1` and
is accessible with the Actuator Agent via `PNNL/ISB1/vav1`.

The name of a registry configuration must match the name used to refer to it in the driver configuration.  The reference
is not case sensitive.

If the Platform Driver Agent is running, any changes to the configuration store will immediately affect the running devices
according to the changes.

Example
^^^^^^^

Consider the following three configuration files:  A platform driver configuration called `platform-driver.agent`, a
Modbus device configuration file called `modbus_driver.config` and corresponding Modbus registry configuration file called
`modbus_registry.csv`

To store the platform driver configuration run the command:

.. code-block:: bash

    volttron-ctl config store platform.driver config platform-driver.agent

To store the registry configuration run the command (note the ``--csv`` option):

.. code-block:: bash

    volttron-ctl config store platform.driver registry_configs/modbus_registry.csv modbus_registry.csv --csv

.. Note::

    The `registry_configs/modbus_registry.csv` argument in the above command must match the reference to the
    `registry_config` found in `modbus_driver.config`.

To store the driver configuration run the command:

.. code-block:: bash

    volttron-ctl config store platform.driver devices/my_campus/my_building/my_device modbus_config.config


Converting Old Style Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The new Platform Driver no longer supports the old style of device configuration.  The old `device_list` setting is
ignored.

To simplify updating to the new format, `scripts/update_platform_driver_config.py` is provided to automatically update to
the new configuration format.

With the platform running run:

.. code-block:: bash

    python scripts/update_platform_driver_config.py <old configuration> <output>

`old_configuration` is the main configuration file in the old format. The script automatically modifies the driver
files to create references to CSV files and adds the CSV files with the appropriate name.

`output` is the target output directory.

If the ``--keep-old`` switch is used, the old configurations in the output directory (if any) will not be deleted before
new configurations are created.  Matching names will still be overwritten.

The output from `scripts/update_platform_driver_config.py` can be automatically added to the configuration store
for the Platform Driver agent with `scripts/install_platform_driver_configs.py`.

Creating and naming configuration files in the form needed by `scripts/install_platform_driver_configs.py` can speed up
the process of changing and updating a large number of configurations. See the ``--help`` message for
`scripts/install_platform_driver_configs.py` for more details.


Device Scalability Settings
---------------------------

To improve the scalability of the platform, unneeded device state publishes for a device can be turned off.
All of the following setting are optional and will override the value set in the main platform driver configuration.

    - **publish_depth_first_all** - Enable "depth first" publish of all points to a single topic.
    - **publish_breadth_first_all** - Enable "breadth first" publish of all points to a single topic.
    - **publish_depth_first** - Enable "depth first" device state publishes for each point on the device.
    - **publish_breadth_first** - Enable "breadth first" device state publishes for each point on the device.

It is common practice to set `publish_breadth_first_all`, `publish_depth_first`, and
`publish_breadth_first` to `False` unless they are specifically needed by an agent running on
the platform.


.. note::

    All Historian Agents require `publish_depth_first_all` to be set to `True` in order to capture data.


Usage
=====

After installing the Platform Driver and loading driver configs into the config store, the installed drivers begin
polling and JSON-RPC endpoints become usable.


.. _Device-State-Publish:

Polling
-------

Once running, the Platform Driver will spawn drivers using the `driver_type` parameter of the
:ref:`driver configuration <Device-Configuration-File>` and periodically poll devices for all point data specified in
the :ref:`registry configuration <Registry-Configuration-File>` at the interval specified by the interval parameter
of the driver configuration.

By default, the value of each point on a device is published 4 different ways when the device state is published.
Consider the following settings in a driver configuration stored under the name ``devices/pnnl/isb1/vav1``:

.. code-block:: json

    {
        "driver_config": {"device_address": "10.1.1.5",
                          "device_id": 500},

        "driver_type": "bacnet",
        "registry_config":"config://registry_configs/vav.csv",
    }

In the `vav.csv` file, a point has the name `temperature`.  For these examples the current value of the
point on the device happens to be 75.2 and the meta data is

.. code-block:: json

    {"units": "F"}

When the driver publishes the device state the following two things will be published for this point:

    A "depth first" publish to the topic `devices/pnnl/isb1/vav1/temperature` with the following message:

        .. code-block:: python

            [75.2, {"units": "F"}]

    A "breadth first" publish to the topic `devices/temperature/vav1/isb1/pnnl` with the following message:

        .. code-block:: python

            [75.2, {"units": "F"}]

    These publishes can be turned off by setting `publish_depth_first` and `publish_breadth_first` to `false`
    respectively.

Also these two publishes happen once for all points:

    A "depth first" publish to the topic `devices/pnnl/isb1/vav1/all` with the following message:

        .. code-block:: python

            [{"temperature": 75.2, ...}, {"temperature":{"units": "F"}, ...}]

    A "breadth first" publish to the topic `devices/all/vav1/isb1/pnnl` with the following message:

        .. code-block:: python

            [{"temperature": 75.2, ...}, {"temperature":{"units": "F"}, ...}]

    These publishes can be turned off by setting `publish_depth_first_all` and `publish_breadth_first_all` to
    ``false`` respectively.


JSON-RPC Endpoints
------------------

**get_point** - Returns the value of specified device set point

    Parameters
        - **path** - device topic string (typical format is devices/campus/building/device)
        - **point_name** - name of device point from registry configuration file

**set_point** - Set value on specified device set point. If global override is condition is set, raise OverrideError
  exception.

    Parameters
        - **path** - device topic string (typical format is devices/campus/building/device)
        - **point_name** - name of device point from registry configuration file
        - **value** - desired value to set for point on device

    .. warning::

        It is not recommended to call the `set_point` method directly.  It is recommended to instead use the
        :ref:`Actuator <Actuator-Agent>` agent to set points on a device, using its scheduling capability.

**scrape_all** - Returns values for all set points on the specified device.

    Parameters
        - **path** - device topic string (typical format is devices/campus/building/device)

**get_multiple_points** - return values corresponding to multiple points on the same device

    Parameters
        - **path** - device topic string (typical format is devices/campus/building/device)
        - **point_names** - iterable of device point names from registry configuration file

**set_multiple_points** - Set values on multiple set points at once.  If global override is condition is set, raise
  OverrideError exception.

    Parameters
        - **path** - device topic string (typical format is devices/campus/building/device)
        - **point_names_value** - list of tuples consisting of (point_name, value) pairs for setting a series of
          points

**heart_beat** - Send a heartbeat/keep-alive signal to all devices configured for Platform Driver

**revert_point** - Revert the set point of a device to its default state/value.  If global override is condition is
  set, raise OverrideError exception.

    Parameters
        - **path** - device topic string (typical format is devices/campus/building/device)
        - **point_name** - name of device point from registry configuration file

**revert_device** - Revert all the set point values of the device to default state/values.  If global override is
  condition is set, raise OverrideError exception.

    Parameters
        - **path** - device topic string (typical format is devices/campus/building/device)

**set_override_on** - Turn on override condition on all the devices matching the specified pattern (
  :ref:`override docs <Platform-Driver-Override>`)

    Parameters
        - **pattern** - Override pattern to be applied. For example,
            - If pattern is `campus/building1/*` - Override condition is applied for all the devices under
              `campus/building1/`.
            - If pattern is `campus/building1/ahu1` - Override condition is applied for only `campus/building1/ahu1`
              The pattern matching is based on bash style filename matching semantics.
        - **duration** - Duration in seconds for the override condition to be set on the device (default 0.0,
          duration <= 0.0 imply indefinite duration)
        - **failsafe_revert** - Flag to indicate if all the devices falling under the override condition must to be
          set
          to its default state/value immediately.
        - **staggered_revert** -

**set_override_off** - Turn off override condition on all the devices matching the pattern.

    Parameters
        - **pattern** - device topic pattern for devices on which the override condition should be removed.

**get_override_devices** - Get a list of all the devices with override condition.

**clear_overrides** - Turn off override condition for all points on all devices.

**get_override_patterns** - Get a list of all override condition patterns currently set.


.. _Platform-Driver-Override:

Driver Override Condition
=========================

By default, every user is allowed write access to the devices by the platform driver.  The override feature will allow the
user (for example, building administrator) to override this default behavior and enable the user to lock the write
access on the devices for a specified duration of time or indefinitely.


Set Override On
---------------

The Platform Driver's ``set_override_on`` RPC method can be used to set the override condition for all drivers with topic
matching the provided pattern.  This can be specific devices, groups of devices, or even all configured devices.  The
pattern matching is based on bash style filename matching semantics.

Parameters:

     - pattern:  Override pattern to be applied. For example,
        * If the pattern is ``campus/building1/*`` the override condition is applied for all the devices under
          `campus/building1/`.
        * If the pattern is ``campus/building1/ahu1`` the override condition is applied for only the
          `campus/building1/ahu1` device. The pattern matching is based on bash style filename matching semantics.
     - duration:  Time duration for the override in seconds. If duration <= 0.0, it implies an indefinite duration.
     - failsafe_revert:  Flag to indicate if all the devices falling under the override condition has to be set to its
       default state/value immediately.
     - staggered_revert: If this flag is set, reverting of devices will be staggered.

Example ``set_override_on`` RPC call:

.. code-block:: python

    self.vip.rpc.call(PLATFORM_DRIVER, "set_override_on", <override pattern>, <override duration>)


Set Override Off
----------------

The override condition can also be toggled off based on a provided pattern using the Platform Driver's
``set_override_off`` RPC call.

Parameters:

     - pattern:  Override pattern to be applied. For example,
        * If the pattern is ``campus/building1/*`` the override condition is removed for all the devices under
          `campus/building1/`.
        * If the pattern is ``campus/building1/ahu1`` the override condition is removed for only for the
          `campus/building1/ahu1` device. The pattern matching is based on bash style filename matching semantics.

Example ``set_override_off`` RPC call:

.. code-block:: python

    self.vip.rpc.call(PLATFORM_DRIVER, "set_override_off", <override pattern>)


Get Override Devices
--------------------

A list of all overridden devices can be obtained with the Platform Driver's ``get_override_devices`` RPC call.

This method call has no additional parameters.

Example ``get_override_devices`` RPC call:

.. code-block:: python

    self.vip.rpc.call(PLATFORM_DRIVER, "get_override_devices")


Get Override Patterns
---------------------

A list of all patterns which have been requested for override can be obtained with the Platform Driver's
``get_override_patterns`` RPC call.

This method call has no additional parameters

Example "get_override_patterns" RPC call:

.. code-block:: python

    self.vip.rpc.call(PLATFORM_DRIVER, "get_override_patterns")


Clear Overrides
---------------

All overrides set by RPC calls described above can be toggled off at using a single ``clear_overrides`` RPC call.

This method call has no additional parameters

Example "clear_overrides" RPC call:

.. code-block:: python

    self.vip.rpc.call(PLATFORM_DRIVER, "clear_overrides")

For information on the global override feature specification, view the
:ref:`Global Override Specification <Global-Override-Specification>` doc.

.. toctree::

   global-override-specification
