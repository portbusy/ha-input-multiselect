# Input Multiselect component for Home Assistant

This is a custom component for Home Assistant that introduces a new helper entity: `input_multiselect`. 

While the native `input_select` only allows you to pick a single option from a dropdown, this component lets you select multiple options simultaneously. It's perfect for scenarios like selecting which rooms a robot vacuum should clean, choosing multiple media players to group, or picking which days of the week an automation should run.

> **Note:** This component only handles the backend logic (creating the entities, storing the state, and exposing the actions). To actually interact with these entities via a proper UI dropdown with checkboxes on your Lovelace dashboard, you will also need the companion frontend card: **[Input Multiselect Card](https://github.com/portbusy/ha-input-multiselect-card)** *(replace with your actual link later)*.

## Installation

### HACS (Recommended)
The easiest way to install this is through [HACS](https://hacs.xyz/). 
Since it's not in the default store yet, you need to add it as a custom repository:

1. Go to HACS -> Integrations.
2. Click the three dots in the top right corner and select **Custom repositories**.
3. Paste the URL of this repository and select **Integration** as the category.
4. Click Add, then search for "Input Multiselect" and download it.
5. **Restart Home Assistant.**

### Manual
1. Download the `custom_components/input_multiselect` folder from this repository.
2. Copy it into your Home Assistant `custom_components` directory.
3. Restart Home Assistant.

## Configuration

Configuration is done entirely via the UI. YAML configuration is not supported.

1. Go to **Settings** -> **Devices & Services** -> **Integrations**.
2. Click **+ Add Integration** and search for "Input Multiselect".
3. Give your entity a name and provide the list of available options (either comma-separated or one per line).

You can edit the options at any time by clicking the **Configure** button on the integration page.

## How it works (States & Attributes)

Home Assistant has a strict 255-character limit for entity states. Storing an array of selected items directly in the state string can easily break this limit. 
To ensure stability, the entity works as follows:

* **State:** Displays the numeric count of currently selected items (e.g., `2 selected`).
* **Attributes:** Contains the actual data arrays.
    * `options`: The full list of available options you configured.
    * `selected_options`: An array containing only the currently checked items (e.g., `['Kitchen', 'Living Room']`).

When writing templates for your automations, you should read from the `selected_options` attribute.

## Available Actions

This integration exposes the following actions that you can call from your scripts and automations:

| Action | Description | Payload |
| :--- | :--- | :--- |
| `input_multiselect.set_options` | Overwrites the current selection entirely. | `options`: List of strings |
| `input_multiselect.add_options` | Adds new items to the existing selection. | `options`: List of strings |
| `input_multiselect.remove_options` | Removes specific items from the selection. | `options`: List of strings |

### Action Example

```yaml
action: input_multiselect.add_options
target:
  entity_id: input_multiselect.rooms_to_clean
data:
  options:
    - Kitchen
    - Hallway