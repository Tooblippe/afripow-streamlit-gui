import linopy
import pypsa

network = pypsa.Network()
m = linopy.Model


# https://pypsa.readthedocs.io/en/latest/examples/reserve-power.html#Limitations-and-other-approaches


"""
We now add a new variable ReservePowerVar which represents the reserve power.
It has a lower bound of zero, is defined for all dispatchable generators and has a time index.
"""
links_subset = []  #
ReserveRequirement = 1234  # read have in the file
link_contributing_factor = 1  # list in same shape as links.p_nom
reserve_lower_limit = 1

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
ReserveUpperLimit = m.add_constraints(
    ReserveRequirementVar + m.variables["Link-p"]
    <= network.links.p_nom * link_contributing_factor,
    name="GlobalConstraint-reserve_upper_limit",
)

"""
Finally, we add a constraint to ensure that the reserve power provided by a generator
must be less than or equal to its actual power p multiplied by a scalar coefficient b. 
This coefficient can take any value between 0 and 1 and represents the technical availability of a generator to provide reserve power.
"""

ReserveLoweLimit = m.add_constraints(
    # although we have ReserveRequirementVar <= 0, the variable itself was defined [0,inf]
    # this means that ReserveRequirementVar must be bigger than 0
    # this should set a spesific link ReserveVar to 0, since p was 0, thus not contributing to the reserve leve
    ReserveRequirementVar <= reserve_lower_limit * m.variables["Link-p"],
    name="GlobalConstraint_reserve_lower_limit",
)

print("\n\n\nRESERVE VARIABLE")
print(ReserveRequirementVar)
print("\nSum of Links contraint")
print(ReserveSumConstraint[0])
print("\nP_nom minus P contraint")
print(ReserveUpperLimit[0])
print("\nP > 0 then Reserve=0 constraint")
print(ReserveLoweLimit[0])
