from stolen import Trajectory, CostMap, Context, cartesian_to_ij

import matplotlib as plt
import scipy
import numpy as np

import math, sys

class Relaxation:

    @staticmethod
    def cost_segment(ctx: Context, trajectory: Trajectory, cost_map: CostMap, i: int, j: int) -> float:
        """
        Calculates the cost of the straight-line path between coordinate indices i and j
        in the given trajectory. The method interpolates floor(length(path)) even-spaced 
        points in the path segment and returns an approximation of "total cost" 
        (cost * path length).
        """

        dist = np.sqrt(
            np.pow(trajectory.coordinates[i][0] - trajectory.coordinates[j][0], 2) +
            np.pow(trajectory.coordinates[i][1] - trajectory.coordinates[j][1], 2))
        
        points_per_m = 1
        interpolate = int(points_per_m * dist)
        segment_interval = dist / interpolate
        
        interpolated = np.column_stack((np.linspace(trajectory.coordinates[i][0], trajectory.coordinates[j][0], interpolate), 
                                        np.linspace(trajectory.coordinates[i][1], trajectory.coordinates[j][1], interpolate)))
        cost = 0.0

        for i, (x, y) in enumerate(interpolated):
            cost += segment_interval * cost_map.data[cartesian_to_ij(ctx, np.array([x, y]))]      # TODO check if this cost function can "overcount" cost

        return cost


    @staticmethod
    def cost_full(ctx: Context, trajectory: Trajectory, cost_map: CostMap) -> tuple[float, list[float]]:
        total_cost = []
        cost = 0.0

        for i in range(len(trajectory.coordinates) - 1):
            cost_i = Relaxation.cost_segment(ctx, trajectory, cost_map, i, i + 1)
            
            cost += cost_i
            total_cost.append(cost_i)

        return (cost, total_cost)


    @staticmethod
    def relax_single(ctx: Context, trajectory: Trajectory, cost_map: CostMap) -> tuple[Trajectory, float]:   
        
        cost_all = Relaxation.cost_full(ctx, trajectory, cost_map)      # TODO could optimize by putting this in relax() and passing it over

        if len(trajectory.coordinates) <= 2:
            pass                                                        # TODO
        
        min_idx = -1
        min_cost = sys.maxsize

        for i in range(1, len(trajectory.coordinates) - 1):
            
            cost_i = Relaxation.cost_segment(ctx, trajectory, cost_map, i - 1, i + 1)
            if cost_i < (cost_all[1][i - 1] + cost_all[1][i]):
                min_cost = cost_i
                min_idx = i
        
        cost = cost_all[0] + min_cost - cost_all[1][min_idx - 1] - cost_all[1][min_idx]
        new_t = Trajectory(np.delete(trajectory.coordinates, min_idx))

        return (new_t, cost)
    

    @staticmethod
    def relax(ctx: Context, trajectory: Trajectory, cost_map: CostMap) -> Trajectory:
        
        cost = Relaxation.cost_full(ctx, trajectory, cost_map)[0]

        current_trajectory = trajectory
        candidate = Relaxation.relax_single(ctx, trajectory, cost_map)
        while(candidate[1] < cost):
            if len(current_trajectory.coordinates) <= 2:
                break
            
            current_trajectory = candidate[0]
            cost = candidate[1]

            candidate = Relaxation.relax_single(ctx, trajectory, cost_map)
        
        return current_trajectory
