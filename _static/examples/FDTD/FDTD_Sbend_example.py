from pyOptiShared.DeviceGeometry import DeviceGeometry
from pyOptiShared.LayerInfo import LayerStack
from pyOptiShared.Material import ConstMaterial
from pyFDTDKernel.pyFDTDSolver import pyFDTDSolver

si02_mat = ConstMaterial(mat_name="SiO2", epsReal=1.45**2,color='lightgreen')
si_mat = ConstMaterial(mat_name="Si", epsReal=3.5**2,color='lightblue')
air_mat = ConstMaterial(mat_name="Air", epsReal=1**2,color='lightyellow')

layer_stack = LayerStack()
layer_stack.addLayer(name="L1", number=1, thickness=0.22, zmin=0.0,
                    material=si_mat, cladding=si02_mat,
                    sideWallAng=0)
layer_stack.setBGandSub(background=si02_mat, substrate=si02_mat)

device_geometry = DeviceGeometry()
device_geometry.SetFromGDS(
    layer_stack=layer_stack,
    gds_file='sbend.gds',
    buffers={'x':1.5,'y':1.5,'z':1.5}
)
device_geometry.SetAutoPortSettings(direction='x',port_buffer=1)

lmin = 1.5
lmax = 1.6
lcen = (lmax+lmin)/2
npts=21
tfinal = 350

fdtd_solver = pyFDTDSolver()
fdtd_solver.SetPorts(profile="gaussian-pw", lcenter=lcen, lmin=lmin, lmax=lmax, npts=npts, mode_indices = 0,symmetries='1x1')
fdtd_solver.AddTimeMonitor(mon_type="2d-z-normal", z0=0.11, name="MyTimeMonitor1",
                          npts=200,
                          save_hx=False,save_hy=False, save_hz=True)
fdtd_solver.SetSimSettings(sim_time=tfinal, space_step=0.05, subpixel_level=2, save_path=r"results",results_filename='sbend',
                        device_geometry = device_geometry,auto_shutoff_limit=1e-2, export_mat_grid=True)
results = fdtd_solver.Run()
