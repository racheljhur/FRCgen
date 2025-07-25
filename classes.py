'''Core Generation Functions'''
import numpy as np
from pathlib import Path
import os
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
import torch
from rich.progress import track

def make_circle_og(radius, size):
    assert len(np.unique(size)) == 1
    size = size[0]
    assert radius < size
    assert size % 2 != 0
    shape = np.zeros((size, size))
    center_loc = int((size - 1) / 2)
    for i in range(size):
        for j in range(size):
            if np.square(i-center_loc) + np.square(j-center_loc) <= np.square(radius):
                shape[i, j] = 1
    return shape

def make_circle_zero_shift(radius, size):
    return np.fft.fftshift(make_circle_og(radius, size)).astype(int)

class NoCandidates(Exception):
    """Raise when the set of candidate points is zero."""
    def __init__(self, message=f"len(candidates) <= 0"):
            super().__init__(message)

class Structure:
    """Contain structure and tools for respective structure."""
    def __init__(self, size, radius, dist_temp, angle_temp):
        self.size = size
        self.radius = radius
        self.dist_temp = dist_temp
        self.angle_temp = angle_temp
        init_point = np.hstack((np.random.randint(0, high=size[0] - 1, size=1),
                                np.random.randint(0, high=size[1] - 1, size=1)))
        self.dist_map = circshift(self.dist_temp, init_point)
        self.angle_map = circshift(self.angle_temp, init_point)
        self.num_circles = 1
        self.centers = [init_point]

    def get_vf(self):
        window_area = self.size[0] * self.size[1]
        circle_area = np.pi * self.radius ** 2
        return (circle_area * self.num_circles) / window_area

    def update_dist_map(self, point):
        point_dist_map = circshift(self.dist_temp, point)
        dist_map_stack = np.stack((self.dist_map, point_dist_map), axis=-1)
        self.dist_map = np.min(dist_map_stack, axis=-1)  ## check numpy docs. This might be bad

    def update_angle_map(self, point):
        point_angle_map = circshift(self.angle_temp, point)
        angle_map_stack = np.stack((self.angle_map, point_angle_map), axis=-1)
        self.angle_map = np.max(angle_map_stack, axis=-1)

    def place(self, placement):
        placement_map = placement.get_map(self)
        candidates = np.transpose(np.nonzero(placement_map))
        if len(candidates) <= 0:
            raise NoCandidates()
        else:
            point_index = np.random.randint(0, high=len(candidates), size=1)
            point = candidates[point_index, :][0]
            self.update_dist_map(point)
            self.update_angle_map(point)
            self.centers.append(point)
            self.num_circles += 1

    def copy(self):
        return copy.copy(self)

class Placement(ABC):
    """Provide tools for placing new circles."""
    def __init__(self, min_dist):
        self.min_dist = min_dist
    
    @abstractmethod
    def get_map(self, struct):
        pass

class ClosePlacement(Placement):
    """Provide tools for placing circles close."""
    def __init__(self, min_dist, close_dist):
        super().__init__(min_dist)
        self.close_dist = close_dist

    def get_map(self, struct):
        close_map = (struct.dist_map > self.min_dist) * \
                    (struct.dist_map < self.close_dist)
        return close_map

class FarPlacement(Placement):
    """Provide tools for placing circles far."""
    def __init__(self, min_dist, percent_far):
        super().__init__(min_dist)
        self.percent_far = percent_far

    def get_map(self, struct):
        far_buffer = np.max(struct.dist_map) * \
                        (1 - self.percent_far)
        far_map = (struct.dist_map > self.min_dist) * \
                    (struct.dist_map > far_buffer)
        return far_map

class AlignedClosePlacement(ClosePlacement):
    """Provide tools for placing circles Close and Aligned."""
    def __init__(self, min_dist, close_dist, percent_high_angle):
        super().__init__(min_dist, close_dist)
        self.percent_high_angle = percent_high_angle

    def get_map(self, struct):
        angle_buffer = np.max(struct.angle_map) * \
                        (1 - self.percent_high_angle)
        aligned_map = struct.angle_map > angle_buffer
        close_map = super().get_map(struct)
        aligned_close_map = aligned_map * close_map
        return aligned_close_map

class StructureGenerator:
    """Generate structures from initial structure and pattern."""
    def __init__(self, struct, placement_pattern):
        self.struct = struct
        self.placement_pattern = placement_pattern

    def generate_to_vf(self, vf, permit_low_vf=True):
        current_pattern_index = 0
        while self.struct.get_vf() < vf:
            try:
                self.struct.place(self.placement_pattern[current_pattern_index])
            except(NoCandidates):
                if permit_low_vf:
                    break
                else:
                    pass
            else:
                current_pattern_index += 1
                if current_pattern_index == len(self.placement_pattern):
                    current_pattern_index = 0

def circshift(template, point):
    return np.roll(template, point, axis=(0, 1))

def get_templates(size, radius, min_dist, close_dist):
    dist_temp = np.zeros(size)
    angle_temp = np.zeros(size)
    center = np.array((int(size[0] / 2), int(size[1] / 2)))
    for point, val in np.ndenumerate(dist_temp):
        dist = np.linalg.norm(point - center) - radius
        dist_temp[point] = dist
        if dist > min_dist and dist < close_dist:
            diff = np.abs(point - center)
            angle_temp[point] = np.rad2deg(np.arctan2(diff[0], diff[1]))
    return [np.fft.fftshift(dist_temp), np.fft.fftshift(angle_temp)]

#--- for micros with even dimensions ---#

def make_circle(radius, grid_size):
    """Create a binary circle centered in a square grid"""
    y, x = np.ogrid[:grid_size, :grid_size]
    center = (grid_size - 1) / 2
    mask = (x - center) ** 2 + (y - center) ** 2 <= radius ** 2
    shape = np.zeros((grid_size, grid_size), dtype=np.uint8)
    shape[mask] = 1
    return shape

def create_binary_image(centers, circle, grid_size):
    """Create a binary image using fiber centers"""
    image = np.zeros((grid_size, grid_size), dtype=np.uint8)

    for center in centers:
        x_shift, y_shift = np.array(center, dtype=np.int32).flatten()
        shifted_circle = np.roll(np.roll(circle, x_shift, axis=0), y_shift, axis=1)
        image += shifted_circle

    image = np.clip(image, 0, 1)
    # rotate for aligned micros
    image = np.rot90(image, k=1)

    return image
