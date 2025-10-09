from stolen import Trajectory, CostMap, cartesian_to_ij
import matplotlib as plt
import scipy
import numpy as np
import math
class Relaxation:

    @staticmethod
    def cost_segment(trajectory: Trajectory, cost_map: CostMap, i: int, j: int):
        dist = np.sqrt(
            np.pow(trajectory.coordinates[i][0] - trajectory.coordinates[j][0], 2) +
            np.pow(trajectory.coordinates[i][1] - trajectory.coordinates[j][1], 2))
        
        points_per_m = 1
        interpolate = int(points_per_m * dist)
        segment_interval = dist / interpolate
        
        interpolated = np.vstack((np.linspace(trajectory.coordinates[i][0], trajectory.coordinates[j][0], interpolate), 
                                  np.linspace(trajectory.coordinates[i][1], trajectory.coordinates[j][1], interpolate)))

        

        cost = 0

        for i, (x, y) in enumerate(interpolated):
            cost += segment_interval #* cost_map[]

    @staticmethod
    def cost_full(trajectory: Trajectory) -> list[float]:
        pass

    @staticmethod
    def relax_single(trajectory: Trajectory) -> tuple[Trajectory, float]:   
        if len(trajectory.coordinates) <= 2:
            pass
        
        for i in range(1, len(trajectory.coordinates) - 1):


    @staticmethod
    def relax():
        pass