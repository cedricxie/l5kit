from functools import lru_cache
from typing import Any, Sequence, Union, no_type_check

import numpy as np
import pymap3d as pm

from ..geometry import transform_points
from .proto.road_network_pb2 import GeoFrame, MapElement, MapFragment

CACHE_SIZE = int(1e5)


class ProtoAPI:
    def __init__(self, protobuf_map_path: str, pose_to_ecef: np.ndarray):
        """
        Interface to the raw protobuf map file with the following features:
        - access to element using ID is O(1);
        - access to coordinates in world ref system for a set of elements is O(1) after first access (lru cache)
        - object support iteration using __getitem__ protocol

        Args:
            protobuf_map_path (str): path to the protobuf file
            pose_to_ecef (np.ndarray): transformation matrix from world coordinates to ECEF (dataset dependent)
        """
        self.protobuf_map_path = protobuf_map_path
        self.ecef_to_pose = np.linalg.inv(pose_to_ecef)

        with open(protobuf_map_path, "rb") as infile:
            mf = MapFragment()
            mf.ParseFromString(infile.read())

        self.elements = mf.elements
        self.ids_to_el = {self.get_element_id(el): idx for idx, el in enumerate(self.elements)}  # fast lookup table

    @staticmethod
    @no_type_check
    def get_element_id(element: MapElement) -> str:
        """
        Get the element id as a string.
        Elements ids are stored as a variable len sequence of bytes in the protobuf

        Args:
            element (MapElement): the element in the protobuf

        Returns:
            str: the id as a str
        """
        return element.id.id.decode("utf-8")

    @no_type_check
    def unpack_deltas_cm(self, dx: Sequence[int], dy: Sequence[int], dz: Sequence[int], frame: GeoFrame) -> np.ndarray:
        """
        Get coords in world reference system (local ENU->ECEF->world).
        See the protobuf annotations for additional information about how coordinates are stored

        Args:
            dx (Sequence[int]): X displacement in centimeters in local ENU
            dy (Sequence[int]): Y displacement in centimeters in local ENU
            dz (Sequence[int]): Z displacement in centimeters in local ENU
            frame (GeoFrame): geo-location information for the local ENU. It contains lat and long origin of the frame

        Returns:
            np.ndarray: array of shape (Nx3) with XYZ coordinates in world ref system

        """
        x = np.cumsum(np.asarray(dx) / 100)
        y = np.cumsum(np.asarray(dy) / 100)
        z = np.cumsum(np.asarray(dz) / 100)
        xyz = np.stack(pm.enu2ecef(x, y, z, frame.origin.lat_e7 * 1e-7, frame.origin.lng_e7 * 1e-7, 0), axis=-1)
        xyz = transform_points(xyz, self.ecef_to_pose)
        return xyz

    @lru_cache(maxsize=CACHE_SIZE)
    def get_lane_coords(self, element_id: str) -> dict:
        """
        Get XYZ coordinates in world ref system for a lane given its id

        Args:
            element_id (str): lane element id

        Returns:
            dict: a dict with the two boundaries coordinates as (Nx3) XYZ arrays
        """
        element = self[element_id]
        assert element.element.HasField("lane")

        lane = element.element.lane
        left_boundary = lane.left_boundary
        right_boundary = lane.right_boundary

        xyz_left = self.unpack_deltas_cm(
            left_boundary.vertex_deltas_x_cm,
            left_boundary.vertex_deltas_y_cm,
            left_boundary.vertex_deltas_z_cm,
            lane.geo_frame,
        )
        xyz_right = self.unpack_deltas_cm(
            right_boundary.vertex_deltas_x_cm,
            right_boundary.vertex_deltas_y_cm,
            right_boundary.vertex_deltas_z_cm,
            lane.geo_frame,
        )

        return {"xyz_left": xyz_left, "xyz_right": xyz_right}

    @lru_cache(maxsize=CACHE_SIZE)
    def get_crossword_coords(self, element_id: str) -> dict:
        """
        Get XYZ coordinates in world ref system for a crosswalk given its id

        Args:
            element_id (str): crosswalk element id

        Returns:
            dict: a dict with the polygon coordinates as an (Nx3) XYZ array
        """
        element = self[element_id]
        assert element.element.HasField("traffic_control_element")
        traffic_element = element.element.traffic_control_element
        assert traffic_element.HasField("pedestrian_crosswalk") and traffic_element.points_x_deltas_cm

        xyz = self.unpack_deltas_cm(
            traffic_element.points_x_deltas_cm,
            traffic_element.points_y_deltas_cm,
            traffic_element.points_z_deltas_cm,
            traffic_element.geo_frame,
        )

        return {"xyz": xyz}

    def __getitem__(self, item: Union[int, str]) -> Any:
        if isinstance(item, str):
            return self.elements[self.ids_to_el[item]]
        elif isinstance(item, int):
            return self.elements[item]
        else:
            raise TypeError("only str or int allowed in API __getitem__")

    def __len__(self) -> int:
        return len(self.elements)

    def __iter__(self) -> Any:
        for i in range(len(self)):
            yield self[i]