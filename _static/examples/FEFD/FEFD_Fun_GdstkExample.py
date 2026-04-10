from pyOptiShared.DeviceGeometry import DeviceGeometry
from pyOptiShared.LayerInfo import LayerStack
from pyOptiShared.Material import ConstMaterial
from pyOptiShared.Designs import flex_taper
from FEMFy.FEFDSolver import FEFDSolver
from pyOptiShared.Simulator import PML_Params, Mesh
import matplotlib.pyplot as plt
import numpy as np

# ==========================================
# 1. Material Definitions
# ==========================================
# Define materials needed for the simulation.
si02_mat = ConstMaterial(mat_name="SiO2", epsReal=1.45**2, color='lightgreen')
si_mat = ConstMaterial(mat_name="Si", epsReal=3.5**2, color='lightblue')
air_mat = ConstMaterial(mat_name="Air", epsReal=1**2, color='lightyellow')


# ==========================================
# 2. Layer Stack Configuration
# ==========================================
# Define the layer stack.
# Note that even when using GDStk/Library functions, we must still assign
# the geometry to a specific layer number (here, layer 1) defined in this stack.
layer_stack = LayerStack()
layer_stack.AddLayer(name="L1", number=1, thickness=0.22, zmin=0.0,
                     material=si_mat, cladding=si02_mat,
                     sideWallAng=0)
layer_stack.SetBGandSub(background=si02_mat, substrate=si02_mat)


# ==========================================
# 3. Geometry Definition (Library Function)
# ==========================================
# Instead of defining a custom 'def waveguide(...)' function, we import 
# 'flex_taper' from the 'pyOptiShared.Designs' library.
# This function uses GDStk internally to generate complex polygon structures.

# define the array of widths for the taper profile
widths = np.linspace(0.3, 1.0, 5)

# Define the parameters tuple required by 'flex_taper'.
# These likely correspond to: (width_array, length, width_start, width_end, etc., layer, boolean_flags)
parameters = (widths, 0.3, 1.0, 0.5, 2.0, 20, 1, False)


# ==========================================
# 4. Device Geometry Setup
# ==========================================
# Initialize the device geometry.
device_geometry = DeviceGeometry()

# Pass the imported 'flex_taper' function and its parameters.
# The 'SetFromFun' method handles the generation of vertices from the library function.
device_geometry.SetFromFun(
    layer_stack=layer_stack,
    func=flex_taper,
    parameters=parameters,
    buffers={'x': 1.5, 'y': 1.5, 'z': 1.5}
)

# Configure automatic port settings.
device_geometry.SetAutoPortSettings(direction='x', port_buffer=1,pad=False)


# ==========================================
# 5. Simulation Parameters
# ==========================================
# General simulation constants.

# Wavelength points for the solver.
lams = np.linspace(start=1.5, stop=1.6, num=5)


# ==========================================
# 6. Mesh & PML Settings
# ==========================================
# Configure the mesh size.
fem_mesh = Mesh(dx=0.01, dy=0.01, dz=0.01)
fem_mesh.SetMeshOptions(mode='quiet', gui=False, export=True)

# Configure Perfectly Matched Layers (PML) for boundaries.
pml = PML_Params()



# ==========================================
# 7. Solver Initialization
# ==========================================
fefd_solver = FEFDSolver()

# Apply boundaries (PML).
fefd_solver.SetBoundaries(min_x="pml",
                          max_x="pml",
                          min_y="pml",
                          max_y="pml", params=pml)

# Apply Excitation settings.
fefd_solver.SetExcitation(wavelength=lams,
                          reciprocity='1x1')


# ==========================================
# 8. Solver Configuration & Run
# ==========================================
# Pass all settings to the solver.
fefd_solver.SetSimSettings(order=2,
    device_geometry=device_geometry,
    mesh=fem_mesh,
    wavelength=lams,
    stability=1.0,
    resolution=400,
    interpolation="FEM",
    method='direct',
    polarization='TM2.5',
    number_iterations=2,
    device_name='flex_taper',
)

# Run the simulation.
results = fefd_solver.Run()

# ==========================================
# 9. Visualization
# ==========================================
results.PlotField()
results.PlotPort()
results.PlotSParameters(s_param="S21")
