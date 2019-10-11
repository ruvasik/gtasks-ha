"""
Component to integrate with gtasks.

For more details about this component, please refer to
https://github.com/BlueBlueBlob/gtasks
"""
import os
from datetime import timedelta
import logging
import voluptuous as vol
from homeassistant import config_entries
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers import discovery
from homeassistant.util import Throttle
from homeassistant.core import callback

import keyring.backend
from keyrings.alt.file import PlaintextKeyring
from gtasks2 import Gtasks

from integrationhelper.const import CC_STARTUP_VERSION

from .const import (
    CONF_BINARY_SENSOR,
    CONF_NAME,
    CONF_SENSOR,
    DEFAULT_NAME,
    DOMAIN_DATA,
    DOMAIN,
    ISSUE_URL,
    PLATFORMS,
    REQUIRED_FILES,
    VERSION,
    CONF_CREDENTIALS_LOCATION,
    CONF_DEFAULT_LIST,
    ATTR_TASK_TITLE,
    ATTR_DUE_DATE,
    ATTR_LIST_TITLE,
    SERVICE_NEW_TASK,
    SERVICE_NEW_LIST,
    SERVICE_COMPLETE_TASK,
)

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=30)

_LOGGER = logging.getLogger(__name__)

BINARY_SENSOR_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)

SENSOR_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)

NEW_TASK_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_TASK_TITLE): cv.string,
        vol.Optional(ATTR_DUE_DATE): cv.datetime,
        vol.Optional(ATTR_LIST_TITLE): cv.string,
    }
)

NEW_LIST_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_LIST_TITLE): cv.string,
    }
)

COMPLETE_TASK_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_TASK_TITLE): cv.string,
        vol.Optional(ATTR_LIST_TITLE): cv.string,
    }
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_CREDENTIALS_LOCATION): cv.string,
                vol.Optional(CONF_DEFAULT_LIST, default=None): cv.string,
                vol.Optional(CONF_BINARY_SENSOR): vol.All(
                    cv.ensure_list, [BINARY_SENSOR_SCHEMA]
                ),
                vol.Optional(CONF_SENSOR): vol.All(cv.ensure_list, [SENSOR_SCHEMA]),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass, config):
    """Set up this component using YAML."""
    
    if config.get(DOMAIN) is None:
        # We get her if the integration is set up using config flow
        return True

    # Print startup message

    # Check that all required files are present
    file_check = await check_files(hass)
    if not file_check:
        return False

    # Create DATA dict
    hass.data[DOMAIN_DATA] = {}

    # Get "global" configuration.
    creds = config[DOMAIN].get(CONF_CREDENTIALS_LOCATION)
    default_list = config[DOMAIN].get(CONF_DEFAULT_LIST)
    hass.data[DOMAIN_DATA]["default_list"] = default_list
    # Configure the client.
    try:
        kr = PlaintextKeyring()
        keyring.set_keyring(kr)
        _LOGGER.info('keyring : {}'.format(kr))
        gtasks_obj = Gtasks(open_browser=False, credentials_location=creds, two_steps=True)
        hass.data[DOMAIN_DATA]["auth_url"] = gtasks_obj.auth_url()
        hass.data[DOMAIN_DATA]["gtasks_obj"] = gtasks_obj
    except Exception as e:
        _LOGGER.exception(e)
        return False

    return True



