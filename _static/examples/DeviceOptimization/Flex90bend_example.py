import numpy as np
from pyOptiShared.Designs import flex_bend90

# Generate the array of random widths
min_width, max_width, num_widths=-0.1,0.2,8
w = np.random.uniform(low=min_width, high=max_width, size=num_widths)

dr_in=np.random.uniform(low=min_width, high=max_width, size=num_widths)
dr_out=np.random.uniform(low=min_width, high=max_width, size=num_widths)

lib=flex_bend90(dr_in=dr_in,dr_out=dr_out,radius=8,resolution=40,write=True)