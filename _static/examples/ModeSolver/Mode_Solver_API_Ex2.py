import gdstk
import os

from pyModeSolver.pyModeSolver import VFDModeSolver
from pyOptiShared.LayerInfo import LayerStack
from pyOptiShared.DeviceGeometry import DeviceGeometry
from pyOptiShared.Material import ConstMaterial,ExperimentalMaterial
import numpy as np
import matplotlib.pyplot as plt

##########################################
###         Create Fiber GDS File         ###
##########################################
filename = "fiber.gds"
lib = gdstk.Library()
cell = lib.new_cell("fiber")
circle = gdstk.ellipse((0, 0), 7.5,layer=1)
cell.add(circle)
lib.write_gds(filename)

##########################################
###         Material Settings          ###
##########################################
air_mat = ConstMaterial("air", epsReal=1, epsImag=0.0)

sio2_exp = ExperimentalMaterial("my_material")
sio2_exp.SetFromRefDotInfo(shelf="main", book="SiO2", page="Malitson", wavelength_unit=1e-6)

##########################################
###       Layer Stack Settings         ###
##########################################
layer_stack = LayerStack()
layer_stack.AddLayer(number=1,material=sio2_exp, thickness=0.0, zmin=0, sideWallAng=0, cladding=air_mat)
layer_stack.SetBGandSub(background=air_mat, substrate=air_mat)

##########################################
###   Device Geometry/Port Settings    ###
##########################################
device_geometry = DeviceGeometry()
device_geometry.SetFromGDS(layer_stack=layer_stack,                              
                          gds_file=filename,
                          buffers={'x':5,'y':5,'z':5})

##########################################
###       ModeSolver Settings          ###
##########################################
lams=np.linspace(start=1.5,stop=1.6,num=5)
mode_solver = VFDModeSolver()
mode_solver.SetBoundaries(min_x = "pmc", max_x = "pmc",
                        min_y = "pmc", max_y = "pmc")

mode_solver.SetSimSettings(device_geometry = device_geometry,
                          mesh={"dx": 0.5,"dy": 0.5, "dz": 0.5},
                          wavelength=lams,
                          nguess = 3.4,
                          nmodes = 1,
                          cut_plane = "XY",
                          cut_location = 0.0,
                          tol = 1e-8,
                          results_path = "./ModeResults",
                          device_name = "my_results")

##########################################
###      Run and Post Processing       ###
##########################################
results = mode_solver.Run()


## Built in plotting functions
results.PlotMode() # Fundamental Mode Profile
results.PlotPermittivity()  # Material Profile
results.PlotIndex('neff',modes=[0]) # Effective Refractive Index
results.PlotIndex('ng',modes=[0]) # Effective Group Index
plt.show()