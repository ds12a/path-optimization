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
        in the given trajectory. The method interpolates ceil(length(path)) evenly-spaced
        points in the path segment and returns an approximation of "total cost"
        (cost * path length).

        trajectory is in cost map coordinates
        """

        # distance between start and end points
        dist = np.sqrt(
            (trajectory.coordinates[i][0] - trajectory.coordinates[j][0]) ** 2
            + (trajectory.coordinates[i][1] - trajectory.coordinates[j][1]) ** 2
        )

        points_per_m = 3
        interpolate = math.ceil(points_per_m * dist)  # total number of interpolated points
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

        for x, y in interpolated:
            # print(x,y)

            if abs(0.5 - (x - int(x))) < 1e-5 and abs(0.5 - (y - int(y))) < 1e-5:     # Close to boundary
                cost_arr = [
                    cost_map.data[int(x), int(y)],
                    cost_map.data[int(x) + 1, int(y)],
                    cost_map.data[int(x), int(y) + 1],
                    cost_map.data[int(x) + 1, int(y) + 1]
                    ]
                
                cost += segment_interval * (min(cost_arr) + 0.001)

                # if cost_arr[0] != 0.0 or cost_arr[1] != 0.0 or cost_arr[2] != 0.0 or cost_arr[3] != 0.0:
                #     print("rounding workaround", x, y, cost_arr, segment_interval * (min(cost_arr) + 0.001))
            else:
                cost += (
                    segment_interval
                    * (cost_map.data[int(y + 0.5), int(x + 0.5)] + 0.001) # make cost nonzero so distance matters
                )
        # print(cost)
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
        min_cost = -1
        max_diff = -sys.maxsize

        for i in range(1, len(trajectory.coordinates) - 1):
            cost_i = Relaxation.cost_segment(ctx, trajectory, cost_map, i - 1, i + 1)
            diff_i = (segment_costs[i - 1] + segment_costs[i]) - cost_i
            if max_diff < diff_i:
                min_cost = cost_i
                min_idx = i
                max_diff = diff_i

        cost = total_cost - max_diff

        new_traj = Trajectory(
            np.append(
                trajectory.coordinates[:min_idx],
                trajectory.coordinates[min_idx + 1 :],
                axis=0,
            )
        )
        return (new_traj, cost)

    @staticmethod
    def relax(ctx: Context, trajectory: Trajectory, cost_map: CostMap) -> Trajectory:
        cost, _ = Relaxation.cost_full(ctx, trajectory, cost_map)

        current_trajectory = trajectory
        candidate_traj, candidate_cost = Relaxation.relax_single(
            ctx, trajectory, cost_map
        )

        # TODO: depending on how inefficient this is, we may limit how many times this loop runs
        while candidate_cost < cost or math.isclose(candidate_cost, cost):
            if len(current_trajectory.coordinates) <= 2:
                break

            current_trajectory = candidate_traj
            cost = candidate_cost

            candidate_traj, candidate_cost = Relaxation.relax_single(
                ctx, current_trajectory, cost_map
            )

        return current_trajectory
