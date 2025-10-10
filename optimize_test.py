from stolen import Context, Environment, CostMap, Trajectory
import numpy as np
from relaxation import Relaxation

context = Context()
env = Environment()
cost_map = CostMap()

cost_map.data = np.array(
    [
        [],
    ]
)


trajectory = Trajectory(np.array([[]]))

new_trajectory = Relaxation.relax(context, trajectory, cost_map)