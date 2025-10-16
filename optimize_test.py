from stolen import Context, Environment, CostMap, Trajectory
import numpy as np
import re
import random
from relaxation import Relaxation
from splines import SplineInterpolation
import matplotlib.pyplot as plt
from matplotlib import colors

COSTMAP_FILE = "costmap.txt"
PATH_FILE = "path_history.txt"

context = Context()
env = Environment()
cost_map = CostMap()


with open(COSTMAP_FILE) as f:
   f.readline()
   g = [l.strip() for l in f.readlines()[:-1]]
   
grid = []
for l in g:
    # print(re.split(r'[\[\] ,]+', l)[1:-1])
    arr = list(map(lambda v: 240 if v=='3' else 0, re.split(r'[\[\] ,]+', l)[1:-1]))
    # print(arr)
    grid.append(arr)
cost_map.data = np.array(grid)

with open(PATH_FILE) as f:
    # print(re.split(r'[\[\] ,\(\)]+', f.readline().strip())[1:-1])
    arr1 = list(map(int, re.split(r'[\[\] ,\(\)]+', f.readline().strip())[1:-1]))
    arr2 = []
    for i in range(len(arr1) // 2):
        arr2.append([arr1[2 * i], arr1[2 * i + 1]])
trajectory = Trajectory(np.array(arr2))

env.cost_map = cost_map
context.env = env

# print(Relaxation.cost_segment(context, trajectory, cost_map, 36, 37))

np.set_printoptions(precision=2, suppress=True, linewidth=np.inf)
print(cost_map.data)
print(trajectory.coordinates)

print(trajectory)
new_trajectory = Relaxation.relax(context, trajectory, cost_map)
newer_trajectory = SplineInterpolation.interpolate(context, new_trajectory, cost_map)
print(new_trajectory)
# print("test", Relaxation.cost_segment(context, new_trajectory, cost_map, 0, 2))

fig, ax = plt.subplots()
ax.imshow(255-cost_map.data, cmap='gray', vmin=0, vmax=255)

ax.grid(which='major', axis='both', linestyle='-', color='k', linewidth=1)
ax.set_xticks(np.arange(-.5, len(cost_map.data[0]), 1))
ax.set_yticks(np.arange(-.5, len(cost_map.data), 1))
ax.tick_params(axis='both', which='both', labelsize=0)

plt.plot(trajectory.coordinates[:, 0], trajectory.coordinates[:, 1], 'o', color='r', )
plt.plot(new_trajectory.coordinates[:, 0], new_trajectory.coordinates[:, 1], 'o')
plt.plot(newer_trajectory.coordinates[:, 0], newer_trajectory.coordinates[:, 1], '-')

plt.show()