from pyOptiShared.LayerInfo import LayerStack
from pyOptiShared.DeviceGeometry import DeviceGeometry
from pyOptiShared.Material import ConstMaterial

import numpy as np

##########################################
###         Material Settings          ###
##########################################
substrate_mat = ConstMaterial("SiO2", epsReal=1.444**2, epsImag=0.0)
core_mat = ConstMaterial("Si", epsReal=3.48**2, epsImag=0.0)

##########################################
###       Layer Stack Settings         ###
##########################################
layer_stack = LayerStack()
layer_stack.addLayer(number=1,material=core_mat, thickness=0.22, zmin=0, sideWallAng=0, cladding="Air_default")
layer_stack.addLayer(number=2,material=core_mat, thickness=0.09, zmin=0.0, sideWallAng=0, cladding="Air_default")
layer_stack.setBGandSub(background="Air_default", substrate=substrate_mat)

lam = 1.55 # um

device_geometry = DeviceGeometry()
device_geometry.SetFromGDS(
    layer_stack=layer_stack,
    gds_file=r"wg.gds",
    buffers={'x':1.5,'y':1.5,'z':1.5}
)

dx = dy = dz = 0.05
bbox = device_geometry.GetBoundingBox(with_buffer=True)
(xmin, xmax), (ymin, ymax), (zmin, zmax) = bbox
xx = np.arange(xmin, xmax, dx)
yy = np.arange(ymin, ymax, dy)
zz = np.arange(zmin, zmax, dz)

nx = xx.shape[0]
ny = yy.shape[0]
nz = zz.shape[0]

XX, YY, ZZ = np.meshgrid(xx, yy, zz, indexing='ij')
points = np.asarray([XX.ravel(), YY.ravel(), ZZ.ravel()]).T

# Get the material and permittivity meshes
material_mesh = device_geometry.GetMatVals(points)
eps = device_geometry.GetPermittivityMesh(points, lam)

# Get back a 3D array of the linear points
shape = (nx,ny,nz)
eps = eps.reshape(shape)

# Plotting real part of epsilon
import matplotlib.pyplot as plt

plt.imshow(np.real(eps[:,:,int(nz/2)]).T,aspect='equal',origin='lower')
plt.show()