"""Sensor platform for Gtasks."""
from homeassistant.helpers.entity import Entity
from .const import ATTRIBUTION, DEFAULT_NAME, DOMAIN_DATA, ICON, DOMAIN
from datetime import datetime, timedelta

async def async_setup_platform(
    hass, config, async_add_entities, discovery_info=None
):  # pylint: disable=unused-argument
    """Setup sensor platform."""
    async_add_entities([GtasksSensor(hass, discovery_info)], True)


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Setup sensor platform."""
    async_add_devices([GtasksSensor(hass, {})], True)


class GtasksSensor(Entity):
    """blueprint Sensor class."""

    def __init__(self, hass, config):
        self.hass = hass
        self.attr = {}
        self._state = None
        self._name = config.get("name", DEFAULT_NAME)

    async def async_update(self):
        """Update the sensor."""
        # Send update "signal" to the component
        await self.hass.data[DOMAIN_DATA]["client"].get_tasks()

        # Get new data (if any)
        task_list = self.hass.data[DOMAIN_DATA].get("tasks_list", None)

        # Check the data and update the value.
        data = {}
        if task_list is None:
            self._state = self._state
        else:
            for task in task_list:
                data[task.title] = task.due_date
            self._state = data

        # Set/update attributes
        self.attr["attribution"] = ATTRIBUTION
        #self.attr["time"] = str(updated.get("time"))
        #self.attr["none"] = updated.get("none")


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
    def device_state_attributes(self):
        """Return the state attributes."""
        return self.attr
