from stolen import Trajectory, CostMap, Context, cartesian_to_ij

import matplotlib.pyplot as plt
import scipy
from scipy.interpolate import make_splprep, splev
import numpy as np

import math, sys


class SplineInterpolation:

    # @staticmethod
    # def generate_points_in_segment(
    #     ctx: Context, trajectory: Trajectory, cost_map: CostMap
    # ) -> np.ndarray:
    #     pass

    @staticmethod
    def interpolate(
        ctx: Context, trajectory: Trajectory, cost_map: CostMap, spacing: float = 0.25
    ) -> Trajectory:
        """
        Fits cubic splines to the given trajectory and returns a new trajectory with 
        evenly spaced points sampled from the splines. We approximate the total distance
        of the calculated splines and map the desired distances of each point to the 
        default parameterization produce by scipy.
        """
        # can configure smoothness (s) and other parameters
        spline, u = make_splprep(
            [trajectory.coordinates[:, 0], trajectory.coordinates[:, 1]], s=0,k=2
        )

        # make really smooth for accurate distance
        u_fine = np.linspace(u.min(), u.max(), 100)  # TODO find good number
        x_fine, y_fine = spline(u_fine)

        # calculate distance from start for each point
        dist = np.cumsum(np.sqrt(np.diff(x_fine) ** 2 + np.diff(y_fine) ** 2))
        dist = np.insert(dist, 0, 0)

        samples = int(dist[-1] / spacing)
        target_dist = np.linspace(0, samples * spacing, samples + 1)

        u_spaced = np.interp(target_dist, dist, u_fine)  # map distance to u parameter
        u_spaced = np.append(u_spaced, u[-1])  # make sure end waypoint is preserved

        # np.concatenate(u_spaced, u) TODO maybe also include original u in input so that all original waypoints are still used

        x_spaced, y_spaced = spline(u_spaced)

        return Trajectory(np.column_stack([x_spaced, y_spaced]))
