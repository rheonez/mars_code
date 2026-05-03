# Regional Dust Optical Depth over the Martian Regions 

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import glob
import os


# Directories
data_path = "/mnt/F2BAB6C1BAB681A1/mars/datasets/my25/*.nc"
save_path = "/mnt/F2BAB6C1BAB681A1/mars/plots/mars/regional_dust_MY25.png"


# Load dataset
files = sorted(glob.glob(data_path))
if len(files) == 0:
    raise FileNotFoundError(f"No files found at {data_path}")

ds = xr.open_mfdataset(files, combine='by_coords')

plt.rcParams["font.family"] = "serif"
Ls = ds["Ls"]
dust = ds["dustcol"]
lat = ds["lat"]
lon = ds["lon"]


# Define Region 
regions = {
    "Hellas Basin": {
        "lat_min": -56.42,  "lat_max": -27.86,
        "lon_min":  46.6,   "lon_max":  96.1
    },
    "Argyre Planitia": {
        "lat_min": -61.0,   "lat_max": -35.0,
        "lon_min": -62.0,   "lon_max": -27.0
    },
    "Utopia Planitia": {
        "lat_min":  30.0,   "lat_max":  65.0,
        "lon_min":  80.0,   "lon_max": 140.0
    },
    "Daedalia Planum": {
        "lat_min": -15.0,   "lat_max":   0.0,
        "lon_min": -145.0,  "lon_max": -125.0
    },
}


# Compute regional mean optical depth
region_series = {}

for name, info in regions.items():
    lat_min, lat_max = info["lat_min"], info["lat_max"]
    lon_min, lon_max = info["lon_min"], info["lon_max"]

    reg = dust.where(
        (lat >= lat_min) & (lat <= lat_max) &
        (lon >= lon_min) & (lon <= lon_max),
        drop=True
    )

    if reg.sizes.get("lat", 0) == 0 or reg.sizes.get("lon", 0) == 0:
        raise ValueError(f"Region {name} is empty — check bounds.")

    region_series[name] = reg.mean(dim=("lat", "lon"))


# Ls 
mask = ((Ls >= 160) & (Ls <= 350)).compute()
Ls_sel = Ls.where(mask, drop=True)

for name in region_series:
    region_series[name] = region_series[name].where(mask, drop=True)


# Plot
plt.figure(figsize=(12, 6))

styles = {
    "Hellas Basin":    {"lw": 0.5},
    "Argyre Planitia": {"lw": 0.5},
    "Utopia Planitia": {"lw": 0.5},
    "Daedalia Planum": {"lw": 0.5},
}

for name, series in region_series.items():
    plt.plot(Ls_sel.values, series.values,
             label=name, **styles.get(name, {}))

plt.ylim(0, 5.0)
plt.yticks(np.arange(0, 5.0, 1.0))
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)

plt.xlabel(r"$L_{s}$", fontsize=20)
plt.ylabel("Column Dust Optical Depth", fontsize=20)
#############
plt.title("Dust Over Regions (MY25) ", fontsize=25, pad = 10)

plt.grid(True, linestyle="--", alpha=0.35)
plt.legend(loc="upper right", fontsize=10, framealpha=0.9)
plt.margins(0)

os.makedirs(os.path.dirname(save_path), exist_ok=True)
plt.savefig(save_path, dpi=500, bbox_inches="tight")
plt.show()

print("Plot saved to:", save_path)
