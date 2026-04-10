"""Dielectric Waveguide Example running on FEMFy

"""

import numpy as np
from pyOptiShared.LayerInfo import LayerStack
from pyOptiShared.Material import ConstMaterial, SellmeierMaterial, ExperimentalMaterial
from pyOptiShared.DeviceGeometry import DeviceGeometry
from pyOptiShared.DataStorage import ScatteredField2D
from FEMFy.FEFDSolver import FEFDSolver 
from pyOptiShared.Simulator import PML_Params,Mesh
import matplotlib.pyplot as plt

##########################################
###         Material Settings          ###
##########################################
myindex1p00 = ConstMaterial(mat_name="myindex1p00", epsReal=1.0**2)
myindex1p5 = ConstMaterial(mat_name="myindex1p5", epsReal=1.5**2)
mySellmeier = SellmeierMaterial(mat_name="mySellmeier", b_coeff=[1,2,3], c_coeff=[1,2,3])
myExperimental = ExperimentalMaterial(mat_name="myExperimental", lamb=[1,2,3], values=[1,2,3])
##########################################
###           Mesh Settings            ###
##########################################
fem_mesh=Mesh(dx=0.02,dy=0.02)
fem_mesh.SetMeshOptions(mode='quiet',gui=False,export=True)


layer_stack = LayerStack()
layer_stack.AddMaterial(mySellmeier)
layer_stack.AddMaterial(myExperimental)
layer_stack.AddLayer(name="L1", number=1, thickness=0.25, zmin=0.0,
                     material=myindex1p5, cladding=myindex1p00)
layer_stack.SetBGandSub(background=myindex1p00, substrate=myindex1p00)

##########################################
###   Device Geometry/Port Settings    ###
##########################################

dvc_geometry = DeviceGeometry()
dvc_geometry.SetFromGDS(
    layer_stack=layer_stack,
    gds_file="bend90.gds",
    buffers={'x':2.5,'y':2.5,'z':1.0},
)
dvc_geometry.SetAutoPortSettings(direction='both',min=0.4,max=0.6,port_buffer=1.5,pad=False)
##########################################
###       FEFDSolver Settings          ###
##########################################
fefd_solver = FEFDSolver()

pml=PML_Params()


fefd_solver.SetBoundaries(  min_x = "pml",
                            max_x = "pml",
                            min_y = "pml",
                            max_y = "pml",
                            params=pml)


lams=np.linspace(start=1.5,stop=1.6,num=11)

fefd_solver.SetExcitation(wavelength=lams,
                          reciprocity='1x1')

fefd_solver.SetSimSettings(device_geometry = dvc_geometry,
                           mesh=fem_mesh,
                           method = 'direct',
                           polarization='TE',
                           resolution=800,
                           )

results = fefd_solver.Run()
results.PlotPort()
results.PlotField()
results.PlotNeff()
results.PlotSParameters(s_param="S21")
results.PlotSParameters(s_param="S11")
results.PlotMaterial()
#s21 = results.sparameters['S31'].Get('data')
#lam = results.sparameters['S31'].Get('wavelength')
