# Data Requirements

Ground-based minutely weather and solar observation data is required. It would not take much work to modify the program to work with data recorded at different frequencies, however the theory has been developed on minutely-based data.

## File format

The program is currently set up to read `.csv` files, however it can read any type of file that the Python [`pandas`](https://pandas.pydata.org/) package can, if you change Pandas import method in `load.load`.

## Required measurements

Some measurements are required by the theory to generate the TMY. The columns from your data need to be renamed correctly using the pre-processor (see [here](configuration.md#weather_and_solar_blocks)). Here's a list of the required columns and what to rename them to:

| Measurement                  | Type    | Pre-processor converted name |
|------------------------------|---------|------------------------------|
| Global horizontal irradiance | Solar   | mean-ghi                     |
| Direct normal irradiance     | Solar   | mean-dni                     |
| Direct horizontal irradiance | Solar   | mean-dhi                     |
| Air temperature              | Weather | air-temp                     |
| Relative humidity            | Weather | relative-humidity            |
| Wind speed                   | Weather | wind-speed                   |

## Required timestamping

In addition to the required measurements listed above, particular timestamp data is required. Multiple timestamps for each observation are supported, and they all need to follow the same rules.

-   Each timestamp needs separate columns for year, months, day, hour and minute
-   These columns need to be numerical (i.e. use '03' instead of 'March')
-   Each timestamp needs to be defined properly in the [time block](configuration.md#time_block)

> The BoM dataset has the same column names for the year/month/day etc. columns for each timestamp, which is not allowed. The script `convert_date_headers.py` has been setup to rename them if needed.

## Available and missing data

As described in the theory, the TMY generator will not process datasets that don't have enough data to pick from. It also won't process datasets that have too much missing data. Here are the requirements:

-   Data from 10 years for each calendar month must be present
-   No more than 30% of each column of data can be empty
-   No more than 10% of data must be missing after 'logical filling' (see `fill.fill`)

## Measurement quality flags

The OneTMY pre-processor supports filtering of the measurements by quality flags. The program is currently set up to ignore all data that has been flagged anything but 'Y' (quality assured). To change this functionality to work for your flags, modify `flagtools.map`.
