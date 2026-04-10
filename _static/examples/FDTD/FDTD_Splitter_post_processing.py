import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from mpl_toolkits.axes_grid1 import make_axes_locatable
import gdstk
from pyFDTDKernel.FDTDResults import FDTDResults

# Loading the Results
results = FDTDResults()
results.loadHDF5('results/splitter.hdf5')
res = results.runs[0].dftmonitors["MyDFTMonitor1"]
x_ax = res.Get('x_axis')
y_ax = res.Get('y_axis')

lib = gdstk.read_gds('splitter.gds')
poly = lib.cells[1].polygons[0]
(xmin,ymin),(xmax,ymax) = poly.bounding_box()

hz_field = res.Get('Hz')

# Plotting the real part of the field
hz_real = np.real(hz_field)
hz_real = hz_real[5,:,:].transpose()
hz_real = hz_real-np.min(hz_real)
hz_real = hz_real/np.max(hz_real)
hz_real = 2*(hz_real-0.5)

fig, ax = plt.subplots()
im = ax.pcolormesh(x_ax,y_ax,hz_real,cmap='seismic',vmin=-1, vmax=1)
ax.set_xlim([xmin,xmax])
ax.set_ylim([ymin,ymax])
polygon = Polygon(poly.points, edgecolor='black', facecolor='none',linewidth=1,ls='--')
ax.add_patch(polygon)
ax.set_aspect('equal')
divider = make_axes_locatable(ax)
cax = divider.append_axes('right', size='5%', pad=0.05)
fig.colorbar(im,cax=cax ,orientation='vertical')
ax.set_xlabel("x (um)")
ax.set_ylabel("y (um)")
ax.set_title("Re{Hz}")
plt.savefig("splitter_hz_outline.svg", format="svg", bbox_inches="tight", dpi=300)
plt.show()