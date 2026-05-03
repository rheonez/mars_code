"""
Meridional Overturning Streamfunction (Ψ = 2πχ) | MY28
"""

import os
import glob
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from scipy.integrate import cumtrapz
from matplotlib.colors import TwoSlopeNorm
import dask

# Directories
data_folder = "/mnt/F2BAB6C1BAB681A1/mars/datasets/my28/"
out_folder  = "/mnt/F2BAB6C1BAB681A1/mars/plots/mars/"
os.makedirs(out_folder, exist_ok=True)

plt.rcParams["font.family"] = "serif"

# Physical constants
a_mars = 3.3895e6
g_mars = 3.71

dask.config.set({"array.slicing.split_large_chunks": True})

# Load nc files
nc_files = sorted(glob.glob(os.path.join(data_folder, "*.nc")))

def _preprocess(ds):
    return ds[["Ls", "v", "ps", "lev", "lat", "lon", "time"]]

ds = xr.open_mfdataset(
    nc_files,
    combine="by_coords",
    preprocess=_preprocess,
    chunks={"time": 5, "lev": 5, "lat": 18, "lon": 36},
    engine="netcdf4",
)

# Set Ls range
mask = ((ds["Ls"] >= 290) & (ds["Ls"] <= 320)).compute()
ds_sel = ds.sel(time=ds.time[mask]).load()

# Compute Means
v_zm  = ds_sel["v"].mean(dim="lon")
ps_zm = ds_sel["ps"].mean(dim="lon")
lev   = ds_sel["lev"]
lat   = ds_sel["lat"].values

ps_expanded = ps_zm.expand_dims({"lev": lev}, axis=1)
pressure = (ps_expanded * lev).transpose("time", "lev", "lat")

v_mean = v_zm.mean(dim="time")
p_mean = pressure.mean(dim="time")

# χ computation
v_rev = v_mean[::-1, :]
p_rev = p_mean[::-1, :]

chi_rev = cumtrapz(y=v_rev.values, x=p_rev.values, axis=0, initial=0.0)
coslat  = np.cos(np.deg2rad(lat))
chi_rev_phys = chi_rev * (a_mars * coslat / g_mars)[np.newaxis, :]
chi = chi_rev_phys[::-1, :]

# Ψ computation
psi = 2.0 * np.pi * chi
psi_Sv = psi / 1e9

# Plotting arrays
X = np.tile(lat[np.newaxis, :], (p_mean.shape[0], 1))
Y = p_mean.values
Z = psi_Sv

fig, ax = plt.subplots(figsize=(10, 6))

# Setting cbar limits
vmin = -1
vmax = 13
vcenter = 0

norm = TwoSlopeNorm(vmin=vmin, vcenter=vcenter, vmax=vmax)

base_ticks = np.linspace(vmin, vmax, 8)
if 0 not in np.round(base_ticks, 6):
    cbar_ticks = np.sort(np.append(base_ticks, 0))
else:
    cbar_ticks = base_ticks

# Contour levels
levels = np.linspace(vmin, vmax, 41)

cf = ax.contourf(
    X, Y, Z,
    levels=levels,
    cmap="RdBu_r",
    norm=norm,
    extend="both"
)

# Y-axis
ax.invert_yaxis()
ax.set_ylim(900, 0)
ax.set_yticks(np.arange(900, -1, -100))
plt.yticks(fontsize=16)
ax.set_ylabel("Pressure (Pa)", fontsize=20)

# X-axis
ax.set_xlim(-90, 90)
ax.set_xticks(np.arange(-90, 91, 30))
ax.set_xticklabels(["90°S", "60°S", "30°S", "0°", "30°N", "60°N", "90°N"], fontsize=16)
ax.set_xlabel("Latitude", fontsize=20)

ax.set_title("Meridional Overturning Streamfunction MY28 (decay)", fontsize=20)

# Colorbar
cbar = plt.colorbar(cf, ax=ax, pad=0.02, ticks=cbar_ticks)
cbar.set_label("10⁹ kg s⁻¹", fontsize=20)
cbar.ax.set_yticklabels([f"{t:.0f}" for t in cbar_ticks], fontsize=16)

plt.tight_layout()

# Save figure
outfile = os.path.join(out_folder, "meridional_overturning_MY28_decay.png")
plt.savefig(outfile, dpi=500)
plt.close(fig)

print(f"Saved: {outfile}")
