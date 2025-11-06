from pyOptiShared.LayerInfo import LayerStack
from pyOptiShared.Material import ConstMaterial
from pyOptiShared.DeviceGeometry import DeviceGeometry
from pyOptiShared.PortInfo import PortInfo
from pyFDTDKernel.pyFDTDSolver import pyFDTDSolver
import gdstk

##########################################
###             WG GDS File            ###
##########################################
filename = "wg.gds"

length = 2
width1 = 0.5
width2 = 2

lib = gdstk.Library()

strt_wg = lib.new_cell("Straight_WG")
vertices1 = [(0, -width1/2), (length, -width1/2), (length, width1/2), (0, width1/2)]
vertices2 = [(0, -width2/2), (length, -width2/2), (length, width2/2), (0, width2/2)]

strt_wg.add(gdstk.Polygon(vertices1, layer=2))
strt_wg.add(gdstk.Polygon(vertices2, layer=1))

lib.write_gds(filename)

##########################################
###         Material Settings          ###
##########################################
myindex1p45 = ConstMaterial(mat_name="myindex1p45", epsReal=1.45**2)
myindex1p55 = ConstMaterial(mat_name="myindex1p55", epsReal=1.55**2)
myindex3p5 = ConstMaterial(mat_name="myindex3p5", epsReal=3.5**2)

##########################################
###       Layer Stack Settings         ###
##########################################
layer_stack = LayerStack()
layer_stack.addLayer(name="L1", number=1, thickness=0.25, zmin=0.0,
                    material=myindex3p5,cladding=myindex1p45)
layer_stack.addLayer(name="L2", number=2, thickness=0.25, zmin=0.25,
                    material=myindex3p5,cladding=myindex1p45)
layer_stack.setBGandSub(background=myindex1p45, substrate=myindex1p45)

##########################################
###   Device Geometry/Port Settings    ###
##########################################
device_geometry = DeviceGeometry()
device_geometry.SetFromGDS(
    layer_stack=layer_stack,
    gds_file=r"wg.gds",
    buffers={'x':1.5,'y':1.5,'z':1.5}
    )

port0=PortInfo(lines=[[(0.0,-0.25),(0.0,0.25)]],layer_number=2,orientation=180,mode_number=0,buffer=[1.0,1.0])
port0.update(lines=[[(0.0,-1.0),(0.0,1.0)]],layer_number=1) # add another cut in a different layer

port1=PortInfo(lines=[[(2.0,-0.25),(2.0,0.25)]],layer_number=2,orientation=0,mode_number=0,buffer=[1.0,1.0])
port1.update(lines=[[(2.0,-1.0),(2.0,1.0)]],layer_number=1) # add another cut in a different layer

device_geometry.AddPort(port0)
device_geometry.AddPort(port1)
device_geometry.PrintPorts()

# General Simulation Settings and Simulation Run
lmin = 1.5
lmax = 1.6
lcen = (lmax+lmin)/2
npts=21
tfinal = 550
fdtd_solver = pyFDTDSolver()
fdtd_solver.SetPorts(profile="gaussian-pw", lcenter=lcen, lmin=lmin, lmax=lmax, npts=npts, mode_indices = 0,symmetries='1x1')
fdtd_solver.AddDFTMonitor(mon_type="2d-z-normal", z0=0.11, name="MyDFTMonitor1",
                                                      lmin=lmin, lmax=lmax,npts=npts,
                                                      save_hz=True)
fdtd_solver.SetSimSettings(sim_time=tfinal, space_step=0.05, subpixel_level=2, save_path=r"results",results_filename='wg',
                                                      device_geometry = device_geometry,auto_shutoff_limit=1e-3,export_mat_grid=True)
results = fdtd_solver.Run()
results.PlotSParameters()
results.PlotPermittivity(cut='x',position=-0.5)
results.PlotPermittivity(cut='x',position=0.5)
results.PlotPermittivity(position=0.11)

