"""
Plot pressure (Pa) vs latitude with temperature contours.
"""

import os
import glob
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

# Directories
data_folder = "/mnt/F2BAB6C1BAB681A1/mars/datasets/my28/"
output_folder = "/mnt/F2BAB6C1BAB681A1/mars/plots/mars/"
out_path = os.path.join(output_folder, "my28_temperature_decay.png")
os.makedirs(output_folder, exist_ok=True)

plt.rcParams["font.family"] = "serif"

# Load nc dataset
files = sorted(glob.glob(os.path.join(data_folder, "*.nc")))
ds = xr.open_mfdataset(files, combine="by_coords")

# Ls range
ls_min = 300
ls_max = 310

mask = (ds["Ls"] >= ls_min) & (ds["Ls"] <= ls_max)
mask = mask.compute()
indices = np.where(mask.values)[0]
print(f"Selected {len(indices)} timesteps for Ls = {ls_min}–{ls_max}")

ds_sel = ds.isel(time=indices)

# Pressure 3D array
lev = ds_sel["lev"]
ps_mean = ds_sel["ps"].mean(dim="lon")
lev_3d, ps_3d = xr.broadcast(lev, ps_mean)
pressure = lev_3d * ps_3d

# Temperature zonal mean
temp = ds_sel["temp"].mean(dim="lon")
temp_mean = temp.mean(dim="time")
p_mean = pressure.mean(dim="time")

lat = ds_sel["lat"].values
lev_vals = ds_sel["lev"].values

# Create 2D meshgrid
LAT, P = np.meshgrid(lat, lev_vals, indexing="xy")
t_plot = temp_mean.values
p_plot = p_mean.values

plt.figure(figsize=(12, 6))

# Filled contours
cf = plt.contourf(
    LAT,
    p_plot,
    t_plot,
    levels=np.linspace(110, 250, 29),
    cmap="RdYlBu_r",
    extend="both"
)

# Contour lines
cs = plt.contour(
    LAT,
    p_plot,
    t_plot,
    levels=np.arange(110, 260, 14),
    colors="k",
    linewidths=0.5
)
plt.clabel(cs, inline=1, fontsize=10, fmt="%.0f")

# Axes settings
ax = plt.gca()
ax.set_yscale("symlog", linthresh=1.0)
ax.invert_yaxis()
ax.set_ylim(800, 0)  

# Tick settings
yticks_pos = [800, 100, 10, 1, 0]
ytick_labels = ["800", "100", "10", "1", "0"]

ax.set_yticks(yticks_pos)
ax.set_yticklabels(ytick_labels)
ax.tick_params(axis="y", which="major", labelsize=15)
ax.tick_params(axis="x", which="major", labelsize=15)

# Latitude ticks
plt.xticks(
    np.arange(-90, 91, 30),
    [r"90°S", r"60°S", r"30°S", r"0°", r"30°N", r"60°N", r"90°N"]
)

plt.ylabel("Pressure (Pa)", fontsize=20)
plt.xlabel("Latitude", fontsize=20)
plt.title("Zonal Mean Temperature MY28 (decay)", fontsize=25, pad=10)
plt.grid(True, which="both", linestyle="--", alpha=0.4)

# Colorbar
cf.set_clim(110, 250)
cbar = plt.colorbar(cf, pad = 0.02, ticks = np.arange(110, 260, 20))
cbar.set_label("Temperature (K)", fontsize=20, labelpad=10)
cbar.ax.tick_params(labelsize=15)

# Save plot
plt.tight_layout()
plt.savefig(out_path, dpi=500)
plt.close()

print(f"Plot saved to: {out_path}")
