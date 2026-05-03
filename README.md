# mars_code

Python analysis scripts for studying the Martian atmosphere using the
**OpenMARS** reanalysis dataset. The scripts produce diagnostics and figures
related to dust storms, zonal/meridional circulation, temperatures, and atmospheric optical depth.

---

## About the data: OpenMARS

[**OpenMARS**](https://ordo.open.ac.uk/collections/OpenMARS_database/4278950)
(*Open access to Mars Assimilated Reanalysis*) is a publicly available
reanalysis of the Martian atmosphere produced by the Open University.
It is built by **assimilating spacecraft observations** (primarily
temperature and dust retrievals from Mars Global Surveyor TES, Mars
Reconnaissance Orbiter MCS, and Mars Express) into the **UK Mars Global
Climate Model (UK-MGCM)**.

The output is a gridded, time-continuous, multi-Mars-Year record of the
state of the Martian atmosphere, including:

- 3-D temperature
- Zonal and meridional winds (`u`, `v`)
- Surface pressure
- Column dust optical depth
- Vertical levels in sigma / pressure coordinates
- Solar longitude (`Ls`) and Mars Year (`MY`) coordinates

Files are stored in **NetCDF** format, typically organized per Mars Year
(e.g. `my24/`, `my25/`, …, `my35/`).

In this project, OpenMARS data is read with `xarray` / `netCDF4` and the
scripts loop over Mars Years and Ls ranges to compute climatologies,
anomalies, wave statistics, and plots.

---

## Repository layout

Each script is a standalone analysis. Hard-coded paths near the top
(`data_folder`, `nc_folder`, `shapefile`, `out_folder`, …) should be
edited to match your local OpenMARS download and shapefile location.

### Dust analyses

| Script | What it does |
|---|---|
| `regional_dust.py` | Time series of regional column dust optical depth across defined Martian regions. |
| `hovmoller.py` | Hovmöller (longitude–time) plot of column dust optical depth. |
| `storm_source.py` | Map of column dust optical depth at the **source** stage of a global dust storm. |
| `peak_phase.py` | Map at the **peak phase** of a global dust storm. |
| `storm_propagation.py` | Map at the **propagation** stage of a global dust storm. |

The four map scripts overlay the **Mars geology shapefile** (see below).

### Circulation

| Script | What it does |
|---|---|
| `meridional_circulation_my25.py` | Meridional overturning streamfunction (Ψ = 2πχ) computed from `v` for Mars Year 25 over a chosen Ls window. |
| `meridional_circulation_my28.py` | Same diagnostic for Mars Year 28. |

### Zonal-mean diagnostics

| Script | What it does |
|---|---|
| `zonal-mean_temperature.py` | Pressure-vs-latitude contour plot of zonal-mean temperature. |
| `zonal_mean-wind.py` | Pressure-vs-latitude contour plot of zonal-mean zonal wind `u`. |

---

## Shapefile data

The `shapefiles/` folder contains the **USGS SIM 3292** *Global Geologic
Map of Mars* (Tanaka et al., 2014), used by the dust-storm map scripts
(`storm_source.py`, `peak_phase.py`, `storm_propagation.py`) to overlay
geological unit boundaries on top of the dust optical depth maps.

```
shapefiles/
├── SIM3292_Global_Geology.shp   # geometry (polygons of geologic units)
├── SIM3292_Global_Geology.shx   # spatial index
└── SIM3292_Global_Geology.dbf   # attribute table (unit names, ages, …)
```

A shapefile is a **set** of files that must stay together — `.shp`
alone is not readable. Loaded in Python with `geopandas`:

```python
import geopandas as gpd
geo = gpd.read_file("shapefiles/SIM3292_Global_Geology.shp")
print(geo.head())
```

> The scripts currently reference the shapefile via an absolute path
> (e.g. `/home/atmos/revaldo/MarsGeologyShapefile/SIM3292_Global_Geology.shp`).
> Update the `shapefile = "..."` line at the top of each script to
> `shapefile = "shapefiles/SIM3292_Global_Geology.shp"` after cloning.

**Source:** Tanaka, K. L., et al. (2014), *Geologic map of Mars*, U.S.
Geological Survey Scientific Investigations Map 3292, scale 1:20,000,000.
[https://pubs.usgs.gov/sim/3292/](https://pubs.usgs.gov/sim/3292/)

---

## Requirements

- **Python** ≥ 3.10
- A working install of **NetCDF** and **PROJ/GEOS** system libraries
  (needed by `netCDF4`, `cartopy`, `pyproj`, `shapely`, `geopandas`).

### Main Python libraries used

These are the packages directly imported by the scripts:

| Library | Purpose |
|---|---|
| `numpy` | numerical arrays |
| `pandas` | tabular data handling |
| `xarray` | labeled N-D arrays / NetCDF I/O |
| `netCDF4` | low-level NetCDF reading |
| `cftime` | Mars/360-day-style calendar handling |
| `dask` + `distributed` | out-of-core / parallel processing of large NetCDF files |
| `scipy` | filtering, FFT, statistics, signal processing |
| `matplotlib` | plotting |
| `cartopy` | map projections (polar, cylindrical) |
| `geopandas` + `shapely` + `pyproj` + `pyogrio` + `pyshp` | spatial / shapefile work |
| `pillow` | image export |
| `bokeh` | optional interactive plots |

The full pinned environment (including transitive dependencies) lives in
[`requirements.txt`](./requirements.txt).

### Install

It is recommended to use a virtual environment.

```bash
# clone
git clone git@github.com:rheonez/mars_code.git
cd mars_code

# create + activate venv
python3 -m venv mars_env
source mars_env/bin/activate

# install everything
pip install --upgrade pip
pip install -r requirements.txt
```

If `cartopy` / `pyproj` / `netCDF4` fail to build via pip, install the
system libraries first (Debian/Ubuntu):

```bash
sudo apt-get install libnetcdf-dev libhdf5-dev libproj-dev proj-data \
                     proj-bin libgeos-dev
```

On conda environments, the easier alternative is:

```bash
conda install -c conda-forge xarray netcdf4 cartopy geopandas dask scipy matplotlib
```

---

## Data setup

The scripts in this repo use OpenMARS NetCDF files for **MY25** and
**MY28**, organized per Mars Year:

```
/path/to/openmars/
├── my25/*.nc
└── my28/*.nc
```

Each script has a hard-coded `data_folder` / `nc_folder` near the top.
**Edit it to match the local OpenMARS download** before running. The
scripts read all `.nc` files in that folder with
`xarray.open_mfdataset(..., combine="by_coords")`.

---

## Running a script

Each script is standalone — just run it with Python:

```bash
python3 regional_dust.py
python3 hovmoller.py
python3 storm_source.py
python3 peak_phase.py
python3 storm_propagation.py
python3 meridional_circulation_my25.py
python3 meridional_circulation_my28.py
python3 zonal-mean_temperature.py
python3 zonal_mean-wind.py
```

Output figures (PNG) are written to the path defined inside each
script, typically a `plots/` folder.

---

## Notes

- Mars Year (MY) and Solar Longitude (Ls, 0–360°) are the natural time
  coordinates used throughout — calendar dates are not used.
- Some scripts assume specific Mars Years are present (e.g. MY25 or MY28);
  adjust the `MY` lists at the top if your local data covers a different
  range.
- Large NetCDF reads use `dask` chunking; you may need to tune chunk
  sizes for your available RAM.
