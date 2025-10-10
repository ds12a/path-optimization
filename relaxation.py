from stolen import Trajectory, CostMap, Context, cartesian_to_ij

import matplotlib as plt
import scipy
import numpy as np

import math, sys


class Relaxation:

    @staticmethod
    def cost_segment(
        ctx: Context, trajectory: Trajectory, cost_map: CostMap, i: int, j: int
    ) -> float:
        """
        Calculates the cost of the straight-line path between coordinate indices i and j
        in the given trajectory. The method interpolates floor(length(path)) evenly-spaced
        points in the path segment and returns an approximation of "total cost"
        (cost * path length).
        """

        # distance between start and end points
        dist = np.sqrt(
            np.pow(trajectory.coordinates[i][0] - trajectory.coordinates[j][0], 2)
            + np.pow(trajectory.coordinates[i][1] - trajectory.coordinates[j][1], 2)
        )

        points_per_m = 1
        interpolate = int(points_per_m * dist)  # total number of interpolated points
        segment_interval = dist / interpolate  # distance between interpolated points

        interpolated = np.column_stack(
            (
                np.linspace(
                    trajectory.coordinates[i][0],
                    trajectory.coordinates[j][0],
                    interpolate,
                ),
                np.linspace(
                    trajectory.coordinates[i][1],
                    trajectory.coordinates[j][1],
                    interpolate,
                ),
            )
        )
        cost = 0.0

        for i, (x, y) in enumerate(interpolated):
            cost += (
                segment_interval * cost_map.data[cartesian_to_ij(ctx, np.array([x, y]))]
            )  # TODO check if this cost function can "overcount" cost

        return cost

    @staticmethod
    def cost_full(
        ctx: Context, trajectory: Trajectory, cost_map: CostMap
    ) -> tuple[float, list[float]]:
        segment_costs = []
        total_cost = 0.0

        for i in range(len(trajectory.coordinates) - 1):
            cost_i = Relaxation.cost_segment(ctx, trajectory, cost_map, i, i + 1)

            total_cost += cost_i
            segment_costs.append(cost_i)

        return (total_cost, segment_costs)

    @staticmethod
    def relax_single(
        ctx: Context, trajectory: Trajectory, cost_map: CostMap
    ) -> tuple[Trajectory, float]:

        total_cost, segment_costs = Relaxation.cost_full(
            ctx, trajectory, cost_map
        )  # TODO could optimize by putting this in relax() and passing it over

        if len(trajectory.coordinates) <= 2:
            return trajectory, total_cost

        min_idx = -1
        min_cost = sys.maxsize

        for i in range(1, len(trajectory.coordinates) - 1):
            cost_i = Relaxation.cost_segment(ctx, trajectory, cost_map, i - 1, i + 1)
            if cost_i < (segment_costs[i - 1] + segment_costs[i]):
                min_cost = cost_i
                min_idx = i

        cost = (
            total_cost + min_cost - segment_costs[min_idx - 1] - segment_costs[min_idx]
        )
        new_traj = Trajectory(np.delete(trajectory.coordinates, min_idx))

        return (new_traj, cost)

    @staticmethod
    def relax(ctx: Context, trajectory: Trajectory, cost_map: CostMap) -> Trajectory:

        cost, _ = Relaxation.cost_full(ctx, trajectory, cost_map)

        current_trajectory = trajectory
        candidate_traj, candidate_cost = Relaxation.relax_single(
            ctx, trajectory, cost_map
        )

        # TODO: depending on how inefficient this is, we may limit how many times this loop runs
        while candidate_cost < cost:
            if len(current_trajectory.coordinates) <= 2:
                break

            current_trajectory = candidate_traj
            cost = candidate_cost

            candidate_traj, candidate_cost = Relaxation.relax_single(
                ctx, trajectory, cost_map
            )

        return current_trajectory
