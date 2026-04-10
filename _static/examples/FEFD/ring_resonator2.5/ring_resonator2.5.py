"""Dielectric Waveguide Example running on FEMFy

"""


import numpy as np
from pyOptiShared.LayerInfo import LayerStack
from pyOptiShared.Material import ConstMaterial, SellmeierMaterial, ExperimentalMaterial
from pyOptiShared.DeviceGeometry import DeviceGeometry
from FEMFy.FEFDSolver import FEFDSolver 
from pyOptiShared.Simulator import PML_Params,Mesh
import matplotlib.pyplot as plt
from pyOptiShared.Utilities import loadsnpfile




##########################################
###         Material Settings          ###
##########################################
si02_mat = ConstMaterial(mat_name="SiO2", epsReal=1.45**2,color='lightgreen')
si_mat = ConstMaterial(mat_name="Si", epsReal=3.5**2,color='red')


# Creates the Layer Stack
layer_stack = LayerStack()
layer_stack.AddLayer(name="L1", number=1, thickness=0.22, zmin=0.0,
                    material=si_mat, cladding=si02_mat,
                    sideWallAng=0)
layer_stack.SetBGandSub(background=si02_mat, substrate=si02_mat)
##########################################
###   Device Geometry/Port Settings    ###
##########################################
port_center=[(0,0)]
port1_width=[0.5]
port2_width=[1.0]
taper_length=[10]
layer=[1]
init_params=(port_center,port1_width,port2_width,taper_length,layer)



dvc_geometry = DeviceGeometry()
dvc_geometry.SetFromGDS(
    layer_stack=layer_stack,
    gds_file="double_ring_100.gds",
    buffers={'x':1.0,'y':2,'z':1.0}
)
dvc_geometry.SetAutoPortSettings(direction='x',min=0,max=0.6,port_buffer=0.8,pad=False)
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
# pml.SetMinX(thickness=1.6,profile=2,kappa=1,sigma=1.6,alpha=0.00)
# pml.SetMaxX(thickness=1.6,profile=2,kappa=1,sigma=1.6,alpha=0.00)
# pml.SetMinY(thickness=0.1,profile=2,kappa=1,sigma=1.0,alpha=0.00)
# pml.SetMaxY(thickness=0.1,profile=2,kappa=1,sigma=1.0,alpha=0.00)

fefd_solver.SetBoundaries( min_x = "pml",
                            max_x = "pml",
                            min_y = "pml",
                            max_y = "pml",params=pml)


lams=np.linspace(start=1.547,stop=1.555,num=101)
fefd_solver.SetExcitation(wavelength=lams,
                          reciprocity='2x2')

fefd_solver.SetSimSettings(device_geometry = dvc_geometry,
                           mesh=fem_mesh,
                           wavelength=lams,
                           stability = 1,
                           resolution = 400,
                           interpolation = "cubic",
                           method = 'direct',
                           polarization='TM2.5',
                           number_iterations=2,
                           results_path='',
                           adjoint_info=None
                           )



fefd_results = fefd_solver.Run()
fefd_results.PlotField(target_wavelength=1.551)
fefd_results.PlotNeff()
fem_lam=fefd_results.GetNeffData()[0]
fem_neff=fefd_results.GetNeffData()[1]
s31=fefd_results.sparameters['S31'].Get('data')
lam=fefd_results.sparameters['S31'].Get('wavelength')
plt.figure()
plt.plot(lam,np.abs(s31),label='FEM |S31|')
plt.xlim([1.547,1.555])
plt.xlabel('Wavelength [um]')
fefd_results.PlotPort()
fefd_results.PlotSParameters(s_param="S31")
fefd_results.PlotSParameters(s_param="S21")
plt.show()
