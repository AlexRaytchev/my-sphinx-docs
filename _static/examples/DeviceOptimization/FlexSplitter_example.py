import numpy as np
from pyOptiShared.Designs import flex_splitter

# Generate the array of random widths
min_width, max_width, num_widths=1,3.2,8
w = np.random.uniform(low=min_width, high=max_width, size=num_widths)

lib=flex_splitter(widths=w,length=4,taper_length=2,resolution=40,write=True)