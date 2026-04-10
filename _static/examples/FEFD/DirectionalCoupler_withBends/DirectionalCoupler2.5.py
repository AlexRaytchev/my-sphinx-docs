from pyOptiShared.DeviceGeometry import DeviceGeometry
from pyOptiShared.LayerInfo import LayerStack
from pyOptiShared.Material import ConstMaterial
import matplotlib.pyplot as plt
from FEMFy.FEFDSolver import FEFDSolver
from pyOptiShared.Simulator import PML_Params,Mesh
from pyFDTDKernel.FDTDResults import FDTDResults
import numpy as np


filename = "coupler.gds"

# Define Materials
si02_mat = ConstMaterial(mat_name="SiO2", epsReal=1.45**2,color='lightgreen')
si_mat = ConstMaterial(mat_name="Si", epsReal=3.5**2,color='lightblue')

# Creates the Layer Stack
layer_stack = LayerStack()
layer_stack.AddLayer(name="L1", number=1, thickness=0.22, zmin=0.0,
                        material=si_mat, cladding=si02_mat)

layer_stack.SetBGandSub(background=si02_mat, substrate=si02_mat)

# Defines the Device Geometry
device_geometry = DeviceGeometry()
device_geometry.SetFromGDS(
    layer_stack=layer_stack,
    gds_file=filename,
    buffers={'x':1.0,'y':3.0,'z':1.0}
)
device_geometry.SetAutoPortSettings(direction='x',port_buffer=2,pad=False)

# General Simulation Settings and Simulation Run
lmin = 1.5
lmax = 1.6
lcen = (lmax+lmin)/2


##########################################
###           Mesh Settings            ###
##########################################
fem_mesh=Mesh(dx=0.04,dy=0.04,dz=0.04)
fem_mesh.SetMeshOptions(mode='quiet',gui=False,export=True)
##########################################
###       FEFDSolver Settings          ###
##########################################
fefd_solver = FEFDSolver()

pml=PML_Params()

fefd_solver.SetBoundaries( min_x = "pml",
                            max_x = "pml",
                            min_y = "pml",
                            max_y = "pml",params=pml)


lams=np.linspace(start=1.5,stop=1.6,num=25)
fefd_solver.SetExcitation(wavelength=lams,
                          reciprocity='2x2')

fefd_solver.SetSimSettings(device_geometry = device_geometry,
                           mesh=fem_mesh,
                           wavelength=lams,
                           resolution = 200,
                           interpolation = "nearest",
                           method = 'direct',
                           polarization='TM2.5',
                           number_iterations=2,
                           results_path='',
                           order=2
                           )


fefd_results = fefd_solver.Run()
fefd_results.PlotField()
fefd_results.PlotSParameters("S31")
fefd_results.PlotSParameters("S41")
fefd_results.PlotPort()


fefd_S31=fefd_results.sparameters['S31'].Get('data')

lam=fefd_results.sparameters['S31'].Get('wavelength')
fefd_S41=fefd_results.sparameters['S41'].Get('data')

plt.figure()
plt.plot(lam,abs(fefd_S31),'--o',label='Abs S31_FEFD')
plt.ylim([0.3,1])
plt.xlabel('wavelength [um]')
plt.legend()



plt.figure()
plt.plot(lam,abs(fefd_S41),'--o',label='Abs S41_FEFD')
plt.xlabel('wavelength [um]')
plt.ylim([0.3,1])
plt.legend()

plt.show()

