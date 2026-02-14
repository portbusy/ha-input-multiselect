"""Config flow setup for the Input Multiselect integration."""
from typing import Any
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import DOMAIN, CONF_OPTIONS

class InputMultiselectConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flow for Input Multiselect via the HA UI."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial setup step triggered by the user."""
        errors: dict[str, str] = {}

        if user_input is not None:
            raw_options = user_input.get(CONF_OPTIONS, "")
            options_list = [
                opt.strip()
                for opt in raw_options.replace("\n", ",").split(",")
                if opt.strip()
            ]

            if not options_list:
                errors["base"] = "empty_options"
            else:
                user_input[CONF_OPTIONS] = options_list
                return self.async_create_entry(title=user_input["name"], data=user_input)

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

    from homeassistant.core import callback

    @staticmethod
    @callback
    def async_get_options_flow(
            config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return InputMultiselectOptionsFlowHandler()


class InputMultiselectOptionsFlowHandler(config_entries.OptionsFlow):
    """Handles the options flow for Input Multiselect via the HA UI."""

    async def async_step_init(
            self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handles options window."""
        if user_input is not None:
            raw_options = user_input.get(CONF_OPTIONS, "")
            options_list = [
                opt.strip()
                for opt in raw_options.replace("\n", ",").split(",")
                if opt.strip()
            ]
            # Salva le nuove opzioni
            return self.async_create_entry(title="", data={CONF_OPTIONS: options_list})

        # Recupera le opzioni attuali per mostrarle precompilate
        current_options = self.config_entry.options.get(
            CONF_OPTIONS, self.config_entry.data.get(CONF_OPTIONS, [])
        )
        current_options_str = ",\n".join(current_options)

        schema = vol.Schema(
            {
                vol.Required(CONF_OPTIONS, default=current_options_str): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.TEXT,
                        multiline=True,
                    )
                ),
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)