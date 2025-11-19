This repository contains research code associated with the protocols detailed in Hur *et al.*'s *Computational Protocols for Studying Damage Initiation in Unidirectional Fiber-Reinforced Polymer Matrix Composites*. 

**Code Usage Instructions**

Use sve_gen.py to generate transverse cross-sections of fiber reinforced composite microstructures at specified dimensions, fiber radii, fiber volume fractions, and inter-fiber dispersions, clustering, and alignment. Further instructions are provided in the mentioned python script. The data employed for the convergence studies in the paper is also available in this repository as 900_15_extremevals.h5. This contains 11200 extreme values per target microstructure (referred to as representative volume elements (RVEs) in the article). Use data_load.py to read the file. The user can access the extreme values for each RVE using the provided dictionary keys.

If you encounter any issues or have any questions, please contact me at jhur64@gatech.edu.

**Article**


J. Hur, D. Hoover, K.M. Ballard, V. Varshney, C. Przybyla, S.R. Kalidindi, *Computational Protocols for the Study of Damage Initiation in Unidirectional Fiber-Reinforced Polymer Matrix Composites*, Integr Mater Manuf Innov. (2025), https://doi.org/10.1007/s40192-025-00429-y.
