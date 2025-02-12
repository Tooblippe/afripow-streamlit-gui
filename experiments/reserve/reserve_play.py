import pandas as pd
import xarray as xr

# Step 1: Get the snapshot (time index) from the PyPSA model
snapshots = (
    m.variables["Generator-p"].coords["snapshot"].to_index()
)  # Convert to Pandas Index
snapshots = pd.Index(snapshots, name="snapshot")  # Ensure it has a name

# Step 2: Get the generator index
generator_coords = pd.Index(
    network.generators.index, name="Generator"
)  # Ensure it has a name

# Step 3: Create the binary dispatching variable
dispatching = m.add_variables(
    name="Generator-Dispatching2",
    binary=True,
    coords=[snapshots, generator_coords],  # ✅ Correctly formatted coordinates
)

# Step 4: Get the generator dispatch variable
p_dispatch = m.variables["Generator-p"]  # The continuous power output variable

# Step 5: Use the generator's nominal capacity (`p_nom`) as an upper bound
p_nom_xr = xr.DataArray(
    network.generators.p_nom,
    dims=["Generator"],
    coords={"Generator": network.generators.index},
)

# Expand `p_nom` across the snapshot dimension
p_nom_expanded = p_nom_xr.expand_dims(snapshot=snapshots)

# 🔹 Constraint 1: If `p_dispatch > 0`, then `dispatching` must be 1
m.add_constraints(
    p_dispatch
    <= dispatching
    * p_nom_expanded,  # Use max possible dispatch (p_nom) instead of .max()
    name="Force_Dispatching_To_One_When_Dispatching",
)

# 🔹 Constraint 2: If `dispatching = 1`, then `p_dispatch` must be positive
m.add_constraints(
    p_dispatch
    >= 0.001 * dispatching,  # Small threshold to ensure `dispatching=1` when generating
    name="Ensure_Dispatching_One_If_Generating",
)
