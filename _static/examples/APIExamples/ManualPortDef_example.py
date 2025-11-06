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

lib = gdstk.Library()

strt_wg = lib.new_cell("Straight_WG")
vertices1 = [(0, -width1/2), (length, -width1/2), (length, width1/2), (0, width1/2)]

strt_wg.add(gdstk.Polygon(vertices1, layer=1))

lib.write_gds(filename)

##########################################
###         Material Settings          ###
##########################################
SiO2 = ConstMaterial(mat_name="SiO2", epsReal=1.45**2)
Si = ConstMaterial(mat_name="Si", epsReal=3.5**2)

##########################################
###       Layer Stack Settings         ###
##########################################
layer_stack = LayerStack()
layer_stack.addLayer(name="L1", number=1, thickness=0.25, zmin=0.0,
                    material=Si,cladding=SiO2)
layer_stack.addLayer(name="L2", number=2, thickness=0.25, zmin=0.25,
                    material=Si,cladding=SiO2)
layer_stack.setBGandSub(background=SiO2, substrate=SiO2)

##########################################
###   Device Geometry/Port Settings    ###
##########################################
device_geometry = DeviceGeometry()
device_geometry.SetFromGDS(
    layer_stack=layer_stack,
    gds_file=filename,
    buffers={'x':1.5,'y':1.5,'z':1.5})

port0=PortInfo(lines=[[(0.0,-0.25),(0.0,0.25)]],layer_number=1,orientation=180,mode_number=0,buffer=[1.0,1.0])
port1=PortInfo(lines=[[(2.0,-0.25),(2.0,0.25)]],layer_number=1,orientation=0,mode_number=0,buffer=[1.0,1.0])

device_geometry.AddPort(port0)
device_geometry.AddPort(port1)

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
fdtd_solver.SetSimSettings(sim_time=tfinal, space_step=0.05, subpixel_level=2, save_path=r"results",results_filename=filename,
                                                      device_geometry = device_geometry,auto_shutoff_limit=1e-3,export_mat_grid=True)
results = fdtd_solver.Run()
results.PlotSParameters()
results.PlotPermittivity(position=0.11)

