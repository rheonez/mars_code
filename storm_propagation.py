"""
Shows the storm propagation 
"""

import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import geopandas as gpd
import numpy as np
from matplotlib.ticker import MaxNLocator, ScalarFormatter
from mpl_toolkits.axes_grid1 import make_axes_locatable
import os
from glob import glob

# Directories
nc_folder = "/mnt/F2BAB6C1BAB681A1/mars/datasets/my28"
shapefile = "/home/atmos/revaldo/MarsGeologyShapefile/SIM3292_Global_Geology.shp"
output_plot = "/mnt/F2BAB6C1BAB681A1/mars/plots/mars/MY28_source.png"

plt.rcParams["font.family"] = "Serif"

# Ls
LS_TARGET = 267.31
LS_TOLERANCE = 0.05

# Load dataset
nc_files = sorted(glob(os.path.join(nc_folder, "*.nc")))
ds_all = xr.open_mfdataset(nc_files, combine="by_coords")

optical_depth = ds_all["dustcol"]
lats = ds_all["lat"]
lons = ds_all["lon"]

# Select nearest Ls
selected_Ls = None
try:
    ds_by_ls = ds_all.set_coords("Ls").swap_dims({"time": "Ls"})
    snap = ds_by_ls.sel(Ls=LS_TARGET, method="nearest", tolerance=LS_TOLERANCE)
    od_at_ls = snap["dustcol"]
    selected_Ls = float(snap["Ls"].values)
except Exception:
    ls_values_np = ds_all["Ls"].compute().values
    idx = int(np.abs(ls_values_np - LS_TARGET).argmin())
    od_at_ls = optical_depth.isel(time=idx)
    selected_Ls = float(ls_values_np[idx])

mars_shape = gpd.read_file(shapefile)

# Plotting
fig = plt.figure(figsize=(16, 9.0667), dpi=500)
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_global()

# Gridlines
gl = ax.gridlines(draw_labels=False, linewidth=0.6, color='gray', alpha=0.5, linestyle='--')

# Ticks
xticks = np.arange(-180, 181, 60)
yticks = np.arange(-90, 91, 30)
ax.set_xticks(xticks, crs=ccrs.PlateCarree())
ax.set_yticks(yticks, crs=ccrs.PlateCarree())

ax.set_xticklabels([f"{x}°" for x in xticks], fontsize=20)
ax.set_yticklabels([f"{y}°" for y in yticks], fontsize=20)

# Map boundaries
mars_shape.boundary.plot(ax=ax, edgecolor='black', linewidth=0.2, transform=ccrs.PlateCarree())

# Plotting
mesh = ax.pcolormesh(
    lons, lats, od_at_ls,
    cmap='OrRd',
    vmin=0, vmax=2.5,
    alpha=0.8,
    transform=ccrs.PlateCarree()
)

# Colorbar
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="3%", pad=0.12, axes_class=plt.Axes)
cbar = plt.colorbar(mesh, cax=cax)
cbar.set_label("Column Dust Optical Depth (τ)", fontsize=25, labelpad=15)
cbar.locator = MaxNLocator(nbins=6)
cbar.ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=False, useOffset=False))
cbar.ax.tick_params(labelsize=20)
cbar.update_ticks()

# Labels
ax.set_xlabel("Longitude", fontsize=25, labelpad=15)
ax.set_ylabel("Latitude", fontsize=25, labelpad=15)

ax.set_title(f"Dust Propagation (MY28)• Ls = {LS_TARGET}°", fontsize=30, pad=10)

# Saving Figure
plt.tight_layout()
plt.savefig(output_plot, dpi=500, bbox_inches='tight')

print(f"Optical depth map at Ls≈{selected_Ls:.2f}° saved as: {output_plot}")
