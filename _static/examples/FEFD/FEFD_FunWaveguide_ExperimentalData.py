from pyOptiShared.DeviceGeometry import DeviceGeometry
from pyOptiShared.LayerInfo import LayerStack
from pyOptiShared.Material import ConstMaterial,ExperimentalMaterial
from FEMFy.FEFDSolver import FEFDSolver
from pyOptiShared.Simulator import PML_Params, Mesh
import matplotlib.pyplot as plt
import numpy as np

# ==========================================
# 1. Material Definitions
# ==========================================
# Define materials needed for the simulation using the ConstMaterial class.
# We define the real permittivity (epsReal = n^2) and visualization colors.
si02_mat = ConstMaterial(mat_name="SiO2", epsReal=1.45**2, color='lightgreen')

lams = np.linspace(start=1.5, stop=1.6, num=5)
n_vals=np.array([3.7840,3.7804,3.7771,3.7739,3.7709])
k_vals=np.array([3,2,1.5,1.1,0.9])*1e-3
eps_vals=(n_vals-1j*k_vals)**2


plt.figure()


ax1 = plt.gca() # Get current axis
line1 = ax1.plot(lams, np.real(eps_vals), color='blue', label='real Epsilon', linestyle='-',marker='o')
ax1.set_xlabel('Wavelength [um]')
ax1.set_ylabel('Real', color='blue')
ax1.tick_params(axis='y', labelcolor='blue')

# 5. Create the Second Axis (Right)
ax2 = ax1.twinx()  # This instantiates a second axes that shares the same x-axis
line2 = ax2.plot(lams, np.imag(eps_vals), color='red', label='imag Epsilon', linestyle='--')
ax2.set_ylabel('Imag', color='red')
ax2.tick_params(axis='y', labelcolor='red')

# 6. Combined Legend (Tricky part!)
# Because there are two axes, standard plt.legend() only sees one.
# We must manually combine handles.
lines = line1 + line2
labels = [l.get_label() for l in lines]
ax1.legend(lines, labels, loc='upper left', frameon=False)

# 7. Adjust Layout and Save
plt.tight_layout()
plt.show()

si_mat = ExperimentalMaterial(mat_name="Si", lamb=lams,values=eps_vals, color='lightblue')



# ==========================================
# 2. Layer Stack Configuration
# ==========================================
# Define the layer stack. We add layers based on the physical stackup.
# - 'material': The material of the geometry defined in this layer.
# - 'cladding': The material filling the rest of the layer outside the geometry.
layer_stack = LayerStack()
layer_stack.AddLayer(name="L1", number=1, thickness=0.22, zmin=0.0,
                     material=si_mat, cladding=si02_mat,
                     sideWallAng=0)

# Set the background (above stack) and substrate (below stack) materials.
layer_stack.SetBGandSub(background=si02_mat, substrate=si02_mat)


# ==========================================
# 3. Geometry Definition (Function-based)
# ==========================================
def waveguide(port_width=0.4, waveguide_length=5.00, input_port_center=(0, 0), layer=1):
    """
    Creates vertices for the structure to solve using polygons.
    
    Args:
        port_width: Width of the waveguide.
        waveguide_length: Length of the waveguide.
        input_port_center: Tuple (x, y) for the start position.
        layer: The layer number this geometry belongs to.
        
    Returns:
        A list of tuples in the format [(vertices, layer)].
    """
    vertices = [
        (input_port_center[0], input_port_center[1] - (port_width / 2)),
        (input_port_center[0] + waveguide_length, input_port_center[1] - (port_width / 2)),
        (input_port_center[0] + waveguide_length, input_port_center[1] + (port_width / 2)),
        (input_port_center[0], input_port_center[1] + (port_width / 2))
    ]
    
    return [(vertices, layer)]


# ==========================================
# 4. Parameter Definition
# ==========================================
# Define the parameters tuple to pass to the function during simulation.
# Format corresponds to function args: (port_width, waveguide_length, input_port_center, layer)
parameters = (0.4, 5.00, (0, 0), 1)


# ==========================================
# 5. Device Geometry Setup
# ==========================================
# Use DeviceGeometry to substitute parameters into the function and build the device.
# We also pass the layer stack and simulation region buffers (x, y, z).
device_geometry = DeviceGeometry()

device_geometry.SetFromFun(
    layer_stack=layer_stack,
    func=waveguide,
    parameters=parameters,
    buffers={'x': 1.5, 'y': 1.5, 'z': 1.5}
)


# ==========================================
# 6. Port Settings
# ==========================================
# Set automatic port detection based on direction (x or y) and buffer size.
device_geometry.SetAutoPortSettings(direction='x', port_buffer=1.3, pad=False)
device_geometry.PrintPorts()


# ==========================================
# 7. Simulation Parameters & PML
# ==========================================
# Define wavelength points (start, stop, number of points).


# Set Perfectly Matched Layer (PML) parameters for the boundaries.
# This defines thickness, profile, kappa, sigma, and alpha for the absorbing layers.
pml = PML_Params()
# ==========================================
# 8. Mesh Settings
# ==========================================
# Configure the finite element mesh size (dx, dy, dz).
fem_mesh = Mesh(dx=0.04, dy=0.04, dz=0.04)
fem_mesh.SetMeshOptions(mode='quiet', gui=False, export=True)


# ==========================================
# 9. Solver Initialization & Boundaries
# ==========================================
fefd_solver = FEFDSolver()

# Set boundaries for the solver (min/max x and y).
# We apply the PML parameters defined in step 7.
fefd_solver.SetBoundaries(min_x="pml",
                          max_x="pml",
                          min_y="pml",
                          max_y="pml", 
                          params=pml)

# Set Excitation and Reciprocity.
# 'reciprocity' avoids simulating symmetrical ports unnecessarily.
fefd_solver.SetExcitation(wavelength=lams,
                          reciprocity='1x1')


# ==========================================
# 10. Final Solver Configuration
# ==========================================
# Pass all defined information (geometry, mesh, wavelength, solver settings) to the solver.
fefd_solver.SetSimSettings(
    device_geometry=device_geometry,
    mesh=fem_mesh,
    wavelength=lams,
    stability=1.0,
    resolution=200,
    interpolation="cubic",
    method='direct',
    polarization='TM2.5',
    number_iterations=2,
    device_name='waveguide_function',
    order=2
)


# ==========================================
# 11. Execution and Visualization
# ==========================================
# Run the simulation.
results = fefd_solver.Run()

# Visualize the results: Fields, Ports, and S-Parameters.
results.PlotField()
results.PlotPort()
results.PlotSParameters(s_param="S21")
