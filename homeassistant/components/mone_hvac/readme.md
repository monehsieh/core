# `mone_hvac`

- [`mone_hvac`](#mone_hvac)
  - [Climate Properties in configuration.yaml](#climate-properties-in-configurationyaml)
    - [name](#name)
    - [unique\_id](#unique_id)
    - [max\_temp](#max_temp)
    - [min\_temp](#min_temp)
    - [target\_temp\_step](#target_temp_step)
    - [ir\_is\_online\_template](#ir_is_online_template)
    - [current\_temperature\_template](#current_temperature_template)
    - [current\_humidity\_template](#current_humidity_template)
    - [hvac\_modes](#hvac_modes)
    - [fan\_modes](#fan_modes)
    - [swingv\_modes](#swingv_modes)
    - [swingh\_modes](#swingh_modes)
    - [json\_format](#json_format)
  - [Examples](#examples)
  - [Services](#services)
    - [set\_swingh\_mode](#set_swingh_mode)
    - [set\_json](#set_json)

## Climate Properties in configuration.yaml

### name
Required.<br/>
The name of the climate device

### unique_id
Optional.<br/>
The unique ID of the climate device

### max_temp
Optional.<br/>
default: 32

### min_temp
Optional.<br/>
default: 16

### target_temp_step
Optional.<br/>
default: 1

### ir_is_online_template
Optional.<br/>
A HASS template to provide the online/offline state of the IR control.  It will be exposed as a climate device attribute.  It can be from a MQTT topic value.

### current_temperature_template
Optional.<br/>
A HASS template to provide the current temperature. It will be exposed as a climate device attribute.  It can be the temperature reading from a bluetooth thermometer device.

### current_humidity_template
Optional.<br/>
A HASS template to provide the current humidity. It will be exposed as a climate device attribute.  It can be the humidity reading from a bluetooth thermometer device.

### hvac_modes
Optional.<br/>
The possibles values of the attribute "hvac_mode" (https://www.home-assistant.io/integrations/climate/).

The default is:

```yaml
    hvac_modes:
        - "off"
        - "heat"
        - "dry"
        - "cool"
        - "auto"
```

### fan_modes
Optional.<br/>
The possible values of the attribute "fan_mode" (https://www.home-assistant.io/integrations/climate/):
The default is:

```yaml
    fan_modes:
        - "Auto"
        - "Min"
        - "Low"
        - "Medium"
        - "High"
        - "Quiet"
```


### swingv_modes
Optional.<br/>
The possible values of the attribute "swing_mode" (https://www.home-assistant.io/integrations/climate/):
The default is:

```yaml
    fan_modes:
        - "Auto"
        - "Highest"
        - "High"
        - "Middle"
        - "Low"
        - "Lowest"
        - "Swing"
```

### swingh_modes
Optional.<br/>
The possible values of the custom attribute "swingh_mode":
The default is:

```yaml
    fan_modes:
        - "Max Left"
        - "Left"
        - "Middle"
        - "Right"
        - "Max Right"
        - "Wide"
```

### json_format
Optional.<br/>
The format of json used to create the json attribute.  $<attribute name> will be replaced with the real value.
The default is:

```yaml
    json_format: '{"power":"$power","mode":"$hvac_mode","temp":$temperature,"fanspeed":"$fan_mode","swingv":"$swing_mode","swingh":"$swingh_mode","source":"$source"}'
```




## Examples

```yaml
climate:
  - platform: mone_hvac
    name: "Family Room HVAC"
    unique_id: "family_room_MSZ-GL18NA"
    ir_is_online_template: "{{ is_state('input_boolean.family_room_ir_is_online', 'on') }}"
    current_temperature_template: "{{ states('sensor.govee_thermometer_temperature') }}"
    current_humidity_template: "{{ states('sensor.govee_thermometer_humidity') }}"
    json_format: '{"power":"$power","mode":"$hvac_mode","temp":$temperature,"fanspeed":"$fan_mode","swingv":"$swing_mode","swingh":"$swingh_mode","source":"$source"}'
```


## Services

### set_swingh_mode

    Set the horizontal swing mode

```yaml
target:
  entity_id: <entity id>
data:
  swingh_mode: <swingh mode>
```


### set_json

    Set the json text attribute

```yaml
target:
  entity_id: <entity id>
data:
  new_json: <json string>
```