async def async_setup_entry(hass, config_entry):
    """Set up this integration using UI."""
    _LOGGER.info("init init")
    
    conf = hass.data.get(DOMAIN_DATA)
    #if config_entry.source == config_entries.SOURCE_IMPORT:
        #if conf is None:
            #hass.async_create_task(
                #hass.config_entries.async_remove(config_entry.entry_id)
            #)
        #return False

    # Print startup message
    _LOGGER.info(
        CC_STARTUP_VERSION.format(name=DOMAIN, version=VERSION, issue_link=ISSUE_URL)
    )

    # Create DATA dict
    #hass.data[DOMAIN_DATA] = {}

    # Get "global" configuration.
    
    _LOGGER.info('data {}'.format(hass.data[DOMAIN_DATA]))

    # Configure the client.
    g = hass.data[DOMAIN_DATA]["gtasks_obj"]
    default_list = hass.data[DOMAIN_DATA]["default_list"]
    hass.data[DOMAIN_DATA]["client"] = GtasksData(hass,g, default_list)
    _LOGGER.info('{}'.format(g))
    # Add binary_sensor
    #hass.async_add_job(
        #hass.config_entries.async_forward_entry_setup(config_entry, "binary_sensor")
    #)

    # Add sensor
    hass.async_add_job(
        hass.config_entries.async_forward_entry_setup(config_entry, "sensor")
    )

    @callback
    def new_task(call):
        title = call.data.get(ATTR_TASK_TITLE)
        due_date = call.data.get(ATTR_DUE_DATE, None)
        task_list = call.data.get(ATTR_LIST_TITLE, default_list)
        try:
            g.new_task(title = title, due_date = due_date, task_list = task_list)
        except Exception as e:
            _LOGGER.exception(e)
            
    @callback
    def new_list(call):
        new_task_list = call.data.get(ATTR_LIST_TITLE)
        try:
            g.new_list(title = new_task_list)
        except Exception as e:
            _LOGGER.exception(e)
            
    @callback
    def complete_task(call):
        task_to_complete = call.data.get(ATTR_TASK_TITLE)
        task_list = call.data.get(ATTR_LIST_TITLE, default_list)
        try:
            list = g.get_list(task_list)
            for t in list:
                if t.title == task_to_complete:
                    t.complete = True
                    break
        except Exception as e:
            _LOGGER.exception(e)
        
    #Register "new_task" service
    hass.services.async_register(
        DOMAIN, SERVICE_NEW_TASK, new_task, schema=NEW_TASK_SCHEMA
    )
    
    #Register "new_list" service
    hass.services.async_register(
        DOMAIN, SERVICE_NEW_LIST, new_list, schema=NEW_LIST_SCHEMA
    )
    
    #Register "comple_task" service
    hass.services.async_register(
        DOMAIN, SERVICE_COMPLETE_TASK, complete_task, schema=COMPLETE_TASK_SCHEMA
    )
    
    return True


class GtasksData:
    """This class handle communication and stores the data."""

    def __init__(self, hass, gtasks, default_list):
        """Initialize the class."""
        self.hass = hass
        self.gtasks = gtasks
        self.default_list = default_list

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def get_tasks(self):
        """Update data."""
        # This is where the main logic to update platform data goes.
        
        try:
            if self.default_list is None:
                tasks_list = await self.hass.async_add_executor_job(self.gtasks.get_list)
            else:
                tasks_list = await self.hass.async_add_executor_job(self.gtasks.get_list, self.default_list)
            self.hass.data[DOMAIN_DATA]["tasks_list"] = tasks_list
        except Exception as e:
            _LOGGER.exception(e)

async def check_files(hass):
    """Return bool that indicates if all files are present."""
    # Verify that the user downloaded all files.
    base = f"{hass.config.path()}/custom_components/{DOMAIN}/"
    missing = []
    for file in REQUIRED_FILES:
        fullpath = "{}{}".format(base, file)
        if not os.path.exists(fullpath):
            missing.append(file)

    if missing:
        _LOGGER.critical("The following files are missing: %s", str(missing))
        returnvalue = False
    else:
        returnvalue = True

    return returnvalue


async def async_remove_entry(hass, config_entry):
    """Handle removal of an entry."""
    try:
        await hass.config_entries.async_forward_entry_unload(
            config_entry, "binary_sensor"
        )
        _LOGGER.info(
            "Successfully removed binary_sensor from the gtasks integration"
        )
    except ValueError:
        pass

    try:
        await hass.config_entries.async_forward_entry_unload(config_entry, "sensor")
        _LOGGER.info("Successfully removed sensor from the gtasks integration")
    except ValueError:
        pass
