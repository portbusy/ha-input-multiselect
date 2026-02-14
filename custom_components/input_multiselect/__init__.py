"""Core logic and entity setup for the Input Multiselect helper."""
import logging
from typing import Any
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.helpers.typing import ConfigType

from .const import (
    DOMAIN,
    CONF_OPTIONS,
    ATTR_OPTIONS,
    ATTR_SELECTED_OPTIONS,
    SERVICE_SET_OPTIONS,
    SERVICE_ADD_OPTIONS,
    SERVICE_REMOVE_OPTIONS,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Initialize the Input Multiselect component and register entity services."""
    component = EntityComponent(_LOGGER, DOMAIN, hass)
    hass.data[DOMAIN] = component

    component.async_register_entity_service(
        SERVICE_SET_OPTIONS,
        {vol.Required(CONF_OPTIONS): vol.All(cv.ensure_list, [cv.string])},
        "async_set_options",
    )

    component.async_register_entity_service(
        SERVICE_ADD_OPTIONS,
        {vol.Required(CONF_OPTIONS): vol.All(cv.ensure_list, [cv.string])},
        "async_add_options",
    )

    component.async_register_entity_service(
        SERVICE_REMOVE_OPTIONS,
        {vol.Required(CONF_OPTIONS): vol.All(cv.ensure_list, [cv.string])},
        "async_remove_options",
    )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Initialize a config entry instance generated from the UI."""
    component: EntityComponent = hass.data[DOMAIN]

    options = entry.options.get(CONF_OPTIONS, entry.data.get(CONF_OPTIONS, []))

    entity = InputMultiSelect(
        unique_id=entry.entry_id,
        name=entry.data["name"],
        options=options,
        icon=entry.data.get("icon"),
    )

    await component.async_add_entities([entity])

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the entity."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry from the integration UI."""
    component: EntityComponent = hass.data[DOMAIN]

    entity = next((ent for ent in component.entities if ent.unique_id == entry.entry_id), None)
    if entity:
        await component.async_remove_entity(entity.entity_id)

    return True


class InputMultiSelect(RestoreEntity):
    """State machine representation of the multiselect entity."""

    # We push state updates manually, polling is unnecessary
    _attr_should_poll = False

    def __init__(
            self, unique_id: str, name: str, options: list[str], icon: str | None
    ) -> None:
        """Initialize the instance with payload from the config entry."""
        self._attr_unique_id = unique_id
        self._attr_name = name
        self._attr_icon = icon
        self._options = options
        self._current_selection: list[str] = []

    @property
    def state(self) -> str:
        """Return the primary state.

        HA strictly limits state strings to 255 characters. 
        Returning the exact array could easily overflow this limit.
        We return the selection count, exposing the actual array via attributes.
        """
        return f"{len(self._current_selection)} selected"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Expose the full context mapping to the state machine attributes."""
        return {
            ATTR_OPTIONS: self._options,
            ATTR_SELECTED_OPTIONS: self._current_selection,
        }

    async def async_added_to_hass(self) -> None:
        """Restore state payload on core restart."""
        await super().async_added_to_hass()
        state = await self.async_get_last_state()

        if state and ATTR_SELECTED_OPTIONS in state.attributes:
            restored_selection = state.attributes[ATTR_SELECTED_OPTIONS]
            # Sanitize restored options against the current configured options
            self._current_selection = [
                opt for opt in restored_selection if opt in self._options
            ]

    async def async_set_options(self, options: list[str]) -> None:
        """Service callback: Override the entire selection array."""
        valid_options = [opt for opt in options if opt in self._options]
        self._current_selection = valid_options
        self.async_write_ha_state()

    async def async_add_options(self, options: list[str]) -> None:
        """Service callback: Append options to the existing array."""
        for opt in options:
            if opt in self._options and opt not in self._current_selection:
                self._current_selection.append(opt)
        self.async_write_ha_state()

    async def async_remove_options(self, options: list[str]) -> None:
        """Service callback: Drop specific options from the array."""
        for opt in options:
            if opt in self._current_selection:
                self._current_selection.remove(opt)
        self.async_write_ha_state()