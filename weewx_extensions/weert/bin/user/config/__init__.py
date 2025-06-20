
from io import StringIO
import configobj


weert_defaults = """
[WeeRT]

    # The WeeRT server
    host = localhost
    port = 3000
    
    # Default username and password. Change these!
    user = weert
    password = weert

    # A unique name for the location of the stream
    platform = default_platform

    # A unique name within the platform for the stream
    stream = default_stream

    # The "measurement" name (this is an InfluxDB terminology).
    measurement = wxpackets
    
    # One try only
    max_tries = 1
    
    # Short timeout
    timeout = 2
    
    # Don't allow much of a backlog
    max_backlog = 2

    [[loop_filters]]
        # These items will be included in the post to the database.
        # The right-hand side can be any Python expression
        altimeter_pressure = altimeter
        console_voltage = consBatteryVoltage
        dewpoint_temperature = dewpoint
        extra1_humidity_percent = extraHumid1
        extra1_temperature = extraTemp1
        extra2_humidity_percent = extraHumid2
        extra2_temperature = extraTemp2
        extra3_temperature = extraTemp3
        gauge_pressure = pressure
        heatindex_temperature = heatindex
        in_humidity_percent = inHumidity
        in_temperature = inTemp
        in_temperature_battery_status = inTempBatteryStatus
        leaf1_temperature = leafTemp1
        leaf2_temperature = leafTemp2
        out_humidity_percent = outHumidity
        out_temperature = outTemp
        out_temperature_battery_status = outTempBatteryStatus
        radiation_radiation = radiation
        rain_battery_status = rainBatteryStatus
        rain_rain = rain
        sealevel_pressure = barometer
        soil1_temperature = soilTemp1
        soil2_temperature = soilTemp2
        soil3_temperature = soilTemp3
        soil4_temperature = soilTemp4
        unit_system = usUnits
        uv_uv = UV
        wind_dir = windDir
        wind_speed = windSpeed
        windchill_temperature = windchill
        x_wind_speed = windSpeed * math.cos(math.radians(90.0 - windDir)) if (windDir is not None and windSpeed is not None) else None
        y_wind_speed = windSpeed * math.sin(math.radians(90.0 - windDir)) if (windDir is not None and windSpeed is not None) else None
"""

config_defaults = configobj.ConfigObj(StringIO(weert_defaults))
