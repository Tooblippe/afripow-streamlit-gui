# https://pypsa.readthedocs.io/en/latest/examples/reserve-power.html#Limitations-and-other-approaches

"""
We now add a new variable ReservePowerVar which represents the reserve power.
It has a lower bound of zero, is defined for all dispatchable generators and has a time index.
"""
ReserveRequirementVar = m.add_variables(
    lower=0,
    upper=network.links.p_nom,
    coords=[network.snapshots, network.links.index],
    name="Link-p_reserves",
)

"""
Next, we define a new constraint which ensures that for each snapshot 
the total reserve requirement is satisfied by the sum of the reserve power provided by all generators.
"""
ReserveRequirement = 10
ReserveSumConstraint = m.add_constraints(
    ReserveRequirementVar.sum("Link") >= ReserveRequirement,
    name="GlobalConstraint-sum_of_reserves",
)

"""
Now we need to limit the amount of reserve power that each generator can provide. 
The following constraint ensures that the reserve power provided by a generator must be
less than or equal to the difference between its power p and its nominal power p_nom:

Set a variable to the size of p_nom lower and upper to fix
-n_reserve.model.variables["Generator-p"] + a * n_reserve.generators["p_nom"]
# or do m.variables["Link-p_nom"]
"""
reserve_upper_limit = 1
m.add_variables(
    upper=network.links.p_nom,
    lower=network.links.p_nom,
    coords=[network.snapshots, network.links],
    name="Link-p_nom_reserve",
)
ReserveUpperLimit = m.add_constraints(
    ReserveRequirementVar
    <= reserve_upper_limit * m.variables["Link-p_nom_reserve"] - m.variables["Link-p"],
    name="Link-reserve_upper_limit",
)

"""
Finally, we add a constraint to ensure that the reserve power provided by a generator
must be less than or equal to its actual power p multiplied by a scalar coefficient b. 
This coefficient can take any value between 0 and 1 and represents the technical availability of a generator to provide reserve power.
"""
reserve_lower_limit = 0.7
ReserveLoweLimit = m.add_constraints(
    ReserveRequirementVar <= reserve_lower_limit * m.variables["Link-p"],
    name="Link-reserve_lower_limit",
)
