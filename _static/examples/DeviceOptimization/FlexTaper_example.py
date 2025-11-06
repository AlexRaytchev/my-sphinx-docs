import numpy as np
from pyOptiShared.Designs import flex_taper

# Generate the array of random widths
min_width, max_width, num_widths=0.4,2.2,8
w = np.random.uniform(low=min_width, high=max_width, size=num_widths)

lib=flex_taper(widths=w,taper_length=10,resolution=40,write=True)