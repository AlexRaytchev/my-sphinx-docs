from pyOptiShared.LayerInfo import LayerStack
from pyOptiShared.Material import ConstMaterial
from pyOptiShared.DeviceGeometry import DeviceGeometry
from pyFDTDKernel.pyFDTDSolver import pyFDTDSolver

##########################################
###         Material Settings          ###
##########################################
SiO2 = ConstMaterial(mat_name="SiO2", epsReal=1.45**2)
Si = ConstMaterial(mat_name="Si", epsReal=3.5**2)

##########################################
###       Layer Stack Settings         ###
##########################################
layer_stack = LayerStack()
layer_stack.addLayer(name="L1", number=1, thickness=0.22, zmin=0.0,
                    material=Si, cladding="Air_default")
layer_stack.addLayer(name="L2", number=2, thickness=0.13, zmin=0.0,
                    material=Si, cladding="Air_default")
layer_stack.setBGandSub(background="Air_default", substrate=SiO2)

##########################################
###   Device Geometry/Port Settings    ###
##########################################
device_geometry = DeviceGeometry()
device_geometry.SetFromGDS(
    layer_stack=layer_stack,
    gds_file=r"etchedCrossing.gds",
    buffers={'x':1.5,'y':1.5,'z':1.5}
)
device_geometry.SetAutoPortSettings(
    direction="both",
    port_buffer=1.0,
)

device_geometry.PlotGDS()
device_geometry.PlotGDSXSection(direction='y',pos=-1.5)

##########################################
###          FDTD Settings             ###
##########################################
fdtd_solver = pyFDTDSolver()
fdtd_solver.SetPorts(profile="gaussian-pw", lcenter=1.55, lmin=1.5, lmax=1.6, npts=21, mode_indices=0,
                    symmetries = {"1_2":"2_1","2_2":"1_1","3_2":"4_1","4_2":"3_1",
                                  "1_3":"3_1","2_3":"3_1","3_3":"1_1","4_3":"2_1",
                                  "1_4":"4_1","2_4":"4_1","3_4":"2_1","4_4":"1_1",})
fdtd_solver.AddDFTMonitor(mon_type="2d-z-normal", z0=0.125, name="MyDFTMonitor1",
                          lmin=1.5, lmax=1.6,npts=12,
                          save_ex=True, save_ey=True, save_ez=True,
                          save_hx=True, save_hy=True, save_hz=True)
fdtd_solver.SetBoundaries()
fdtd_solver.SetSimSettings(sim_time=1500, space_step=0.050, subpixel_level=2, save_path=r"results",results_filename='etchedCrossing',
                          device_geometry = device_geometry, export_mat_grid=True)

##########################################
###      Run and Post Processing       ###
##########################################
results = fdtd_solver.Run()
results.PlotSParameters(snp='ALL',plot_type='power')
results.PlotDFTMonitor('MyDFTMonitor1',field='Hx')
results.PlotSParameters(snp='ALL',plot_type='phase')