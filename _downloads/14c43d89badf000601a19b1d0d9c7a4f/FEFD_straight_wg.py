"""Dielectric Waveguide Example running on FEMFy

"""
import numpy as np
from pyOptiShared.LayerInfo import LayerStack
from pyOptiShared.Material import ConstMaterial, SellmeierMaterial, ExperimentalMaterial
from pyOptiShared.DeviceGeometry import DeviceGeometry
from FEMFy.FEFDSolver import FEFDSolver 
from pyOptiShared.Simulator import PML_Params,Mesh
import matplotlib.pyplot as plt

##########################################
###         Material Settings          ###
##########################################
myindex1p0 = ConstMaterial(mat_name="myindex1p0", epsReal=1.0**2)
myindex1p5 = ConstMaterial(mat_name="myindex3p5", epsReal=1.5**2)
mySellmeier = SellmeierMaterial(mat_name="mySellmeier", b_coeff=[1,2,3], c_coeff=[1,2,3])
myExperimental = ExperimentalMaterial(mat_name="myExperimental", lamb=[1,2,3], values=[1,2,3])

##########################################
###             Layer Stack            ###
##########################################
fem_mesh=Mesh(dx=0.02,dy=0.02,dz=0.02)
fem_mesh.SetMeshOptions(mode='quiet',gui=False,export=True)

layer_stack = LayerStack()
layer_stack.AddMaterial(mySellmeier)
layer_stack.AddMaterial(myExperimental)
layer_stack.AddLayer(name="L1", number=1, thickness=0.25, zmin=0.0,
                     material=myindex1p5, cladding=myindex1p0)
layer_stack.SetBGandSub(background=myindex1p0, substrate=myindex1p0)
### End Layer Stack


##########################################
###           Mesh Settings            ###
##########################################
fem_mesh=Mesh(dx=0.02,dy=0.02,dz=0.02)
fem_mesh.SetMeshOptions(mode='quiet',gui=False,export=True)
### End Mesh Settings

##########################################
###   Device Geometry/Port Settings    ###
##########################################

dvc_geometry = DeviceGeometry()
dvc_geometry.SetFromGDS(
    layer_stack=layer_stack,
    gds_file="straightWG.gds",
    buffers={'x':1.0,'y':1.5,'z':1.0},
)
dvc_geometry.SetAutoPortSettings(direction='x',min=0,max=0.6,port_buffer=1.0,pad=False)

### End Device Geometry

##########################################
###            PML Settings            ###
##########################################
pml=PML_Params()
pml.SetPMLParameters(thickness=[1.0,1.0,0.2,0.2],profile=3,kappa=1,sigma=[1.9,1.9,1.0,1.0],alpha=0.00)
### End PML Settings

##########################################
###       FEFDSolver Settings          ###
##########################################
fefd_solver = FEFDSolver()
fefd_solver.SetBoundaries(  min_x = "pml",
                            max_x = "pml",
                            min_y = "pml",
                            max_y = "pml",
                            params=pml)


lams=np.linspace(start=1.5,stop=1.6,num=3)

fefd_solver.SetExcitation(wavelength=lams,
                          reciprocity='1x1')

fefd_solver.SetSimSettings(device_geometry = dvc_geometry,
                           mesh=fem_mesh,
                           method = 'direct',
                           polarization='TM'
                           )
### End FEFDSolver Settings
##########################################
###         Run and Visualize          ###
##########################################
results = fefd_solver.Run()
results.PlotPort()
results.PlotField()
results.PlotNeff()
results.PlotSParameters(s_param="S21")
### End Visualize
