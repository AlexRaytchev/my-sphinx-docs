from pyOptiShared.DeviceGeometry import DeviceGeometry
from pyOptiShared.LayerInfo import LayerStack
from pyOptiShared.Material import ConstMaterial
from pyFDTDKernel.pyFDTDSolver import pyFDTDSolver

import gdsfactory as gf
import numpy as np
import matplotlib.pyplot as plt

def dir_coupler(gap:float=0.1,length:float=5.0)->gf.Component:
    c = gf.Component()
    coupler = gf.components.coupler(gap=gap,length=length)
    ref = c.add_ref(coupler)
    return c


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

#Device Geometry Settings
device_geometry = DeviceGeometry()

device_geometry.SetFromFun(
            layer_stack=layer_stack,
            func=dir_coupler,
            parameters=(0.1,0),
            buffers={'x':1.0,'y':1.0,'z':1.0})

device_geometry.SetAutoPortSettings(direction='x',port_buffer=1,min=[0.1,0.51],max=[0.55,0.55])

# Simulation Settings and Runs
lmin = 1.5
lmax = 1.6
lcen = (lmax+lmin)/2
npts=3
tfinal = 1500

length = np.linspace(0,7.5,10)

s31_data = list()
s41_data = list()


for ii in range(0,len(length)):

    L = length[ii]

    script_parameters = (0.1,L)

    device_geometry.UpdateScriptParams(script_parameters)
    fdtd_solver = pyFDTDSolver()
    fdtd_solver.SetExcitation(profile="gaussian-pw", lcenter=lcen, lmin=lmin, lmax=lmax, npts=npts, mode_indices=0,symmetries='2x2')
    fdtd_solver.AddDFTMonitor(mon_type="2d-z-normal", z0=0.11, name="MyDFTMonitor1",
                            lmin=lmin, lmax=lmax,npts=npts,
                            save_ex=True, save_ey=True, save_ez=True,
                            save_hx=True, save_hy=True, save_hz=True)


        
    fdtd_solver.SetSimSettings(sim_time=tfinal, space_step=0.05, subpixel_level=2, results_path=r"results",device_name='coupler',
                            device_geometry = device_geometry,export_mat_grid=True)
    results = fdtd_solver.Run()

    S31 = results.sparameters['S31'].Get('data')
    s31_data.append(abs(S31[1])**2)

    S41 = results.sparameters['S41'].Get('data')
    s41_data.append(abs(S41[1])**2)



results.PlotDFTMonitor(mon_name='MyDFTMonitor1',field='Ey')


plt.plot(length,s31_data,label='S31')
plt.plot(length,s41_data,label='S41')
plt.xlabel('Coupler Length (um)')
plt.legend()
plt.ylim([0,1])
plt.show()
