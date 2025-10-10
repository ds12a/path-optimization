from stolen import Trajectory, CostMap, Context, cartesian_to_ij

import matplotlib as plt
import scipy
import numpy as np

import math, sys

class SplineInterpolation:

    @staticmethod
    def generate_points_in_segment(ctx: Context, trajectory: Trajectory, cost_map: CostMap) -> np.ndarray:
        pass

    @staticmethod
    def interpolate(ctx: Context, trajectory: Trajectory, cost_map: CostMap) -> Trajectory:

        # scipy interpolate
        # loop through each segment, generate points
        # bing bang boom return
        pass