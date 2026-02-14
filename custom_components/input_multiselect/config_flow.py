"""Config flow setup for the Input Multiselect integration."""
from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import DOMAIN, CONF_OPTIONS

class InputMultiselectConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow for Input Multiselect via the HA UI."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial setup step triggered by the user."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Parse the raw input string into a sanitized list of options
            raw_options = user_input.get(CONF_OPTIONS, "")
            # Supports both comma-separated values and multiline inputs
            options_list = [
                opt.strip()
                for opt in raw_options.replace("\n", ",").split(",")
                if opt.strip()
            ]

            if not options_list:
                errors["base"] = "empty_options"
            else:
                user_input[CONF_OPTIONS] = options_list
                # Title becomes the entity name, data is persisted to the registry
                return self.async_create_entry(title=user_input["name"], data=user_input)

        # Build the schema using modern HA selectors for better UI rendering
        schema = vol.Schema(
            {
                vol.Required("name"): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
                ),
                vol.Optional("icon"): selector.IconSelector(),
                vol.Required(CONF_OPTIONS): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.TEXT,
                        multiline=True,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=schema, errors=errors
        )