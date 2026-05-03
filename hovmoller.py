# Hovmöller plot to show the evolution of dust with time

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import glob
import os

# Directories
input_folder = "/mnt/F2BAB6C1BAB681A1/mars/datasets/my28/"
output_folder = "/mnt/F2BAB6C1BAB681A1/mars/plots/mars/"
os.makedirs(output_folder, exist_ok=True)


# Load all NetCDF files
files = sorted(glob.glob(os.path.join(input_folder, "*.nc")))
ds = xr.open_mfdataset(files, combine='by_coords')

# Set the font family
plt.rcParams["font.family"] = "serif"


# Select Ls range and latitude range
ds_sel = ds.sel(time=(ds["Ls"] >= 266) & (ds["Ls"] <= 275))
lat_sel = ds_sel.sel(lat=slice(-35, -50))


# Mean optical depth over latitude
dust_mean_lat = lat_sel["dustcol"].mean(dim="lat")

# Coordinates
Ls_vals = ds_sel["Ls"].values
lon_vals = ds["lon"].values
dust_vals = dust_mean_lat.values 


# Hovmöller Plot 
plt.figure(figsize=(12, 6))

plt.pcolormesh(
    lon_vals,
    Ls_vals,
    dust_vals,
    cmap="OrRd",
    shading="gouraud",   
    vmin=0,
    vmax=2.5,
)

# Colorbar
cbar = plt.colorbar(pad = 0.02)
cbar.set_label("Column Dust Optical Depth (τ)", fontsize = 20, labelpad=15)
cbar.ax.tick_params(labelsize=16)

plt.xlabel("Longitude", fontsize = 20, labelpad = 15)
plt.ylabel(r'Solar Longitude ($L_{s}$)', fontsize = 20, labelpad=15)
plt.title("Hovmöller Plot: MY28", fontsize = 20, pad = 10)
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)


# Mark Ls ticks
ls_ticks = np.arange(266 , 275, 1)
plt.yticks(ls_ticks)

# Add horizontal lines 
for val in ls_ticks:
    plt.axhline(val, color='white', alpha=0.25, linewidth=0.6)

# Limits
plt.xlim(lon_vals.min(), lon_vals.max())
plt.ylim(Ls_vals.min(), Ls_vals.max())

# Save
outfile = os.path.join(output_folder, "hovmoller_MY28.png")
plt.savefig(outfile, dpi=500, bbox_inches="tight")
plt.close()

print("Saved Hovmöller plot to:", outfile)
