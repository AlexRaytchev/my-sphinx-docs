from pyOptiShared.DeviceGeometry import DeviceGeometry
from pyOptiShared.LayerInfo import LayerStack
from pyOptiShared.Material import ConstMaterial
from pyFDTDKernel.pyFDTDSolver import pyFDTDSolver
import gdstk

##########################################
###         Material Settings          ###
##########################################
# Silicon dioxide (n=1.444) for substrate and cladding
sio2_mat = ConstMaterial(mat_name="SiO2", epsReal=1.444**2, color='lightgreen')

# Silicon (n=3.48) for waveguide core
si_mat = ConstMaterial(mat_name="Si", epsReal=3.48**2, color='lightblue')

# Air (n=1.0) for background
air_mat = ConstMaterial(mat_name="Air", epsReal=1**2, color='lightyellow')

### End Material Settings

##########################################
###       Layer Stack Settings         ###
##########################################
layer_stack = LayerStack()

# Add silicon layer: 220nm thick starting at z=0
layer_stack.AddLayer(
   name="L1", 
   number=1, 
   thickness=0.22, 
   zmin=0.0,
   material=si_mat, 
   cladding=air_mat,
   sideWallAng=0
)

# Set background (above structure) and substrate (below structure)
layer_stack.SetBGandSub(background=air_mat, substrate=sio2_mat)

### End Layer Stack

##########################################
###   Device Geometry/Port Settings    ###
##########################################



#Create GDS mask for the device
length = 10
width = 0.5
layer_core = 1

output_filename = "waveguide.gds"
lib = gdstk.Library()

strt_wg = lib.new_cell("Straight")
vertices = [(0, -width/2), (length, -width/2), (length, width/2), (0, width/2)]
strt_wg.add(gdstk.Polygon(vertices, layer=layer_core))

lib.write_gds(output_filename)


device_geometry = DeviceGeometry()
device_geometry.SetFromGDS(
   layer_stack=layer_stack,
   gds_file='waveguide.gds',
   buffers={'x': 1.5, 'y': 1.5, 'z': 1.5}
)

# Automatically detect ports along the x-direction
device_geometry.SetAutoPortSettings(
   direction='x',
   port_buffer=1.0
)

device_geometry.PlotGDS()
device_geometry.PlotGDSXSection(direction='y',pos=2)
### End Device Geometry

##########################################
###          FDTD Settings             ###
##########################################

### Configure the FDTD Solver

# Define wavelength range
lmin = 1.5   # Minimum wavelength (μm)
lmax = 1.6   # Maximum wavelength (μm)
lcen = (lmax + lmin) / 2  # Center wavelength
npts = 21    # Number of frequency points

fdtd_solver = pyFDTDSolver()

# Configure port excitation with Gaussian pulse
fdtd_solver.SetExcitation(
   profile="gaussian-pw",
   lcenter=lcen,
   lmin=lmin,
   lmax=lmax,
   npts=npts,
   mode_indices=0,
   symmetries='1x1'
)

### End Configure the FDTD Solver
### Add Monitors

# Add DFT monitor to capture frequency-domain fields
fdtd_solver.AddDFTMonitor(
   mon_type="2d-z-normal",
   z0=0.11,
   name="MyDFTMonitor1",
   lmin=lmin,
   lmax=lmax,
   npts=npts,
   save_ex=True,
   save_ey=True,
   save_hz=True
)

### End Add Monitors

###  Set Simulation Parameters

# Configure simulation parameters
fdtd_solver.SetSimSettings(
   sim_time=350,
   space_step=0.05,
   subpixel_level=2,
   results_path="./results",
   device_name='waveguide',
   device_geometry=device_geometry,
   auto_shutoff_limit=1e-2,
   export_mat_grid=True
)

### End Set Simulation Parameters

### End FDTD Settings

##########################################
###      Run and Post Processing       ###
##########################################
# Run the simulation
results = fdtd_solver.Run()

# Plot S-parameters
results.PlotSParameters(snp='ALL', plot_type='power')
results.PlotSParameters(snp='ALL', plot_type='phase')

### End Run and Post Processing
