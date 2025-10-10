from dataclasses import dataclass, field
import numpy as np


@dataclass
class Trajectory:
    # Coordinates of the trajectory
    coordinates: np.ndarray
    # Currently tracked coordinate index along trajectory
    cur_pt: int = field(default=0, init=False)

    def get_current_point(self) -> np.ndarray:
        return self.coordinates[self.cur_pt]

    def increment_point(self) -> bool:
        """
        Increments the tracked point in the trajectory, returns true if
        the trajectory is finished
        """
        self.cur_pt = min(self.cur_pt + 1, len(self.coordinates))
        return self.cur_pt >= len(self.coordinates)

    def decerement_point(self) -> bool:
        """
        Increments the tracked point in the trajectory, returns true if
        the trajectory is finished
        """
        self.cur_pt = max(0, self.cur_pt - 1)
        return self.cur_pt <= 0

    def done(self) -> bool:
        return self.cur_pt >= len(self.coordinates)

    def empty(self) -> bool:
        return len(self.coordinates) == 0

    def is_last(self) -> bool:
        if len(self.coordinates) == 0:
            return True
        else:
            return self.cur_pt == len(self.coordinates) - 1

    def clear(self):
        self.coordinates = np.array([])
        self.cur_pt = 0

    def reset(self) -> None:
        """
        Resets the trajectory back to its start
        """
        self.cur_pt = 0



class CostMap:
    def __init__(self):
        self.data = np.array([[]])
        self.origin = np.asarray([0, 0])
        self.resolution = 0.25


class Environment:
    cost_map = CostMap()


class Context:
    env = Environment()


def cartesian_to_ij(context: Context, cart_coord: np.ndarray) -> np.ndarray:
    """
    Convert real world cartesian coordinates (x, y) to coordinates in the occupancy grid (i, j)
    using formula floor(v - (WP + [-W/2, H/2]) / r) * [1, -1]
    v: (x,y) coordinate
    WP: origin
    W, H: grid width, height (meters)
    r: resolution (meters/cell)
    :param cart_coord: array of x and y cartesian coordinates
    :return: array of i and j coordinates for the occupancy grid
    """
    return np.floor(
        (cart_coord[0:2] - context.env.cost_map.origin)
        / context.env.cost_map.resolution
    ).astype(np.int32)


def ij_to_cartesian(context: Context, ij_coords: np.ndarray) -> np.ndarray:
    """
    Convert coordinates in the occupancy grid (i, j) to real world cartesian coordinates (x, y)
    using formula (WP - [W/2, H/2]) + [j * r, i * r] + [r/2, -r/2] * [1, -1]
    WP: origin
    W, H: grid width, height (meters)
    r: resolution (meters/cell)
    :param ij_coords: array of i and j occupancy grid coordinates
    :return: array of x and y coordinates in the real world
    """
    half_res = np.array(
        [context.env.cost_map.resolution / 2, context.env.cost_map.resolution / 2]
    )
    return (
        context.env.cost_map.origin
        + ij_coords * context.env.cost_map.resolution
        + half_res
    )
