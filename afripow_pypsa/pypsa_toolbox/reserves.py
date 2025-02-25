from pathlib import Path

import linopy
import pandas as pd
import pypsa


def add_spinning_reserves_per_level_and_area(
    m: linopy.model,
    network: pypsa.Network,
    reserve_level: str,
    area_link_list: dict,
    total_reserve_capacity_needed: float,
    constraint_name: str,
):
    """
    Source          :   https://pypsa.readthedocs.io/en/latest/examples/reserve-power.html#Limitations-and-other-approaches
    m               :   Linopy model

    network         :   Pypsa network

    reserve_level   :   'reserve_area_1' or 'reserve_level_2', ..., or 'reserve_level_6'

    area_link_list  :   {'reserve_area_1':
                                  {
                                  'non_extendable':
                                      {
                                       'links':
                                               ['Lk10_(B2-B1)', ...],
                                       'p_nom':
                                               [1500.0, ...]
                                      },
                                  'all_links':
                                              ['Lk10_(B2-B1)', 'Lk11_(B2-B1)', 'Lk12_(B2-B1)'],
                                  'extendable':
                                              ['Lk11_(B2-B1)', 'Lk12_(B2-B1)']}
                            }
    reserve_capacity_needed :   the value of the reserves obtained from the 'level_area'  the reserves.csv

    contstaint_name         :   reserve_level_reserve_area = f"{reserve_level}_{reserve_area}"
                                f"Reserve_Constraint_{reserve_level_reserve_area}_{reserve_capacity_needed}"
    """
    # read have in the file

    # Network elements selection
    snapshots = network.snapshots
    links_df = network.links.loc[area_link_list["all_links"]]
    reserve_links = links_df.index
    p_nom = links_df.p_nom

    # reserve levels per link the level for each the links in the list
    contributing_factor_per_link = links_df[reserve_level]

    # Variables selection
    P = m.variables["Link-p"].sel({"Link": area_link_list["all_links"]})

    # not used
    reserve_lower_limit_factor = 1

    """
    Add a new variable ReserveRequirement. It has a lower bound of zero, is defined for all snapshots and
    dispatchable generators.
    """
    ReserveRequirement = m.add_variables(
        lower=0,
        upper=p_nom,
        coords=[snapshots, reserve_links],
        name=f"Link-p_reserves-{constraint_name}",
    )

    """
    Next, we define a new constraint which ensures that for each snapshot 
    the total reserve requirement is satisfied by the sum of the reserve power provided by all generators.
    """
    TotalReserveCapacity = ReserveRequirement.sum("Link")
    ReserveSumConstraint = m.add_constraints(
        TotalReserveCapacity >= total_reserve_capacity_needed,
        name=f"GlobalReserveConstraint-sum_of_reserves-{constraint_name}",
    )

    """
    Now we need to limit the amount of reserve power that each generator can provide. 
    The following constraint ensures that the reserve power provided by a generator must be
    less than or equal to the difference between its power p and its nominal power p_nom:
    """
    ReserveUpperLimit = m.add_constraints(
        P + ReserveRequirement <= p_nom * contributing_factor_per_link,
        name=f"GlobalReserveConstraint-reserve_upper_limit-{constraint_name}",
    )

    """
    Finally, we add a constraint to ensure that the reserve power provided by a generator
    must be less than or equal to its actual power p multiplied by a scalar coefficient b. 
    """
    ReserveLowerLimit = m.add_constraints(
        # although we have ReserveRequirementVar <= 0, the variable itself was defined [0,inf]
        # this means that ReserveRequirementVar must be bigger than 0
        # this should set a spesific link ReserveVar to 0, since p was 0, thus not contributing to the reserve leve
        ReserveRequirement <= P * reserve_lower_limit_factor,
        name=f"GlobalReserveConstraint-reserve_lower_limit-{constraint_name}",
    )

    print("\n\n\nRESERVE VARIABLE")
    print(ReserveRequirement)
    print("\nSum of Links contraint")
    print(ReserveSumConstraint[0])
    print("\nP_nom minus P contraint")
    print(ReserveUpperLimit[0])
    print("\nP > 0 then Reserve=0 constraint")
    print(ReserveLowerLimit[0])


