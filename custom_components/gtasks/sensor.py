"""Sensor platform for Gtasks."""
import logging
from datetime import datetime
from uuid import getnode as get_mac
from homeassistant.helpers.entity import Entity

from .const import (
    ATTRIBUTION,
    DEFAULT_NAME,
    DOMAIN_DATA,
    ICON,
    DOMAIN,
    SENSOR_UNIT_OF_MEASUREMENT,
    CONF_SENSOR,
)


_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass, config, async_add_entities, discovery_info=None
):  # pylint: disable=unused-argument
    """Setup sensor platform."""
    async_add_entities([GtasksSensor(hass, discovery_info)], True)


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Setup sensor platform."""
    tasks_lists = hass.data[DOMAIN_DATA]["tasks_lists"]
    for task_list in tasks_lists:
        async_add_devices([GtasksSensor(hass, {}, task_list)], True)


def helper_task(task_list, data):
    """Gets incomplete tasks."""
    for task in task_list:
        jtask = {}
        jtask["task_title"] = f'{task.title}'
        jtask["due_date"] = f'{task.due_date}'
        if not task.complete:
            data.append(jtask)
    return data


class GtasksSensor(Entity):
    """blueprint Sensor class."""

    def __init__(self, hass, config, list_name):
        self.hass = hass
        self.attr = {}
        self._state = 0
        self._list = list_name
        self._name = f'{config.get("name", DEFAULT_NAME)}_{self._list}'
        self._unique_id = f'{get_mac()}-{CONF_SENSOR}-{self._name}'

    async def async_update(self):
        """Update the sensor."""
        # Send update "signal" to the component
        await self.hass.data[DOMAIN_DATA]["client"].update_data(self._list)

        # Get new data (if any)
        task_list = self.hass.data[DOMAIN_DATA].get(self._list + CONF_SENSOR + "_data", None)
        data = {}
        # Check the data and update the value.
        if task_list is None:
            self._state = 0
        else:
            self._state = len(task_list)
            parent_tasks = []
            child_tasks = []
            for task in task_list:
                if task.get('parent', None):
                    child_tasks.append(task)
                else:
                    parent_tasks.append(task)

            # Add parents
            for task in parent_tasks:
                jtask = {}
                jtask["task_title"] = f'{task["title"]}'
                jtask["id"] = f'{task["id"]}'
                jtask["children"] = []
                if 'due' in task:
                    jtask["due_date"] = datetime.strftime(
                                            datetime.strptime(task['due'],
                                            '%Y-%m-%dT00:00:00.000Z').date(),
                                            '%Y-%m-%d'
                                            )
                    jtask["due_time"] = datetime.strftime(
                                            datetime.strptime(task['due'],
                                            '%Y-%m-%dT00:00:00.000Z').date(),
                                            '%H:%M:%S'
                                            )
                    jtask["due"] = task['due']
                data[jtask['id']] = jtask

            # Add children
            for task in child_tasks:
                if data.get(task['parent'], None):
                    jtask = {}
                    jtask["task_title"] = f'{task["title"]}'
                    if 'due' in task:
                        jtask["due_date"] = datetime.strftime(
                                                datetime.strptime(task['due'],
                                                '%Y-%m-%dT00:00:00.000Z').date(),
                                                '%Y-%m-%d'
                                                )
                        jtask["due_time"] = datetime.strftime(
                                                datetime.strptime(task['due'],
                                                '%Y-%m-%dT00:00:00.000Z').date(),
                                                '%H:%M:%S'
                                                )
                        jtask["due"] = task['due']
                    data[task['parent']]['children'].append(jtask)
                else:
                    # No Parent? maybe a deeper level for now only first level
                    pass

            # Sort children
            data = list(data.values())
            for task in data:
                if len(task['children']) > 0:
                    task['children'].sort(key=self.sort_child)

        # Set/update attributes
        self.attr["attribution"] = ATTRIBUTION
        self.attr["tasks"] = data

    def sort_child(self, x):
        if not x.get('due_date', None):
            return '9999'
        return x['due_date']

    @property
    def unique_id(self):
        """Return a unique ID to use for this sensor."""
        return self._unique_id

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.unique_id)},
            "name": self.name,
            "manufacturer": "Gtasks",
        }

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return ICON

    @property
    def unit_of_measurement(self):
        return SENSOR_UNIT_OF_MEASUREMENT

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self.attr
