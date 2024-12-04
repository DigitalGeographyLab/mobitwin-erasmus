# Erasmus+ student mobility flows on LAU and NUTS 3 levels across Europe from 2014 to 2022
Repository for scripts used to extract OD flows from Erasmus+ data in a data description article published in Scientific Data.


## Pre-requisites

### Data
1. Erasmus+ official mobility statistics (KA1) for each year between 2014–2022 from [Erasmus](https://erasmus-plus.ec.europa.eu/resources-and-tools/factsheets-statistics-evaluations/statistics/for-researchers?facets__permanent%7Cfield_eac_topics=1998).
2. Local Administrative Units (LAU) for each year between 2014–2022 from [GISCO](https://ec.europa.eu/eurostat/web/gisco/geodata/statistical-units/local-administrative-units).
3. NUTS regional layers for 2013, 2016, and 2021 from [GISCO](https://ec.europa.eu/eurostat/web/gisco/geodata/statistical-units/territorial-units-statistics).

### Python libraries
1. `pandas`
2. `geopandas`
3. `geopy`
4. `shapely`

## Order of running the scripts

| Step | File | Description | Input | Output |
| ---- | :----- | :---------- | :---- | :----- |
| 1 | [process_and_combine_erasmus_data.py](process_and_combine_erasmus_data.py) | Reads in the downloaded .xlsx files and combines them | Excel files from Erasmus | A CSV and a pickled dataframe |
| 2 | [geocode_erasmus.py](geocode_erasmus.py) | Geocodes the place names in Erasmus+ data | Pickled dataframe from step 1 | Geopackage of point locations representing origins and destinations of Erasmus+ data |
| 3 | [get_NUTS_LAU_codes_to_points.py](get_NUTS_LAU_codes_to_points.py) | Joins NUTS and LAU codes to geocoded placenames | Result geopackage from step 2 and the spatial layers | Geopackage of point locations with their associated regional codes on LAU and NUTS 3 levels |
| 4 | [connect_NUTS_LAU_OD.py](connect_NUTS_LAU_OD.py) | Connect geocoded data to original combined data across all spatial layers | Pickle from step 1, geopackage from step 3 | CSVs of mobilities |
| 4.5 | [connect_NUTS_LAU_OD_specific.py](connect_NUTS_LAU_OD_specific.py) | Connect geocoded data to original combined data for a specific spatial layer | Pickle from step 1, geopackage from step 3 | CSVs of mobilities |
| 5 | [sample_verification.py](sample_verification.py) | Gets the weighted random sample of 1000 for manual verification | Geopackage from step 4 | An Excel spreadsheet file |


## Citation

```
@article{Vaisanen2024,
  title = {Geolocated Erasmus+ student mobility in Europe: individual and spatially aggregate mobility flow data from 2014 to 2022},
  author = {Väisänen, Tuomas and Malekzadeh, Milad and Inkeröinen, Oula and Järv, Olle},
  year = {2024},
  journal = {Scientific Data},
  volume = {XXX},
  number = {YYY},
  pages = {ZZZZ},
  doi = {doi.number/doi.number}
}
```

## Links to Mobi-Twin project

* [Mobi-Twin project official webpage](https://mobi-twin-project.eu/)
* [Digital Geography Lab webpage](https://www.helsinki.fi/en/researchgroups/digital-geography-lab)
