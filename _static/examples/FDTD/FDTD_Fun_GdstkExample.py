from pyOptiShared.DeviceGeometry import DeviceGeometry
from pyOptiShared.LayerInfo import LayerStack
from pyOptiShared.Material import ConstMaterial
from pyFDTDKernel.pyFDTDSolver import pyFDTDSolver
from pyOptiShared.Designs import flex_taper
import numpy as np

# Material Settings
si02_mat = ConstMaterial(mat_name="SiO2", epsReal=1.45**2,color='lightgreen')
si_mat = ConstMaterial(mat_name="Si", epsReal=3.5**2,color='lightblue')
air_mat = ConstMaterial(mat_name="Air", epsReal=1**2,color='lightyellow')

# Layer Stack Settings
layer_stack = LayerStack()
layer_stack.AddLayer(name="L1", number=1, thickness=0.22, zmin=0.0,
                    material=si_mat, cladding=si02_mat,
                    sideWallAng=0)
layer_stack.SetBGandSub(background=si02_mat, substrate=si02_mat)


widths=np.linspace(0.3,1.0,5)
parameters=(widths,0.3,1.0,0.5,2.0,20,1,False)

#Device Geometry Settings
device_geometry = DeviceGeometry()

device_geometry.SetFromFun(
    layer_stack=layer_stack,
    func=flex_taper,
    parameters=parameters,
    buffers={'x':1.5,'y':1.5,'z':1.5})

device_geometry.SetAutoPortSettings(direction='x',port_buffer=1)

# Simulation Settings and Runs
lmin = 1.5
lmax = 1.6
lcen = (lmax+lmin)/2
npts=3
tfinal = 1500

fdtd_solver = pyFDTDSolver()
fdtd_solver.SetExcitation(profile="gaussian-pw", lcenter=lcen, lmin=lmin, lmax=lmax, npts=npts, mode_indices=0,symmetries='1x1')
fdtd_solver.AddDFTMonitor(mon_type="2d-z-normal", z0=0.11, name="MyDFTMonitor1",
                        lmin=lmin, lmax=lmax,npts=npts,
                        save_ex=True, save_ey=True, save_ez=True,
                        save_hx=True, save_hy=True, save_hz=True)
    
fdtd_solver.SetSimSettings(sim_time=tfinal, space_step=0.0250, subpixel_level=2, results_path=r"results",device_name='flex_taper',
                        device_geometry = device_geometry,export_mat_grid=True)

results = fdtd_solver.Run()

results.PlotDFTMonitor('MyDFTMonitor1',field='Ey')