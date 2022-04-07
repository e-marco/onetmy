# OneTMY
A minute-based Typical Meteorological Year (TMY) generator for observations from ground-based weather stations. Written in Python and based on the following paper:

> Marco Ernst, Jack Gooday, *Methodology for generating high time resolution typical meteorological year data for accurate photovoltaic energy yield modelling*, Solar Energy, Volume 189, 2019, Pages 299-306, ISSN 0038-092X, <https://doi.org/10.1016/j.solener.2019.07.069>.

Please reference this publication when mentioning this program or creating derivative works from it.

OneTMY consists of two parts; a highly-customisable pre-processor for cleaning and filling missing data, and a TMY generator. The TMY generator can be used by itself if you have the data set up correctly.

The system has only been tested on minutely solar and weather data from the Australian Bureau of Meteorology.

Found a bug? Create an issue! Contributions always welcome.

To get started, take a look at these:
1. [Data Requirements](data_requirements.md)
2. [Installing OneTMY](installing.md)
3. [Configuration](configuration.md)

Once you've done that, generating the TMY is as simple as:

```bash
# onetmy/src/
python onetmy.py
```
