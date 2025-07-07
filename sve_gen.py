"""Main FRC SVE Generation Script"""

# author: Daniel Hoover (dhoovr@gmail.com)
# edited by Jihye Hur (jhur64@gatech.edu) starting from 08_01_24

# MIT License

# Copyright (c) 2025 Jihye Hur

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import numpy as np
from pathlib import Path
import os
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
import torch
from rich.progress import track
from classes import *

#---- generation parameters ----# 
size = (257, 257)
radius = 11.29294274
vf = 0.25
min_dist = radius + 2
close_dist = min_dist +2
percent_far = 0.1
percent_high_angle = 0.1

circle = make_circle_zero_shift(radius, size)

dist_temp, angle_temp = get_templates(size, radius, min_dist, close_dist)
pattern = [FarPlacement(min_dist, percent_far)]
pattern_seq = 'F25'
num_structs = 650

'''
FarPlacement(min_dist, percent_far)
ClosePlacement(min_dist, close_dist),
AlignedClosePlacement(min_dist, close_dist, percent_high_angle)
'''

structs = np.zeros([num_structs, size[0], size[1]])
centers_list = []
for n in track(range(num_structs)):
    struct_temp = np.zeros(size)
    struct = Structure(size, radius, dist_temp, angle_temp)
    StructureGenerator(struct, pattern).generate_to_vf(vf)
    centers = struct.centers
    centers_list.append(centers)
    for center in centers:
        structs[n, :, :] += np.roll(circle, center, axis=(0, 1))

centers_array = np.array(centers_list, dtype=object)
print('checking centers_array shape:', centers_array.shape)

#---- if even dimensions are needed... ----#

# new dims
UNIT_CELL_SIZE = 0.000112099824327958 # d value in um
GRID_SIZE = 256
RADIUS = int((4.925824504424278e-06 / UNIT_CELL_SIZE) * GRID_SIZE)  # r (um)/d (um)* d (pixel)

circle = make_circle(RADIUS, GRID_SIZE)

binary_images = []
for n in range(len(centers_array)):
    centers = centers_array[n] # get the x,y coords for n^th micro

    binary_image = create_binary_image(centers, circle, GRID_SIZE)
    binary_images.append(binary_image)

structs_new = np.stack(binary_images)

print("Number of binary images created:", len(binary_images))
print("Shape of the stacked array:", structs_new.shape)

# np.save(f'micros/{pattern_seq}/{pattern_seq}_{num_structs}_structs.npy', structs_new)
