from pyModeSolver.pyModeSolver import VFDModeSolver
from pyOptiShared.LayerInfo import LayerStack
from pyOptiShared.DeviceGeometry import DeviceGeometry
from pyOptiShared.Material import ConstMaterial
import gdstk
import numpy as np
import matplotlib.pyplot as plt
##########################################
###             WG GDS File            ###
##########################################
filename = "wg.gds"

length = 10
width1 = 0.5
width2 = 2

lib = gdstk.Library()

strt_wg = lib.new_cell("Straight_WG")
vertices1 = [(0, -width1/2), (length, -width1/2), (length, width1/2), (0, width1/2)]
vertices2 = [(0, -width2/2), (length, -width2/2), (length, width2/2), (0, width2/2)]

strt_wg.add(gdstk.Polygon(vertices1, layer=1))
strt_wg.add(gdstk.Polygon(vertices2, layer=2))

lib.write_gds(filename)

##########################################
###         Material Settings          ###
##########################################
substrate_mat = ConstMaterial("SiO2", epsReal=1.444**2, epsImag=0.0)
core_mat = ConstMaterial("Si", epsReal=3.48**2, epsImag=0.0)

##########################################
###       Layer Stack Settings         ###
##########################################
layer_stack = LayerStack()
layer_stack.AddLayer(number=1,material=core_mat, thickness=0.22, zmin=0, sideWallAng=0, cladding="Air_default")
layer_stack.AddLayer(number=2,material=core_mat, thickness=0.09, zmin=0.0, sideWallAng=0, cladding="Air_default")
layer_stack.SetBGandSub(background="Air_default", substrate=substrate_mat)

##########################################
###   Device Geometry/Port Settings    ###
##########################################
device_geometry = DeviceGeometry()
device_geometry.SetFromGDS(layer_stack=layer_stack,
                           gds_file=filename,
                           buffers={'x':1,'y':1,'z':1})

##########################################
###       ModeSolver Settings          ###
##########################################
mode_solver = VFDModeSolver()
mode_solver.SetBoundaries(min_x = "pmc", max_x = "pmc",
                        min_y = "pmc", max_y = "pmc")

lams=np.linspace(start=1.5,stop=1.6,num=5)

mode_solver.SetSimSettings(device_geometry = device_geometry,
                           mesh={"dx": 0.02,"dy": 0.02, "dz": 0.02},
                           wavelength=lams,
                           nguess = 2.1,
                           nmodes = 10,
                           cut_plane = "YZ",
                           cut_location = 0.0,
                           tol = 1e-8,
                           results_path = "./ModeResults",
                           device_name = "my_results")

##########################################
###   Run and Results Visualization    ###
##########################################
results = mode_solver.Run()


results.PlotMode(field='Hy') # Fundamental Mode Profile
results.PlotPermittivity()  # Material Profile
results.PlotIndex('neff',modes=[0,1,2,3]) # Effective Refractive Index
results.PlotIndex('ng',modes=[0,1,2,3]) # Effective Group Index
results.Polarity(wavelength=1.5) # polarity of the modes
plt.show()