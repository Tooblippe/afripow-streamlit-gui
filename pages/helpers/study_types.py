from afripow_pypsa.toolbox.toolbox import (
    run_unconstrained_expansion,
    run_optimum_expansion,
    run_incremental_demand_expansion,
)

STUDY_TYPES = {
    "1. Unconstrained Expansion": {
        "input": "Inputs",
        "output": "Results_uc",
        "function": run_unconstrained_expansion,
        "doc": "1) Adding Hydro Efficiency, 2) Fix Battery Capacity, 3) Add reserve constraints",
    },
    "2. Optimum Expansion": {
        "input": "Results_uc",
        "output": "Results_opt",
        "function": run_optimum_expansion,
        "doc": "Add documentation for Optimum Expansion",
    },
    "3. Incremental Demand Expansion": {
        "input": "Results_opt",
        "output": "Results_opti",
        "function": run_incremental_demand_expansion,
        "doc": "Add documentation for Incremental Demand Expansion",
    },
    # "4. Excess Energy Optimisation": {
    #     "input": "Results_opt",
    #     "output": "Results_opti",
    #     "function": excess_energy_optimisation,
    #     "doc": "Optimise Excess Energy",
    # },
}
