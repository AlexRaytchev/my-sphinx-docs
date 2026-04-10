from pyOptiShared.DeviceGeometry import DeviceGeometry
from pyOptiShared.LayerInfo import LayerStack
from pyOptiShared.Material import ConstMaterial
import matplotlib.pyplot as plt
from FEMFy.FEFDSolver import FEFDSolver
from pyOptiShared.Simulator import PML_Params,Mesh
from pyOptiShared.Designs import cosine_taper
import numpy as np

import gdstk
input_length:float=0.8
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
                        material=si_mat, cladding=si02_mat)

layer_stack.SetBGandSub(background=si02_mat, substrate=si02_mat)

# Defines the Device Geometry
device_geometry = DeviceGeometry()
device_geometry.SetFromGDS(
    layer_stack=layer_stack,
    gds_file=filename,
    buffers={'x':2.0,'y':2.0,'z':1.0}
)
device_geometry.SetAutoPortSettings(direction='x',port_buffer=2.5,pad=False)

# General Simulation Settings and Simulation Run
lmin = 1.5
lmax = 1.6



##########################################
###           Mesh Settings            ###
##########################################
fem_mesh=Mesh(dx=0.02,dy=0.02,dz=0.02)
fem_mesh.SetMeshOptions(mode='quiet',gui=False,export=False)
##########################################
###       FEFDSolver Settings          ###
##########################################
fefd_solver = FEFDSolver()

pml=PML_Params()

fefd_solver.SetBoundaries( min_x = "pml",
                            max_x = "pml",
                            min_y = "pml",
                            max_y = "pml",params=pml)


lams=np.linspace(start=1.5,stop=1.6,num=21)
fefd_solver.SetExcitation(wavelength=lams,
                          reciprocity='1x1')

fefd_solver.SetSimSettings(device_geometry = device_geometry,
                           mesh=fem_mesh,
                           wavelength=lams,
                           resolution = 800,
                           interpolation = "FEM",
                           method = 'direct',
                           polarization='TM2.5',
                           number_iterations=2,
                           results_path='',
                           )


fefd_results = fefd_solver.Run()
fefd_results.PlotField(1.55)
fefd_results.PlotPort()
fefd_results.PlotSParameters(s_param="S21")


