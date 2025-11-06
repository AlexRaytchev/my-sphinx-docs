import gdstk
from pyModeSolver.py_mode_solver import VFDModeSolver
from pyOptiShared.LayerInfo import LayerStack
from pyOptiShared.DeviceGeometry import DeviceGeometry
from pyOptiShared.Material import ConstMaterial, ExperimentalMaterial

##########################################
###      Create Fiber GDS File         ###
##########################################
# Create circular fiber core
filename = "fiber.gds"
lib = gdstk.Library()
cell = lib.new_cell("fiber")
circle = gdstk.ellipse((0, 0), 7.5, layer=1)  # 7.5 μm radius
cell.add(circle)
lib.write_gds(filename)

##########################################
###         Material Settings          ###
##########################################
air_mat = ConstMaterial("air", epsReal=1, epsImag=0.0)

# Load silica data from refractiveindex.info database
sio2_mat = ExperimentalMaterial("my_material")
sio2_mat.SetFromRefDotInfo(
    shelf="main",
    book="SiO2",
    page="Malitson",
    wavelength_unit=1e-6
)

##########################################
###       Layer Stack Settings         ###
##########################################
layer_stack = LayerStack()
layer_stack.addLayer(number=1, material=sio2_mat, thickness=0.0,
                     zmin=0, sideWallAng=0, cladding=air_mat)
layer_stack.setBGandSub(background=air_mat, substrate=air_mat)

##########################################
###   Device Geometry/Port Settings    ###
##########################################
device_geometry = DeviceGeometry()
device_geometry.SetFromGDS(
    layer_stack=layer_stack,
    gds_file=filename,
    buffers={'x': 5, 'y': 5, 'z': 5}
)

##########################################
###       ModeSolver Settings          ###
##########################################
mode_solver = VFDModeSolver()

# Set boundary conditions (PMC = Perfect Magnetic Conductor)
mode_solver.SetBoundaries(
    min_x={"bc": "pmc"}, max_x={"bc": "pmc"},
    min_y={"bc": "pmc"}, max_y={"bc": "pmc"}
)

# Configure simulation settings
mode_solver.SetSimSettings(
    device_geometry=device_geometry,
    mesh={"dx": 0.5, "dy": 0.5, "dz": 0.5},
    wavelength={"min": 1.5, "max": 1.6, "npts": 11},
    nguess=3.4,
    nmodes=1,
    cut_plane="XY",      # Cross-section for Z-propagation
    cut_location=0.0,
    tol=1e-8,
    savepath="./ModeResults",
    res_filename="fiber_results"
)

##########################################
###      Run and Post Processing       ###
##########################################
# Run the simulation
results = mode_solver.Run()

# Visualize results
results.PlotMode()                    # Field profiles for all modes
results.PlotPermittivity()            # Material cross-section
results.PlotIndex('neff', modes=[0]) # Effective index vs wavelength
results.PlotIndex('ng', modes=[0])   # Group index vs wavelength