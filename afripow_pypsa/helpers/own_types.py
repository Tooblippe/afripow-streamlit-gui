from typing import Tuple, List

import pypsa
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from pandas import DataFrame

FigAxDF = Tuple[Figure, Axes, DataFrame]

NetworkList = List[pypsa.Network]
