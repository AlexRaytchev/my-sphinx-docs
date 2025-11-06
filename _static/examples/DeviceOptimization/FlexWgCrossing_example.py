import numpy as np
from pyOptiShared.Designs import flex_crossing

# Generate the array of random widths
min_width, max_width, num_widths=0.02,0.1,8
cross_dw = np.random.uniform(low=min_width, high=max_width, size=num_widths)

flex_crossing(cross_dw=cross_dw,dsep=2,resolution=40,write=True)

