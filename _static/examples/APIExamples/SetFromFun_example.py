from pyOptiShared.DeviceGeometry import DeviceGeometry
from pyOptiShared.LayerInfo import LayerStack
from pyOptiShared.Material import ConstMaterial
from pyFDTDKernel.pyFDTDSolver import pyFDTDSolver

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon


si02_mat = ConstMaterial(mat_name="SiO2", epsReal=1.45**2,color='lightgreen')
si_mat = ConstMaterial(mat_name="Si", epsReal=3.5**2,color='lightblue')
air_mat = ConstMaterial(mat_name="Air", epsReal=1**2,color='lightyellow')

layer_stack = LayerStack()

layer_stack.AddLayer(name="L1", number=1, thickness=0.22, zmin=0.0,
                        material=si_mat, cladding=si02_mat,
                        sideWallAng=20)


layer_stack.SetBGandSub(background=air_mat, substrate=si02_mat)

device_geometry = DeviceGeometry()
    
def waveguide(port_width=0.4,waveguide_length=1.00,input_port_center=(0,0),layer=1):
    vertices=[(input_port_center[0],input_port_center[1]-(port_width/2)),
                (input_port_center[0]+waveguide_length,input_port_center[1]-(port_width/2)),
                (input_port_center[0]+waveguide_length,input_port_center[1]+(port_width/2)),
                (input_port_center[0],input_port_center[1]+(port_width/2))]
    
    return [(vertices,layer)] 

parameters=(0.4,1.00,(0,0),1) # (port_width,waveguide_length,input_port_center,layer)

WG1=waveguide(*parameters)
vertices=WG1[0][0]

fig, ax = plt.subplots()
polygon = Polygon(vertices, closed=True, facecolor="lightcoral", edgecolor="black")
ax.add_patch(polygon)
plt.ylim([-1,1])
plt.show()

device_geometry.SetFromFun(func=waveguide
                   ,layer_stack=layer_stack
                   ,parameters=parameters
                   ,buffers={'x':1.5,'y':1.5,'z':1.5}
                   )

# Automatically detect ports along the x-direction
device_geometry.SetAutoPortSettings(
   direction='x',
   port_buffer=1.0
)

# General Simulation Settings and Simulation Run
lmin = 1.5
lmax = 1.6
lcen = (lmax+lmin)/2
npts=21
tfinal = 550
fdtd_solver = pyFDTDSolver()
fdtd_solver.SetExcitation(profile="gaussian-pw", lcenter=lcen, lmin=lmin, lmax=lmax, npts=npts, mode_indices = 0,symmetries='1x1')
fdtd_solver.AddDFTMonitor(mon_type="2d-z-normal", z0=0.11, name="MyDFTMonitor1",
                                                      lmin=lmin, lmax=lmax,npts=npts,
                                                      save_hz=True)
fdtd_solver.SetSimSettings(sim_time=tfinal, space_step=0.05, subpixel_level=2, results_path=r"results",device_name='wg',
                                                      device_geometry = device_geometry,auto_shutoff_limit=1e-3,export_mat_grid=True)
results = fdtd_solver.Run()
results.PlotSParameters()
results.PlotPermittivity(position=0.11)