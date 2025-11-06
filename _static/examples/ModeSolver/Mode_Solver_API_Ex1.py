from pyModeSolver.py_mode_solver import VFDModeSolver
from pyOptiShared.LayerInfo import LayerStack
from pyOptiShared.DeviceGeometry import DeviceGeometry
from pyOptiShared.Material import ConstMaterial
import gdstk

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
layer_stack.addLayer(number=1,material=core_mat, thickness=0.22, zmin=0, sideWallAng=0, cladding="Air_default")
layer_stack.addLayer(number=2,material=core_mat, thickness=0.09, zmin=0.0, sideWallAng=0, cladding="Air_default")
layer_stack.setBGandSub(background="Air_default", substrate=substrate_mat)

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
mode_solver.SetBoundaries(min_x = {"bc":"pmc"}, max_x = {"bc":"pmc"},
                        min_y = {"bc":"pmc"}, max_y = {"bc":"pmc"},)
mode_solver.SetSimSettings(device_geometry = device_geometry,
                           mesh={"dx": 0.02,"dy": 0.02, "dz": 0.02},
                           wavelength={"min":1.5,"max":1.6,"npts": 5},
                           nguess = 2.1,
                           nmodes = 4,
                           cut_plane = "YZ",
                           cut_location = 0.0,
                           tol = 1e-8,
                           savepath = "./ModeResults",
                           res_filename = "my_results")

##########################################
###   Run and Results Visualization    ###
##########################################
results = mode_solver.Run()


results.PlotMode(field='Hy') # Fundamental Mode Profile
results.PlotPermittivity()  # Material Profile
results.PlotIndex('neff',modes=[0,1,2,3]) # Effective Refractive Index
results.PlotIndex('ng',modes=[0,1,2,3]) # Effective Group Index