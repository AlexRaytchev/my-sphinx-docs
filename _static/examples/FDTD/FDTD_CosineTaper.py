from pyOptiShared.DeviceGeometry import DeviceGeometry
from pyOptiShared.LayerInfo import LayerStack
from pyOptiShared.Material import ConstMaterial
from pyFDTDKernel.pyFDTDSolver import pyFDTDSolver
import matplotlib.pyplot as plt
import numpy as np
from pyOptiShared.Designs import cosine_taper

input_length:float=0.3
in_width:float=0.5
out_width:float=2
max_width:float=2
taper_length=5.00
resolution:int=40


taper_lib=cosine_taper(input_length,in_width,out_width,max_width,taper_length)

filename='cosine_taper.gds'
taper_lib.write_gds(filename) 

# Define Materials
si02_mat = ConstMaterial(mat_name="SiO2", epsReal=1.45**2,color='lightgreen')
si_mat = ConstMaterial(mat_name="Si", epsReal=3.5**2,color='lightblue')
# Creates the Layer Stack
layer_stack = LayerStack()
layer_stack.AddLayer(name="L1", number=1, thickness=0.22, zmin=0.0,
                    material=si_mat, cladding=si02_mat,
                    sideWallAng=0)

layer_stack.SetBGandSub(background=si02_mat, substrate=si02_mat)

# Defines the Device Geometry
device_geometry = DeviceGeometry()
device_geometry.SetFromGDS(
    layer_stack=layer_stack,
    gds_file=filename,
    buffers={'x':1.5,'y':1.5,'z':1.5}
)
device_geometry.SetAutoPortSettings(direction='x',port_buffer=1)

# General Simulation Settings and Simulation Run
lmin = 1.5
lmax = 1.6
lcen = (lmax+lmin)/2
npts=21
tfinal = 1000

fdtd_solver = pyFDTDSolver()
fdtd_solver.SetExcitation(profile="gaussian-pw", lcenter=lcen, lmin=lmin, lmax=lmax, npts=npts, mode_indices = 0,symmetries='1x1')
fdtd_solver.AddDFTMonitor(mon_type="2d-z-normal", z0=0.11, name="DFTMonitor_z_normal",
                                                      lmin=lmin, lmax=lmax,npts=npts,
                                                      save_hz=True,
                                                      save_hx=True)

fdtd_solver.AddDFTMonitor(mon_type="2d-x-normal", x0=2.0, name="DFTMonitor_x_normal",
                                                      lmin=lmin, lmax=lmax,npts=npts,
                                                      save_hz=True,
                                                      save_hx=True)

fdtd_solver.AddDFTMonitor(mon_type="2d-y-normal", y0=0.0, name="DFTMonitor_y_normal",
                                                      lmin=lmin, lmax=lmax,npts=npts,
                                                      save_hz=True,
                                                      save_hx=True)



fdtd_solver.SetSimSettings(sim_time=tfinal, space_step=0.04, subpixel_level=2, results_path=r"results",device_name='cosine_taper',
                                                      device_geometry = device_geometry,auto_shutoff_limit=1e-3)
results = fdtd_solver.Run()

s21 = results.sparameters['S21'].Get('data')
lam = results.sparameters['S21'].Get('wavelength')


plt.figure()
plt.plot(lam,np.abs(s21),label='mag_s21')
plt.xlabel('Wavelength [um]')
plt.legend()
plt.show()

results.PlotDFTMonitor(mon_name='DFTMonitor_z_normal',field='Hz')
results.PlotDFTMonitor(mon_name='DFTMonitor_x_normal',field='Hz')
results.PlotDFTMonitor(mon_name='DFTMonitor_y_normal',field='Hz')
