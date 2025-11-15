"""Main FRC SVE Generation Script"""
import numpy as np
from pathlib import Path
import os
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
import torch
from rich.progress import track
from classes import *

#---- Global Parameters for Generation ----# 
'''
The edge length of the domain considered in the study was 112 um.
The radius was (112 um / 75 pixels) * 11 pixels ≈ 16 um.

THINGS THAT YOU WILL NEED TO CHANGE EXPLICITLY:
(1) DOMAIN SIZE >> (d,d)
(2) FIBER RADIUS >> 30
(3) TARGET FIBER VOLUME FRACTION >> 0.30
(4) MINIMUM PERMISSIBLE DISTANCE B/W FIBER EDGES >> fiber_radius + 2
(5) CLOSE CLUSTERING DISTANCES >> minimum_distance + 2
(6) PERCENTILE OF FAR DISTANCES >> 0.1 (corresponds to the top 99th percentile)
(7) PERCENTILE OF HORIZONTAL ALIGNMENT >> 0.1 (corresponds to the top 99th percentile)
'''

size = (751, 751) # The dimensions here must be odd
radius = 30
vf = 0.30 
min_dist = radius + 2
close_dist = min_dist + 2 
percent_far = 0.1 
percent_high_angle = 0.1 
num_structs = 10 # Number of SVEs to be generated
pattern_seq = "F30" # This is for my filename later

# Call core generation functions
'''
Placement options:
FarPlacement(min_dist, percent_far)
ClosePlacement(min_dist, close_dist),
AlignedClosePlacement(min_dist, close_dist, percent_high_angle)

Usage example:
pattern = [FarPlacement(min_dist, percent_far), 
           ClosePlacement(min_dist, close_dist)]
'''

circle = make_circle_zero_shift(radius, size)
dist_temp, angle_temp = get_templates(size, radius, min_dist, close_dist)

pattern = [FarPlacement(min_dist, percent_far)] 

structs = np.zeros([num_structs, size[0], size[1]])
# Initialize centers array 
# (this was mainly for the FE simulations, since the tool we used takes in fiber centers)
# centers_list = []

# Main loop to generate n number of SVEs
for n in track(range(num_structs)):
    struct_temp = np.zeros(size)
    struct = Structure(size, radius, dist_temp, angle_temp)
    StructureGenerator(struct, pattern).generate_to_vf(vf)
    centers = struct.centers
    # centers_list.append(centers)
    for center in centers:
        structs[n, :, :] += np.roll(circle, center, axis=(0, 1))

# centers_array = np.array(centers_list, dtype=object) # Specifying dtype here because python gets annoyed when saving npy arrays of inconsistent number of columns

# write results
# np.save(f'micros/{pattern_seq}/{pattern_seq}_{num_structs}_structs.npy', structs)
# print('checking centers_array shape:', centers_array.shape)

# If even dimensions are needed
# Setting new dimensions
UNIT_CELL_SIZE = 0.000112099824327958 # d value in um
GRID_SIZE = 750
RADIUS = int((4.925824504424278e-06 / UNIT_CELL_SIZE) * GRID_SIZE)  # r (um)/d (um)* d (pixel)

circle = make_circle(RADIUS, GRID_SIZE)

binary_images = []
for n in range(len(centers_array)):
    centers = centers_array[n] # get the x,y coords for n^th SVE
    binary_image = create_binary_image(centers, circle, GRID_SIZE)
    binary_images.append(binary_image)

structs_new = np.stack(binary_images)

# print("Number of binary images created:", len(binary_images))
# print("Shape of the stacked array:", structs_new.shape)

# write results
# np.save(f'micros/{pattern_seq}/{pattern_seq}_{num_structs}_structs.npy', structs_new)
