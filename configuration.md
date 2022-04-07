# Configuration

The program is configured completely using the configuration YAML file `config.yml`. An example file is included in the repository, but you will have to edit most of this to get the program to work properly with your data.

The configuration file has six main blocks; `folders`, `stations`, `time`, `weather`, `solar`, `tmy`.

## `folders` block
This block defines the input and output paths applied to all stations:

| Variable    | Description                                                   |
|-------------|---------------------------------------------------------------|
| `source`    | Source folder of input data. Each station must be in a subfolder with the station name |
| `destination-tmy` | Output filename of TMY files. Use {} as placeholder for stationname. File ending must be csv. |
| `destination-filtered`  | Output folder for filtered and gap filled input data. Generates subfolder with stationname for each station. |
| `pattern`    | regex pattern for searching for files in the source directory |

## `station` block
This contains information about the different stations in your dataset. Each station definition requires the following variables to be set:

| Variable    | Description                                                   |
|-------------|---------------------------------------------------------------|
| `latitude`  | Latitude of station                                           |
| `longitude` | Longitude of station                                          |
| `timezone`  | pytz timezone of station (must be one in [this list][ref1])   |
| `offset`    | fixed timezone offset (without daylight savings) in minutes   |

[ref1]: https://stackoverflow.com/questions/13866926/is-there-a-list-of-pytz-timezones

Here's an example of the definition of two different stations:

```yaml
stations:
  # Define a station called "Station 1"
  Station 1:
    latitude: -17.9475
    longitude: 122.2353
    timezone: Australia/Perth
	offset: 480
  # Define a station called "014015". Use quotes to force the string type
  "014015":
    latitude: -12.4239
    longitude: 130.8925
    timezone: Australia/Darwin
	offset: 570
```

## `time` block

This block contains information about how to extract timestamps from your data. OneTMY currently requires time data to be stored in separate columns (i.e. separate columns for year, month, day etc.). It supports multiple timestamps per observation (i.e. datasets that stamp both UTC and local time for every observation. All of this data needs to be in separate columns).

Here's an example on how to set up the time block for a dataset with two timestamp types:

```yaml
time:
  # First time format: UTC time
  utc:
    timezone: UTC
    file_format:
      year: YYYY-UTC
      month: MM-UTC
      day: DD-UTC
      hour: HH-UTC
      minute: MI-UTC
  # Second time format: local standard time (without DST)
  # Timezone set to the station's timezone using timezone=Station
  lst:
    timezone: Station
    file_format:
      year: YYYY-LST
      month: MM-LST
      day: DD-LST
      hour: HH-LST
      minute: MI-LST
```

## `weather` and `solar` blocks

Both of these blocks determine which observation columns from the source files are processed. Columns to be processed are selected using a key-value pair, with the key being the destination column and the value being the source column. This also allows you to rename columns.

For example, let's say we have a column labelled 'Air Temperature in degrees Celsius' that we wanted to put in the TMY. This is a really long column name, so let's assume we want to rename it as 'air-temp'. As this is weather data, the `weather` block would look like this:

```yaml
weather:
  air-temp: Air Temperature in degrees Celsius
```

As mentioned in [Measurement quality flags](data_requirements.md#measurement_quality_flags), the OneTMY pre-processor supports filtering of the measurements by **quality flags**. Flag columns need to be mapped to the same name as their observation column, with the added suffix `-flag`. If we were to add a quality flag column (called 'Quality of air temperature') to the example above, we would get the following `weather` block:

```yaml
weather:
  air-temp: Air Temperature in degrees Celsius
  air-temp-flag: Quality of air temperature
```

Some observation data is **required** (see [Required measurements](data_requirements.md#required_measurements)). Ensure that these columns are mapped in the `weather` and `solar` blocks accordingly.

## `tmy` block

Configure the variables and weighting for month selection for TMY generation.

```yaml
tmy:
  variables: ["mean-dni", "mean-ghi"]
  weighting: [0.75, 0.25]
  sort-by-windspeed: false
  sort-by-least-number-missing-days: true
```

sort-by-windspeed: Top three candidates will be sorted based on the smallest deviation in average monthly windspeed.

sort-by-least-number-missing-days: Ranking for best three candidates based on least number of days with gaps. This may override results from windspeed selection.

## Example `config.yml` file

An example configuration file is the one that ships with OneTMY aleady (click [here](src/config.yml)). It is set up for BoM observation data.

## Logging settings

OneTMY uses the Python `logging` library to log stuff to the console and files. This is configured using the configuration file `logconfig.yml`. Notes on how to configure the Python logger using a file can be found [here](https://docs.python.org/3/library/logging.config.html#logging-config-fileformat). Take a look at the default OneTMY [`logconfig.yml`](src/logconfig.yml)
