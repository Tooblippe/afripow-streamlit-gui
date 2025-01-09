import pypsa


def is_solved_case(network: pypsa.Network):
    """this can be expanded but in its simplist form it looks
    in to links_t results if there is values for p0.
    it assumes that if there is values it is a solved network
    """
    return not network.links_t["p0"].empty
