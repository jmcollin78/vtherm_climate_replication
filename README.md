[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![hacs][hacs_badge]][hacs]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

<div> <br> </div>
<p align="center">
<img src="https://github.com/jmcollin78/versatile_thermostat/blob/main/images/icon.png" />
</p>

# VTherm Climate Replication

VTherm Climate Replication is a Home Assistant custom integration for [Versatile Thermostat](https://github.com/jmcollin78/versatile_thermostat).

It links a physical thermostat entity to a Versatile Thermostat climate entity and forwards the physical thermostat state changes to the target VTherm. The goal is to use a real thermostat as a physical remote control for a VTherm.

## What the integration does

For each configured pair, the integration listens to the selected physical climate entity and updates the selected Versatile Thermostat climate entity.

The integration currently replicates:

- HVAC mode
- Target temperature
- Preset mode when the target VTherm supports presets

Each replication entry also creates a switch entity. This switch can be used to temporarily disable replication without removing the configuration entry. When the switch is turned on again, the target VTherm is immediately resynchronized with the current state of the physical thermostat.

## Requirements

Before installing this integration, make sure that:

- Versatile Thermostat is already installed in Home Assistant
- the physical thermostat you want to mirror is available as a climate entity
- the target Versatile Thermostat is already created and available as a climate entity

## Installation

### Option 1: Install with HACS

1. Open HACS in Home Assistant.
2. Add this repository as a custom repository.
3. Select the Integration category.
4. Install VTherm Climate Replication.
5. Restart Home Assistant.

### Option 2: Manual installation

1. Copy the `custom_components/vtherm_climate_replication` folder into your Home Assistant `custom_components` directory.
2. Restart Home Assistant.

## Configuration

This integration is configured from the Home Assistant user interface. There is no YAML configuration.

1. Go to Settings > Devices & Services.
2. Select Add Integration.
3. Search for VTherm Climate Replication.
4. Choose the physical thermostat climate entity.
5. Choose the Versatile Thermostat climate entity to update.
6. Confirm the configuration.

The two selected climate entities must be different.

You can create multiple replication entries, but the same physical climate and target climate pair cannot be configured twice.

## How to use it

After the integration is configured:

- change the HVAC mode on the physical thermostat to update the VTherm
- change the target temperature on the physical thermostat to update the VTherm
- change the preset on the physical thermostat to update the VTherm when presets are supported
- use the replication switch entity to enable or disable forwarding at runtime

## Notes

- The integration adds a switch platform only.
- Replication is enabled by default when a configuration entry is created.
- Turning replication back on triggers a full state resynchronization from the physical thermostat to the target VTherm.

# Contributions are welcome!

If you wish to contribute, please read the [contribution guidelines](CONTRIBUTING.md).

# 🍻 Thanks for the beers 🍻
[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/jmcollin78)

***

[vtherm_climate_replication]: https://github.com/jmcollin78/vtherm_climate_replication
[buymecoffee]: https://www.buymeacoffee.com/jmcollin78
[buymecoffeebadge]: https://img.shields.io/badge/Buy%20me%20a%20beer-%245-orange?style=for-the-badge&logo=buy-me-a-beer
[commits-shield]: https://img.shields.io/github/commit-activity/y/jmcollin78/**versatile_thermostat**.svg?style=for-the-badge
[commits]: https://github.com/jmcollin78/vtherm_climate_replication/commits/master
[hacs]: https://github.com/custom-components/hacs
[hacs_badge]: https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/jmcollin78/vtherm_climate_replication.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Joakim%20Sørensen%20%40ludeeus-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/jmcollin78/vtherm_climate_replication.svg?style=for-the-badge
[releases]: https://github.com/jmcollin78/vtherm_climate_replication/releases
