"""
Plot zonal-mean zonal wind (u) vs latitude and pressure.
"""

import os
import glob
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from matplotlib.ticker import ScalarFormatter

# Directories
data_folder = "/mnt/F2BAB6C1BAB681A1/mars/datasets/my28/"
out_folder  = "/mnt/F2BAB6C1BAB681A1/mars/plots/mars/"
outfile = os.path.join(out_folder, "my28_wind_decay.png")
os.makedirs(out_folder, exist_ok=True)

# Load nc dataset
files = sorted(glob.glob(os.path.join(data_folder, "*.nc")))
ds = xr.open_mfdataset(files, combine="by_coords", engine="netcdf4", join="inner")

plt.rcParams["font.family"] = "serif"

# Ls selection
ls_min = 300
ls_max = 310

ls = ds["Ls"]
sel_time_mask = (ls >= ls_min) & (ls <= ls_max)

ds_sel = ds.sel(time=sel_time_mask)
print(f"Selected {int(sel_time_mask.sum())} time steps for Ls {ls_min}-{ls_max}")

# Zonal means
u_zonal = ds_sel["u"].mean(dim="lon")
ps_zonal = ds_sel["ps"].mean(dim="lon")

# Pressure 3D array
lev = ds_sel["lev"]
pressure_3d = lev * ps_zonal
u_mean = u_zonal.mean(dim="time")
pressure_mean = pressure_3d.mean(dim="time")

# Wind zonal mean  
lat = ds_sel["lat"].values
u_plot = u_mean.values
p_plot = pressure_mean.values
nlev, nlat = u_plot.shape
lat_2d = np.tile(lat.reshape(1, nlat), (nlev, 1))

fig, ax = plt.subplots(figsize=(12, 6))

# Colormap normalization
vmin, vmax = -200, 200
norm = TwoSlopeNorm(vmin=vmin, vcenter=0, vmax=vmax)
levels = np.linspace(vmin, vmax, 41)

# Filled contours
cf = ax.contourf(lat_2d, p_plot, u_plot,
                 levels=levels, cmap="RdBu_r",
                 norm=norm, extend="both")

# Contour lines
pos_levels = np.linspace(0, vmax, 11)
neg_levels = np.linspace(vmin, 0, 11)

pos_contours = ax.contour(lat_2d, p_plot, u_plot,
                          levels=pos_levels, colors="black",
                          linestyles="-", linewidths=0.6)
neg_contours = ax.contour(lat_2d, p_plot, u_plot,
                          levels=neg_levels, colors="black",
                          linestyles="--", linewidths=0.6)
ax.contour(lat_2d, p_plot, u_plot, levels=[0], colors="black", linewidths=1.0)

# Contour labels
ax.clabel(pos_contours, fmt="%d", inline=True, fontsize=10, colors="black")
ax.clabel(neg_contours, fmt="%d", inline=True, fontsize=10, colors="black")

# Axes settings
ax.set_yscale("symlog", linthresh=1.0)  
ax.invert_yaxis()                       
ax.set_ylim(800, 0)                     

plt.ylabel("Pressure (Pa)", fontsize=20)
plt.xlabel("Latitude", fontsize=20)
ax.set_title("Zonal-Mean Zonal Wind MY28 (decay)", fontsize=25, pad = 9)

# Latitude ticks
ax.set_xticks([-90, -60, -30, 0, 30, 60, 90])
ax.set_xticklabels(["90°S", "60°S", "30°S", "0", "30°N", "60°N", "90°N"])

# Pressure ticks
yticks = [800, 100, 10, 1, 0]
ax.set_yticks(yticks)
ax.set_yticklabels(["800", "100", "10", "1", "0"])
ax.tick_params(axis="y", which="both", direction="in", right=True, labelsize=15)
ax.tick_params(axis="x", which="both", direction="in", right=True, labelsize=15)

ax.grid(which="major", linestyle=":", linewidth=0.5, alpha=0.7)

# Colorbar
cbar = fig.colorbar(cf, ax=ax, orientation="vertical", pad=0.02)
cbar.set_label("Zonal Wind (m/s)", fontsize=20)
cbar.set_ticks(np.arange(-200, 201, 50))
cbar.ax.tick_params(labelsize=15)

# Save figure
plt.tight_layout()
plt.savefig(outfile, dpi=500)
plt.close(fig)

print(f"Figure saved to: {outfile}")
