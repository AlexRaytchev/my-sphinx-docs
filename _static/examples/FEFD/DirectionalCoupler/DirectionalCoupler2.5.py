from pyOptiShared.DeviceGeometry import DeviceGeometry
from pyOptiShared.LayerInfo import LayerStack
from pyOptiShared.Material import ConstMaterial
import matplotlib.pyplot as plt
from FEMFy.FEFDSolver import FEFDSolver
from pyOptiShared.Simulator import PML_Params,Mesh
import numpy as np

import gdstk

filename = "DirectionalCoupler2.5.gds"

length = 11
width1 = 0.5
width2 = 0.5
gap = 0.15+0.25
lib = gdstk.Library()
shift=1.0
strt_wg = lib.new_cell("Straight_WG")
vertices1 = [(shift+0, -width1/2+gap), (shift+length, -width1/2+gap), (shift+length, width1/2+gap), (shift+0, width1/2+gap)]
vertices2 = [(0, -width2/2-gap), (length, -width2/2-gap), (length, width2/2-gap), (0, width2/2-gap)]

strt_wg.add(gdstk.Polygon(vertices1, layer=1))
strt_wg.add(gdstk.Polygon(vertices2, layer=1))

lib.write_gds(filename)



# Define Materials
si02_mat = ConstMaterial(mat_name="SiO2", epsReal=1.45**2,color='lightgreen')
sin_mat = ConstMaterial(mat_name="SiN", epsReal=1.99**2,color='lightblue')

# Creates the Layer Stack
layer_stack = LayerStack()
layer_stack.AddLayer(name="L1", number=1, thickness=0.22, zmin=0.0,
                        material=sin_mat, cladding=si02_mat)

layer_stack.SetBGandSub(background=si02_mat, substrate=si02_mat)

# Defines the Device Geometry
device_geometry = DeviceGeometry()
device_geometry.SetFromGDS(
    layer_stack=layer_stack,
    gds_file=filename,
    buffers={'x':1.0,'y':2.0,'z':1.0}
)
device_geometry.SetAutoPortSettings(direction='x',port_buffer=2,pad=True)

# General Simulation Settings and Simulation Run
lmin = 1.5
lmax = 1.6
lcen = (lmax+lmin)/2


##########################################
###           Mesh Settings            ###
##########################################
fem_mesh=Mesh(dx=0.02,dy=0.02,dz=0.02)
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


lams=np.linspace(start=1.5,stop=1.6,num=5)
fefd_solver.SetExcitation(wavelength=lams,
                          reciprocity='1x1')

fefd_solver.SetSimSettings(device_geometry = device_geometry,
                           mesh=fem_mesh,
                           wavelength=lams,
                           stability = 1.0,
                           resolution = 800,
                           interpolation = "FEM",
                           method = 'direct',
                           polarization='TM2.5',
                           number_iterations=2,
                           results_path='',
                           )


fefd_results = fefd_solver.Run()
fefd_results.PlotField()
fefd_results.PlotPort()
fefd_results.PlotSParameters(s_param="S21")


