from pyOptiShared.LayerInfo import LayerStack
from pyOptiShared.Material import ConstMaterial
from pyOptiShared.DeviceGeometry import DeviceGeometry
from pyFDTDKernel.pyFDTDSolver import pyFDTDSolver

##########################################
###         Material Settings          ###
##########################################
SiO2_mat = ConstMaterial(mat_name="SiO2", epsReal=1.445**2)
Si_mat = ConstMaterial(mat_name="Si", epsReal=3.455**2)

##########################################
###       Layer Stack Settings         ###
##########################################
layer_stack = LayerStack()
layer_stack.AddLayer(name="L0", number=0, thickness=0.2, zmin=0.0,
                    material=Si_mat, cladding=Si_mat)
layer_stack.AddLayer(name="L1", number=1, thickness=0.2, zmin=0.2,
                    material=Si_mat, cladding="Air_default")
layer_stack.SetBGandSub(background="Air_default", substrate=SiO2_mat)

##########################################
###   Device Geometry/Port Settings    ###
##########################################
device_geometry = DeviceGeometry()
device_geometry.SetFromGDS(
    layer_stack=layer_stack,
    gds_file=r"Ridge_Taper_WG_pol_converter.gds",
    buffers={'x':1.5,'y':1.5,'z':1.5}
)
device_geometry.SetAutoPortSettings(
    direction="x",
    port_buffer=1.0,
    min=0.1,
    max=8.5,
)


##########################################
###          FDTD Settings             ###
##########################################
fdtd_solver = pyFDTDSolver()
fdtd_solver.SetExcitation(profile="gaussian-pw", lcenter=1.5, lmin=1.45, lmax=1.55, npts=21, mode_indices=[2,2])
fdtd_solver.AddDFTMonitor(mon_type="2d-z-normal", z0=0.2, name="MyDFTMonitor1",
                          lmin=1.45, lmax=1.55,npts=3,
                          save_ex=True, save_ey=True)
fdtd_solver.SetBoundaries()
fdtd_solver.SetSimSettings(sim_time=50000, space_step=0.050, subpixel_level=1, results_path=r"results",
                          device_geometry = device_geometry, export_mat_grid=True, show_modes=True)

# ##########################################
# ###      Run and Post Processing       ###
# ##########################################
results = fdtd_solver.Run()
