"""Main FRC SVE Generation Script"""

# author: Daniel Hoover (dhoover9@gmail.com)
# edited by me (jhur64@gatech.edu) starting from 08_01_24

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
