''' Read .h5 files '''
import numpy as np
import h5py

# dat = '900_15_sves.h5'
evs = '900_15_extremevals.h5'

# Class names (access keys)
seq = ["F30", "FA30", "FAAA30", "FC30", "FCCC30",
      "F40", "FA40", "FAAA40", "FC40", "FCCC40",
      "F50", "FA50", "FAAA50", "FC50", "FCCC50"]

# Load in .h5 files
# with h5py.File(dat, 'r') as f:
#     for pattern in seq:
#         data = f[pattern][:]
#         print(f"Loaded {pattern}, data shape: {data.shape}")

with h5py.File(evs, 'r') as f:
    for pattern in seq:
        data = f[pattern][:]
        print(f"Loaded {pattern}, data shape: {data.shape}")