def add_all_reserve_constraints(
    network: pypsa.Network, m: linopy.model, reserves_file_path: str | Path
):
    """find all constraints from links.csv, and loads reserves.csv witht the RHS from Inputsfolder

    To set up, in the links.csv file:
    1. add a column called "reserve_area" and add the reserve areas to this column e.g - reserve_area_1, WesternCape, Gauteng. These names will be used in 'reserves.csv'.
    2. add columns called "reserve_level_1", "reserve_level_2", "reserve_level_n" and add the weightings e.g. 0.2, 0.3. These names will be used in 'reserves.csv'.

    links.csv
    reserve_area        reserve_level_1         reserve_level_2     .....
    ============        ===============         ===============     =====
    reserve_area_1      0.9                     0.1
    WesternCape         0                       0.7
    Gauteng             0.4                     0.2


    3. Create a 'reserves.csv' file and use the 'reserve_area' and 'reserve_level' names to build the file and column 'level_area'
    the level_area column should be 'reserve_level_name_reserve_area'. The 'value_mw' is the RHS of the constraint

    reserves.csv
    level_area                          value_mw
    ------------------------------      --------
    reserve_level_1_reserve_area_1      100
    reserve_level_1_WesternCape         30
    reserve_level_1_Gauteng             20



    3. Creates a dict
    find the links per area
    split the dict up into "extendable" and "non-extendable"
    {'reserve_area_1':
      {
      'non_extendable':
          {
           'links':
                   ['Lk10_(B2-B1)', ...],
           'p_nom':
                   [1500.0, ...]
          },
      'all_links':
                  ['Lk10_(B2-B1)', 'Lk11_(B2-B1)', 'Lk12_(B2-B1)'],
      'extendable':
                  ['Lk11_(B2-B1)', 'Lk12_(B2-B1)']}
    }
    """

    print("\n\nadd_all_reserve_constraints")
    print("===============================")
    # get all the network reserve areas defined in links.csv
    reserve_areas = network.links["reserve_area"].dropna()
    reserve_areas = reserve_areas[reserve_areas != 0]
    reserve_areas = reserve_areas[reserve_areas != "0"]
    reserve_areas = reserve_areas.unique()

    if reserve_areas == [0]:
        reserve_areas = []

    reserve_areas = [
        area for area in reserve_areas if "reserve_area" in area
    ]  # remove areas that does not contain "reserve area"
    print(f"Found the following areas: {reserve_areas}\n")

    # get the reserve level
    reserve_levels = [col for col in network.links.columns if "reserve_level_" in col]
    print(f"Found reserve levels: {reserve_levels}\n")

    area_to_links_lookup = {}
    for reserve_area in reserve_areas:
        area_to_links_lookup[reserve_area] = {}
        area_to_links_lookup[reserve_area]["non_extendable"] = {}
        area_to_links_lookup[reserve_area]["all_links"] = []
        links = network.links
        area_to_links_lookup[reserve_area]["all_links"] = links[
            (links["reserve_area"] == reserve_area)
        ].index.to_list()
        area_to_links_lookup[reserve_area]["extendable"] = links[
            (links["reserve_area"] == reserve_area)
            & (links["p_nom_extendable"] == True)
        ].index.to_list()
        area_to_links_lookup[reserve_area]["non_extendable"]["links"] = links[
            (links["reserve_area"] == reserve_area)
            & (links["p_nom_extendable"] == False)
        ].index.to_list()
        area_to_links_lookup[reserve_area]["non_extendable"]["p_nom"] = links[
            (links["reserve_area"] == reserve_area)
            & (links["p_nom_extendable"] == False)
        ].p_nom.to_list()
    print("The areas are associated  with the links:")
    print("\n")

    # read reserves RHS
    reserves = pd.read_csv(reserves_file_path, index_col=0)
    print(f"Reading RHS file from: {reserves_file_path}\n")
    print("Found RHS reserve constraints:")
    print(f"{reserves}\n")

    ignored_constraints = []

    # add constraints found
    for reserve_level in reserve_levels:
        for reserve_area in sorted(reserve_areas):
            reserve_level_reserve_area = f"{reserve_level}_{reserve_area}"
            area_link_list = area_to_links_lookup[reserve_area]

            try:
                reserve_capacity_needed = reserves.at[
                    reserve_level_reserve_area, "value_mw"
                ]
                constraint_name = (
                    f"-{reserve_level_reserve_area}_{reserve_capacity_needed}"
                )
                print(
                    f"Adding: {constraint_name}-{area_link_list} >= {reserve_capacity_needed}\n\n"
                )
                print("=" * 80)
                # add_reserve_constraint_per_level_and_area(
                #     m,
                #     network,
                #     reserve_level,
                #     area_link_list,
                #     reserve_capacity_needed,
                #     constraint_name,
                # )
                add_spinning_reserves_per_level_and_area(
                    m,
                    network,
                    reserve_level,
                    area_link_list,
                    reserve_capacity_needed,
                    constraint_name,
                )
            except KeyError:
                print(
                    f"{reserve_level} and {reserve_area} was not found in reserves.csv file. Skipping. Please check.\n"
                )
                ignored_constraints.append(reserve_level_reserve_area)

    print("Final Linopy Model for optimization:")
    print("Call: network.optimize.solve_model()")
    print("============================================================")
    print("The following constraints have been ADDED to the model:")
    added_constraints = [c for c in m.constraints if "GlobalReserveConstraint" in c]
    for i, constraint in enumerate(added_constraints):
        print(f"{i} ✅ -- {constraint}")
    print("============================================================")
    print("The following constraints have been SKIPPED:")
    for i, constraint in enumerate(ignored_constraints):
        print(f"{i} ❌ -- {constraint}")
    print("============================================================\n\n")
