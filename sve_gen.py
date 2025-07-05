"""Main FRC SVE Generation Script"""

# author: Daniel Hoover (dhoovr@gmail.com)
# edited by me (jhur64@gatech.edu) starting from 08_01_24

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


import os
import numpy as np
from pathlib import Path
from datetime import datetime
from rich.progress import track

from pathlib import Path
from abc import ABC, abstractmethod

from classes import *

data_dir = Path(os.getcwd()) / "data"
os.makedirs(data_dir, exist_ok=True)

#---------- generation parameters ----------#
size = (751, 751)
radius = 30
num_structs = 200
vf = 0.35
min_dist = 2
close_dist = min_dist + 2
percent_far = 0.1
percent_high_angle = 0.1

#---------- generation pattern ----------#
dist_temp, angle_temp = get_templates(size, radius, min_dist, close_dist)

pattern_string = 'FAAA'

placement_mapping = {
    'F': lambda: FarPlacement(min_dist, percent_far),
    'C': lambda: ClosePlacement(min_dist, close_dist),
    'A': lambda: AlignedClosePlacement(min_dist, close_dist, percent_high_angle),
}

pattern = [placement_mapping[char]() for char in pattern_string]

#---------- generation loop ----------#
centers_list = []

for n in track(range(num_structs)):
        struct = Structure(size, radius, dist_temp, angle_temp)
        generator = StructureGenerator(struct, pattern)
        generator.generate_to_vf(vf)

        centers_list.append(np.hstack([struct.centers, np.ones([len(struct.centers), 1]) * radius]))

fiber_centers = np.vstack(centers_list)
np.save(data_dir / f"{pattern_string}_{num_structs}_centers.npy", fiber_centers)
