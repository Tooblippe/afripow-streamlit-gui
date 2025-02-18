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

p_nom = m.variables["p_nom"]

reserve_sync = p_nom - p
reserve_per_snapshot = reserve_sync.sum(dim="Link")

m.add_constraints(reserve_per_snapshot >= 10000, name="Reserve_p_nom_min_p")
