"""Mone's HVAC Climate."""

import json
import logging
from typing import Any

import voluptuous as vol

from homeassistant.components.climate import (
    ATTR_MAX_TEMP,
    ATTR_MIN_TEMP,
    ATTR_TARGET_TEMP_STEP,
    PLATFORM_SCHEMA,
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.const import (
    CONF_ICON_TEMPLATE,
    CONF_NAME,
    CONF_UNIQUE_ID,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_platform
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.template import Template
from homeassistant.helpers.template_entity import TemplateEntity
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

SERVICE_SET_SWINGH_MODE = "set_swingh_mode"
SERVICE_SET_JSON = "set_json"

# configurations
CONF_JSON_FORMAT = "json_format"
CONF_HVAC_MODE_LIST = "hvac_modes"
CONF_FAN_MODE_LIST = "fan_modes"
CONF_SWINGV_MODE_LIST = "swingv_modes"
CONF_SWINGH_MODE_LIST = "swingh_modes"
CONF_IR_IS_ONLINE_TEMPLATE = "ir_is_online_template"
CONF_CURRENT_TEMPERATURE_TEMPLATE = "current_temperature_template"
CONF_CURRENT_HUMIDITY_TEMPLATE = "current_humidity_template"


JSON_FORMAT_DEFAULT = """{"power":"$power","mode":"$hvac_mode","temp":$temperature,"fanspeed":"$fan_mode","swingv":"$swing_mode","swingh":"$swingh_mode","source":"$source"}"""

# HVAC_MODE
HVAC_MODE_OFF = HVACMode.OFF
HVAC_MODE_HEAT = HVACMode.HEAT
HVAC_MODE_DRY = HVACMode.DRY
HVAC_MODE_COOL = HVACMode.COOL
HVAC_MODE_AUTO = HVACMode.AUTO

"""Mitsubishi MSZxxNA fan mode for climate devices."""
FAN_MODE_AUTO = "Auto"
FAN_MODE_MIN = "Min"
FAN_MODE_LOW = "Low"
FAN_MODE_MEDIUM = "Medium"
FAN_MODE_HIGH = "High"
FAN_MODE_QUIET = "Quiet"

FAN_MODE_DEFAULT = FAN_MODE_AUTO

"""Mitsubishi MSZxxNA swing v modes for climate devices."""
SWINGV_MODE_AUTO = "Auto"
SWINGV_MODE_HIGHEST = "Highest"
SWINGV_MODE_HIGH = "High"
SWINGV_MODE_MIDDLE = "Middle"
SWINGV_MODE_LOW = "Low"
SWINGV_MODE_LOWEST = "Lowest"
SWINGV_MODE_SWING = "Swing"

SWINGV_MODE_DEFAULT = SWINGV_MODE_MIDDLE


"""Mitsubishi MSZxxNA swing h modes for climate devices."""
SWINGH_MODE_MAX_LEFT = "Max Left"
SWINGH_MODE_LEFT = "Left"
SWINGH_MODE_MIDDLE = "Middle"
SWINGH_MODE_RIGHT = "Right"
SWINGH_MODE_MAX_RIGHT = "Max Right"
SWINGH_MODE_WIDE = "Wide"

SWINGH_MODE_DEFAULT = SWINGH_MODE_MIDDLE

SOURCE_HASS = "HASS"
SOURCE_IRREMOTE = "IRRemote"
SOURCE_UNKNOWN = ""

ATTR_SWINGH_MODES = "swingh_modes"
ATTR_SWINGH_MODE = "swingh_mode"
ATTR_JSON = "json"
ATTR_JSON_FORMAT = "json_format"
ATTR_IR_IS_ONLINE = "ir_is_online"

_LOGGER = logging.getLogger(__name__)


DEFAULT_MAX_TEMP: float = 32
DEFAULT_MIN_TEMP: float = 16

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_NAME): cv.string,
        vol.Optional(CONF_UNIQUE_ID): cv.string,
        vol.Optional(ATTR_MAX_TEMP, default=DEFAULT_MAX_TEMP): cv.positive_float,
        vol.Optional(ATTR_MIN_TEMP, default=DEFAULT_MIN_TEMP): cv.positive_float,
        vol.Optional(ATTR_TARGET_TEMP_STEP, default=1.0): cv.positive_float,
        vol.Optional(CONF_JSON_FORMAT, default=JSON_FORMAT_DEFAULT): cv.string,
        vol.Optional(CONF_IR_IS_ONLINE_TEMPLATE): cv.template,
        vol.Optional(CONF_CURRENT_TEMPERATURE_TEMPLATE): cv.template,
        vol.Optional(CONF_CURRENT_HUMIDITY_TEMPLATE): cv.template,
        vol.Optional(
            CONF_HVAC_MODE_LIST,
            default=[
                HVACMode.OFF,
                HVACMode.HEAT,
                HVACMode.DRY,
                HVACMode.COOL,
                HVACMode.AUTO,
            ],
        ): cv.ensure_list,
        vol.Optional(
            CONF_FAN_MODE_LIST,
            default=[
                FAN_MODE_AUTO,
                FAN_MODE_MIN,
                FAN_MODE_LOW,
                FAN_MODE_MEDIUM,
                FAN_MODE_HIGH,
                FAN_MODE_QUIET,
            ],
        ): cv.ensure_list,
        vol.Optional(
            CONF_SWINGV_MODE_LIST,
            default=[
                SWINGV_MODE_AUTO,
                SWINGV_MODE_HIGHEST,
                SWINGV_MODE_HIGH,
                SWINGV_MODE_MIDDLE,
                SWINGV_MODE_LOW,
                SWINGV_MODE_LOWEST,
                SWINGV_MODE_SWING,
            ],
        ): cv.ensure_list,
        vol.Optional(
            CONF_SWINGH_MODE_LIST,
            default=[
                SWINGH_MODE_MAX_LEFT,
                SWINGH_MODE_LEFT,
                SWINGH_MODE_MIDDLE,
                SWINGH_MODE_RIGHT,
                SWINGH_MODE_MAX_RIGHT,
                SWINGH_MODE_WIDE,
            ],
        ): cv.ensure_list,
    }
)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the climate platform."""
    # Assign configuration variables.
    # The configuration check takes care they are present.

    async def _async_create_entities(
        hass: HomeAssistant, config: ConfigType
    ) -> list[MyClimate]:
        """Create the MyClimate."""
        entities = [MyClimate(hass, config)]

        # Add devices
        return entities

    async_add_entities(await _async_create_entities(hass, config))

    # Register services
    platform = entity_platform.async_get_current_platform()

    platform.async_register_entity_service(
        SERVICE_SET_SWINGH_MODE,
        {vol.Required(ATTR_SWINGH_MODE): cv.string},
        "async_set_swingh_mode",
        [ClimateEntityFeature.SWING_MODE],
    )
    platform.async_register_entity_service(
        SERVICE_SET_JSON,
        {vol.Required("new_json"): cv.string},
        "async_set_json",
    )


class MyClimate(TemplateEntity, ClimateEntity, RestoreEntity):
    """Representation of a custom climate device."""

    _mitsubishi_power: str | None
    _mitsubishi_hvac_mode: str | None

    _swingh_mode: str | None
    _swingh_modes: list[str] | None

    _ir_is_online: bool = False
    _ir_is_online_template: Template | None
    _current_temp_template: Template | None
    _current_humidity_template: Template | None

    _json_format: str | None
    _json: str | None

    def __init__(self, hass: HomeAssistant, config: ConfigType) -> None:
        """Initialize the climate device."""
        super().__init__(
            hass,
            icon_template=config.get(CONF_ICON_TEMPLATE),
            unique_id=config.get(CONF_UNIQUE_ID),
        )

        self._attr_max_temp = config.get(ATTR_MAX_TEMP) or DEFAULT_MAX_TEMP
        self._attr_min_temp = config.get(ATTR_MIN_TEMP) or DEFAULT_MIN_TEMP
        self._attr_target_temperature_step = config.get(ATTR_TARGET_TEMP_STEP)

        self._json_format = config.get(CONF_JSON_FORMAT)

        self._attr_has_entity_name = True
        self._attr_name = config[CONF_NAME]

        self._attr_unique_id = config.get(CONF_UNIQUE_ID)

        self._state = None

        self._attr_supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.FAN_MODE
            | ClimateEntityFeature.SWING_MODE
        )
        self._attr_target_temperature = 24

        # mitsubishi HVAC separate power(on/off) from hvac_mode.
        # we will convert hvac_mode to/from power and mitsubishi HVAC mode in this integration
        # _mitsubishi_hvac_mode is to back up the last hvac_mode when the HVAC was 'on'
        self._mitsubishi_power = HVAC_MODE_OFF
        self._mitsubishi_hvac_mode = HVAC_MODE_COOL
        self._attr_hvac_mode = HVAC_MODE_OFF
        self._attr_hvac_modes = config[CONF_HVAC_MODE_LIST]

        self._attr_fan_mode = FAN_MODE_DEFAULT
        self._attr_fan_modes = config.get(CONF_FAN_MODE_LIST)

        self._attr_swing_mode = SWINGV_MODE_DEFAULT
        self._attr_swing_modes = config.get(CONF_SWINGV_MODE_LIST)

        # mitsubbishi MSZ18NA supports SwingH mode but HASS doesn't
        # so it's stored as an extra attribute.
        self._swingh_mode = SWINGH_MODE_DEFAULT
        self._swingh_modes = config.get(CONF_SWINGH_MODE_LIST)

        self._ir_is_online = False
        # self._attr_current_temperature
        # self._attr_current_humidity
        self._ir_is_online_template = config.get(CONF_IR_IS_ONLINE_TEMPLATE)
        self._current_temp_template = config.get(CONF_CURRENT_TEMPERATURE_TEMPLATE)
        self._current_humidity_template = config.get(CONF_CURRENT_HUMIDITY_TEMPLATE)

        # build json
        self._json = None
        self.build_json(SOURCE_HASS)

    @property
    def should_poll(self) -> bool:
        """Switch needs polling."""
        return False

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return device specific state attributes."""
        return {
            ATTR_SWINGH_MODE: self._swingh_mode,
            ATTR_SWINGH_MODES: self._swingh_modes,
            ATTR_JSON: self._json,
            ATTR_JSON_FORMAT: self._json_format,
            ATTR_IR_IS_ONLINE: self._ir_is_online,
        }

    async def async_added_to_hass(self) -> None:
        """Register callbacks."""
        if self._ir_is_online_template:
            self.add_template_attribute(
                "_ir_is_online",
                self._ir_is_online_template,
                None,
                self._update_ir_is_online,
                none_on_template_error=True,
            )

        if self._current_temp_template:
            self.add_template_attribute(
                "_attr_current_temperature",
                self._current_temp_template,
                None,
                self._update_current_temp,
                none_on_template_error=True,
            )

        if self._current_humidity_template:
            self.add_template_attribute(
                "_attr_current_humidity",
                self._current_humidity_template,
                None,
                self._update_current_humidity,
                none_on_template_error=True,
            )

        await super().async_added_to_hass()

        # Restore to the last persisted states
        if state := await self.async_get_last_state():
            _LOGGER.debug("state=%s", state)
            last_json = state.attributes.get("json", None)
            if last_json is not None:
                self.parse_json(last_json)

    async def async_will_remove_from_hass(self) -> None:
        """Unregister callbacks."""

    @callback
    def _update_ir_is_online(self, result):
        if result not in (STATE_UNKNOWN, STATE_UNAVAILABLE):
            try:
                self._ir_is_online = bool(result)
            except ValueError:
                _LOGGER.error("Could not parse ir_is_online from %s", result)

    @callback
    def _update_current_temp(self, result):
        if result not in (STATE_UNKNOWN, STATE_UNAVAILABLE):
            try:
                self._attr_current_temperature = float(result)
            except ValueError:
                _LOGGER.error("Could not parse temperature from %s", result)

    @callback
    def _update_current_humidity(self, result):
        if result not in (STATE_UNKNOWN, STATE_UNAVAILABLE):
            try:
                self._attr_current_humidity = float(result)
            except ValueError:
                _LOGGER.error("Could not parse humidity from %s", result)

    @property
    def temperature_unit(self) -> str:
        """Return the unit of measurement."""
        return UnitOfTemperature.CELSIUS

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        self._attr_target_temperature = kwargs.get("temperature")
        self.build_json(SOURCE_HASS)
        self.async_write_ha_state()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new HVAC mode."""
        self._attr_hvac_mode = hvac_mode
        if hvac_mode == HVAC_MODE_OFF:
            self._mitsubishi_power = "Off"
        else:
            self._mitsubishi_power = "On"
            self._mitsubishi_hvac_mode = hvac_mode
        self.build_json(SOURCE_HASS)
        self.async_write_ha_state()

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set new fan mode."""
        self._attr_fan_mode = fan_mode
        self.build_json(SOURCE_HASS)
        self.async_write_ha_state()

    async def async_set_swing_mode(self, swing_mode: str) -> None:
        """Set new swingv mode."""
        self._attr_swing_mode = swing_mode
        self.build_json(SOURCE_HASS)
        self.async_write_ha_state()

    @property
    def swingh_mode(self) -> str | None:
        """Swingh mode for some mitsubishi HVAC system."""
        return self._swingh_mode

    async def async_set_swingh_mode(self, swingh_mode: str) -> None:
        """Set new target swingh operation."""
        # await self.hass.async_add_executor_job(self.set_swingh_mode, swingh_mode)
        self._swingh_mode = swingh_mode
        self.build_json(SOURCE_HASS)
        self.async_write_ha_state()

    @property
    def json_format(self) -> str:
        """Json text."""
        return self._json_format or JSON_FORMAT_DEFAULT

    @property
    def json(self) -> str | None:
        """Json text."""
        return self._json

    async def async_set_json(self, new_json: str) -> None:
        """Json text."""
        _LOGGER.debug("set_json=%s", new_json)

        if self.parse_json(new_json):
            self.async_write_ha_state()

    def parse_json(self, new_json) -> bool:
        """Parse new_json and update properties.

        Return true if the properties are changed
        otherwise false if no property is changed.

        Callers need to call self.async_write_ha_state() to persist the state
        with HASS.
        """
        try:
            if new_json is None or self._json == new_json:
                return False

            json_data = json.loads(new_json)

            self._mitsubishi_power = json_data.get("power", self._mitsubishi_power)
            self._mitsubishi_hvac_mode = json_data.get(
                "mode", self._mitsubishi_hvac_mode
            )
            if self._mitsubishi_power == "Off":
                self._attr_hvac_mode = HVAC_MODE_OFF
            else:
                self._attr_hvac_mode = self._mitsubishi_hvac_mode

            self._attr_target_temperature = json_data.get(
                "temp", self._attr_target_temperature
            )
            self._attr_fan_mode = json_data.get("fanspeed", self._attr_fan_mode)
            self._attr_swing_mode = json_data.get("swingv", self._attr_swing_mode)
            self._swingh_mode = json_data.get("swingh", self._swingh_mode)

            # if "source" is missing from the json string, assume it
            # is created from HASS.
            json_source = json_data.get("source", SOURCE_HASS)

            self.build_json(json_source)

            return True

        except json.JSONDecodeError as err:
            # log error message
            _LOGGER.error("JSONDecodeError: %s", err)
            return False

    def build_json(self, source: str) -> None:
        """Update the self._json with the current property values.

        Callers need to call self.async_write_ha_state() to persist the state
        with HASS.

        source: the source of the changes that triggers to rebuild the
                json string. e.g. HASS or IRRemote
        E.g.
        {
            "power": "On",
            "mode": "Auto",
            "temp": 25,
            "fanspeed": "Auto",
            "swingv": "Off",
            "swingh": "Right Max",
            "source": "HASS"
        }
        """
        # Write the new state to the JSON file
        # '{
        #       "power":"$power",
        #       "mode":"$hvac_mode",
        #       "temp":$temperature,
        #       "fanspeed":"$fan_mode",
        #       "swingv":"$swing_mode",
        #       "swingh":"$swingh_mode",
        #       "source":"$source"
        # }'
        json_str = (
            self.json_format.replace("$power", self._mitsubishi_power or "")
            .replace("$hvac_mode", self._mitsubishi_hvac_mode or "")
            .replace("$temperature", str(self._attr_target_temperature or ""))
            .replace("$fan_mode", self._attr_fan_mode or "")
            .replace("$swing_mode", self._attr_swing_mode or "")
            .replace("$swingh_mode", self._swingh_mode or "")
            .replace("$source", source or "")
        )

        self._json = json_str  # json.dumps(json_data)
