from pyModeSolver.pyModeSolver import VFDModeSolver
from pyOptiShared.LayerInfo import LayerStack
from pyOptiShared.DeviceGeometry import DeviceGeometry
from pyOptiShared.Material import ConstMaterial
import numpy as np
import gdstk

##########################################
###         Material Settings          ###
##########################################
# Low-index material (n=1.444) for substrate
substrate_mat = ConstMaterial("SiO2", epsReal=1.444**2, epsImag=0.0)

# High-index material (n=3.48) for waveguide core
core_mat = ConstMaterial("Si", epsReal=3.48**2, epsImag=0.0)

##########################################
###       Layer Stack Settings         ###
##########################################
layer_stack = LayerStack()

# Add first layer: 250nm thick at z=0
layer_stack.AddLayer(number=1, material=core_mat, thickness=0.22,
                    zmin=0, sideWallAng=0, cladding="Air_default")

# Set background (above structure) and substrate (below structure)
layer_stack.SetBGandSub(background="Air_default", substrate=substrate_mat)

##########################################
###   Device Geometry/Port Settings    ###
##########################################
len = 5
width = 0.5
layer_core = 1

output_filename = "wg.gds"
lib = gdstk.Library()

strt_wg = lib.new_cell("Straight_WG")
vertices = [(0, -width/2), (len, -width/2), (len, width/2), (0, width/2)]
strt_wg.add(gdstk.Polygon(vertices, layer=layer_core))

lib.write_gds(output_filename)
device_geometry = DeviceGeometry()
device_geometry.SetFromGDS(
    layer_stack=layer_stack,
    gds_file="wg.gds",
    buffers={'x': 1, 'y': 1, 'z': 1}  # 1 μm padding on all sides
)

##########################################
###       ModeSolver Settings          ###
##########################################
mode_solver = VFDModeSolver()

# Set boundary conditions (PMC = Perfect Magnetic Conductor)
mode_solver.SetBoundaries(min_x = "pmc", max_x = "pmc",
                        min_y = "pmc", max_y = "pmc")

lams=np.linspace(start=1.5,stop=1.6,num=21)

# Configure simulation settings
mode_solver.SetSimSettings(
    device_geometry=device_geometry,
    mesh={"dx": 0.025, "dy": 0.025, "dz": 0.025},  # 25nm mesh resolution
    wavelength=lams,         # 1.5-1.6 μm range
    nguess=2.1,              # Initial guess for effective index
    nmodes=1,                # Find first mode
    cut_plane="YZ",          # Cross-section plane (propagation along X)
    cut_location=0.0,        # Position along X-axis
    tol=1e-8,                # Convergence tolerance
    results_path="./ModeResults",
    device_name="my_results"
)

##########################################
###   Run and Results Visualization    ###
##########################################
# Run the simulation
results = mode_solver.Run()

# Visualize results
results.PlotMode(field='Hx')                # Field profiles
results.PlotPermittivity()                  # Material cross-section
results.PlotIndex('neff', modes=[0]) # Effective index vs wavelength
results.PlotIndex('ng', modes=[0])   # Group index vs wavelength
results.ExportNeff("StraightWG-neffData", 0) # Exports effective index data in a .txt format
results.ExportNg("StraightWG-ngData", 0) # Exports group index data in a .txt format