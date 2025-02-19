import pypsa

# Create a new network
n = pypsa.examples.ac_dc_meshed(from_master=True)

m = n.optimize.create_model()


# Add the p_nom as a scalar
# -------------------------
import xarray as xr

p = m.variables["Link-p"]

m.add_variables(
    network.links.p_nom,
    network.links.p_nom,
    coords=[network.snapshots, network.links],
    name="p_nom",
)

m.add_variables(
    network.links.p_nom_opt,
    network.links.p_nom_opt,
    coords=[network.snapshots, network.links],
    name="p_nom_opt",
)

p_nom = m.variables["p_nom"]
p_nom_opt = m.variables["p_nom_opt"]

reserve_sync = p_nom - p


reserve_per_snapshot = reserve_sync.sum(dim="Link")

m.add_constraints(reserve_per_snapshot >= 10000, name="Reserve_p_nom_min_p")


(p_nom - p).where(xr.DataArray(p >= 1, coords=p.coords, dims=p.dims)).sum(dim="Link")
(p_nom_opt - p).where(xr.DataArray(p >= 1, coords=p.coords, dims=p.dims)).sum(
    dim="Link"
)

# mmmmmm
(p - 1).sum(dim="Link") >= 0

 mask = xr.DataArray((p - 1) >= 0, coords=p.coords, dims=p.dims, name="p_on_filter")

p.where(mask, other=xr.DataArray(False, coords=p.coords, dims=p.dims))

def c(p):
    return p>=1

p.where(c)
