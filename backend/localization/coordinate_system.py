"""
Spatial Coordinate System & Room Geometry
Author: Uday Kiran Jammula
"""

import math
from typing import Tuple, Dict
from backend.config import config

class CoordinateSystem:
    """
    Manages 3D Cartesian coordinates inside the configured physical room.
    Origin (0, 0, 0) is at the bottom corner of the room floor.
    Z-axis represents height (vertical).
    X-axis represents room width.
    Y-axis represents room length.
    """
    def __init__(
        self,
        width: float = config.ROOM_WIDTH,
        length: float = config.ROOM_LENGTH,
        height: float = config.ROOM_HEIGHT,
        node_positions: Dict[int, Tuple[float, float, float]] = None
    ):
        self.width = width
        self.length = length
        self.height = height

        if node_positions is None:
            self.node_positions = {
                nid: ncfg.position for nid, ncfg in config.NODES.items()
            }
        else:
            self.node_positions = node_positions

    def clamp_to_bounds(self, x: float, y: float, z: float = 0.0) -> Tuple[float, float, float]:
        """Clamps estimated position inside the realistic physical boundaries of the room."""
        # Keep margin of 0.3 meters from walls
        margin = 0.3
        cx = max(margin, min(self.width - margin, x))
        cy = max(margin, min(self.length - margin, y))
        cz = max(0.0, min(self.height, z))
        return round(cx, 2), round(cy, 2), round(cz, 2)

    def get_node_position(self, node_id: int) -> Tuple[float, float, float]:
        return self.node_positions.get(node_id, (0.0, 0.0, 2.0))

    @staticmethod
    def distance_3d(p1: Tuple[float, float, float], p2: Tuple[float, float, float]) -> float:
        return math.sqrt(
            (p1[0] - p2[0]) ** 2 +
            (p1[1] - p2[1]) ** 2 +
            (p1[2] - p2[2]) ** 2
        )

    @staticmethod
    def distance_2d(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
