# mone_hvac

- [`mone\_hvac`](#mone_hvac)
  - [Climate Properties in configuration.yaml](#climate-properties-in-configurationyaml)
    - [name](#name)
    - [unique\_id](#unique_id)
    - [protocol](#protocol)
    - [ir\_is\_online\_template](#ir_is_online_template)
    - [current\_temperature\_template](#current_temperature_template)
    - [current\_humidity\_template](#current_humidity_template)
    - [hvac\_modes](#hvac_modes)
    - [fan\_modes](#fan_modes)
    - [swingv\_modes](#swingv_modes)
    - [swingh\_modes](#swingh_modes)
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

### protocol
Optional.<br/>
The protocol value in json file.  It provides a way to do versioning and forward and backward JSON compatibility. The default is "MSZ__NA".

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



## Examples

```yaml
climate:
  - platform: mone_hvac
    name: "Family Room HVAC"
    unique_id: "family_room_MSZ-GL18NA"
    ir_is_online_template: "{{ is_state('input_boolean.family_room_ir_is_online', 'on') }}"
    current_temperature_template: "{{ states('sensor.govee_thermometer_temperature') }}"
    current_humidity_template: "{{ states('sensor.govee_thermometer_humidity') }}"
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

