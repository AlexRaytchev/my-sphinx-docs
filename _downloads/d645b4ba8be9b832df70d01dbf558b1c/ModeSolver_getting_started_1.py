##########################################
###           Import Modules           ###
##########################################
from pyModeSolver.pyModeSolver import VFDModeSolver
from pyOptiShared.LayerInfo import LayerStack
from pyOptiShared.DeviceGeometry import DeviceGeometry
from pyOptiShared.Material import ConstMaterial
import gdstk
import numpy as np

### End Import Modules

##########################################
###         Material Settings          ###
##########################################
# Low-index material (n=1.444) for substrate
substrate_mat = ConstMaterial("SiO2", epsReal=1.444**2, epsImag=0.0)

# High-index material (n=3.48) for waveguide core
core_mat = ConstMaterial("Si", epsReal=3.48**2, epsImag=0.0)

### End Material Settings

##########################################
###       Layer Stack Settings         ###
##########################################
layer_stack = LayerStack()

# Add first layer: 250nm thick at z=0
layer_stack.AddLayer(number=1, material=core_mat, thickness=0.22, 
                    zmin=0, sideWallAng=0, cladding="Air_default")

# Add second layer: 250nm thick at z=0.25μm
layer_stack.AddLayer(number=2, material=core_mat, thickness=0.09, 
                    zmin=0, sideWallAng=0, cladding="Air_default")

# Set background (above structure) and substrate (below structure)
layer_stack.SetBGandSub(background="Air_default", substrate=substrate_mat)

### End Layer Stack
########################################
###  Create GDS mask for the device  ###
########################################
filename = "wg.gds"

length = 10
width1 = 0.5
width2 = 2

lib = gdstk.Library()

strt_wg = lib.new_cell("Straight_WG")
vertices1 = [(0, -width1/2), (length, -width1/2), (length, width1/2), (0, width1/2)]
vertices2 = [(0, -width2/2), (length, -width2/2), (length, width2/2), (0, width2/2)]

strt_wg.add(gdstk.Polygon(vertices1, layer=1))
strt_wg.add(gdstk.Polygon(vertices2, layer=2))

lib.write_gds(filename)


### End GDS mask

##########################################
###   Device Geometry/Port Settings    ###
##########################################
device_geometry = DeviceGeometry()
device_geometry.SetFromGDS(
    layer_stack=layer_stack,
    gds_file="wg.gds",
    buffers={'x': 1, 'y': 1, 'z': 1}  # 1 μm padding on all sides
)

### End Device Geometry

##########################################
###       ModeSolver Settings          ###
##########################################
mode_solver = VFDModeSolver()

# Set boundary conditions (PMC = Perfect Magnetic Conductor)
mode_solver.SetBoundaries(min_x = "pmc", max_x = "pmc",
                        min_y = "pmc", max_y = "pmc")

# Configure simulation settings
lams=np.linspace(start=1.5,stop=1.6,num=5)
mode_solver.SetSimSettings(
    device_geometry=device_geometry,
    mesh={"dx": 0.025, "dy": 0.025, "dz": 0.025},  # 25nm mesh resolution
    wavelength=lams,  # 1.5-1.6 μm range
    nguess=2.1,              # Initial guess for effective index
    nmodes=4,                # Find first 4 modes
    cut_plane="YZ",          # Cross-section plane (propagation along X)
    cut_location=0.0,        # Position along X-axis
    tol=1e-8,                # Convergence tolerance
    results_path="./ModeResults",
    device_name="my_results"
)


### End ModeSolver Settings

##########################################
###   Run and Results Visualization    ###
##########################################
# Run the simulation
results = mode_solver.Run()

# Visualize results
results.PlotMode(field='Hy')               # Field profile of the fundamental mode
results.PlotPermittivity()                 # Material cross-section
results.PlotIndex('neff', modes=[0,1,2,3]) # Effective index vs wavelength
results.PlotIndex('ng', modes=[0,1,2,3])   # Group index vs wavelength

### End Run and Results