from pyOptiShared.DeviceGeometry import DeviceGeometry
from pyOptiShared.LayerInfo import LayerStack
from pyOptiShared.Material import ConstMaterial
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
# Define the layer stack structure.
layer_stack = LayerStack()
layer_stack.AddLayer(name="L1", number=1, thickness=0.22, zmin=0.0,
                     material=si_mat, cladding=si02_mat,
                     sideWallAng=0)
layer_stack.SetBGandSub(background=si02_mat, substrate=si02_mat)


# ==========================================
# 3. Geometry Definition (Function-based)
# ==========================================
def waveguide(port_width=0.4, waveguide_length=1.00, input_port_center=(0, 0), layer=1):
    """
    Creates vertices for the waveguide structure.
    This function will be called repeatedly with updated parameters during the sweep.
    """
    vertices = [
        (input_port_center[0], input_port_center[1] - (port_width / 2)),
        (input_port_center[0] + waveguide_length, input_port_center[1] - (port_width / 2)),
        (input_port_center[0] + waveguide_length, input_port_center[1] + (port_width / 2)),
        (input_port_center[0], input_port_center[1] + (port_width / 2))
    ]
    return [(vertices, layer)]


# ==========================================
# 4. Sweep Parameter Setup
# ==========================================
# Define the range of widths to sweep over.
min_width = 0.3
max_width = 0.8
num_points = 3
widths = np.linspace(min_width, max_width, num_points)

# Define initial parameters tuple.
# Format: (port_width, waveguide_length, input_port_center, layer)
initial_parameters = (widths[0], 5.00, (0, 0), 1)


# ==========================================
# 5. Device Geometry Initialization
# ==========================================
# Initialize the device geometry with the function and INITIAL parameters.
# The parameters will be updated inside the loop later.
device_geometry = DeviceGeometry()

device_geometry.SetFromFun(
    layer_stack=layer_stack,
    func=waveguide,
    parameters=initial_parameters,
    buffers={'x': 1.5, 'y': 1.5, 'z': 1.5}
)

# Configure ports.
device_geometry.SetAutoPortSettings(direction='x', port_buffer=1, 
                                    min=[0.1, 0.51], max=[0.55, 0.55], pad=False)


# ==========================================
# 6. Simulation Parameters
# ==========================================
# Wavelength points for the solver.
lams = np.linspace(start=1.5, stop=1.6, num=21)


# ==========================================
# 7. Mesh & PML Settings
# ==========================================
# Configure the mesh size.
fem_mesh = Mesh(dx=0.04, dy=0.04, dz=0.04)
fem_mesh.SetMeshOptions(mode='quiet', gui=False, export=True)

# Configure Perfectly Matched Layers (PML) for each boundary.
pml = PML_Params()
#pml.SetMinX(thickness=0.6, profile=2, kappa=1, sigma=1.3, alpha=0.00)
#pml.SetMaxX(thickness=0.6, profile=2, kappa=1, sigma=1.3, alpha=0.00)
#pml.SetMinY(thickness=0.1, profile=2, kappa=1, sigma=1.0, alpha=0.00)
#pml.SetMaxY(thickness=0.1, profile=2, kappa=1, sigma=1.0, alpha=0.00)

# ==========================================
# 8. Solver Initialization
# ==========================================
fefd_solver = FEFDSolver()

# Apply boundaries (PML) and excitation settings.
fefd_solver.SetBoundaries(min_x="pml",
                          max_x="pml",
                          min_y="pml",
                          max_y="pml", params=pml)

fefd_solver.SetExcitation(wavelength=lams,
                          reciprocity='1x1')
    



# ==========================================
# 9. Sweep Execution Loop
# ==========================================
# Iterate through each width in the defined array.
for w in widths:
    # 9a. Define filename for this specific iteration
    results_filename = 'waveguide_spx_1_50nm_sweep_' + str(w)
    print('solving for width : ', w)
    
    # 9b. Update Geometry Parameters
    # Create a new parameters tuple with the current width 'w'.
    # The other parameters (length, center, layer) remain constant.
    params = (w, 5.00, (0, 0), 1)
    
    # UpdateScriptParams applies the new parameters to the 'waveguide' function
    # defined in the DeviceGeometry object.
    device_geometry.UpdateScriptParams(params)

    
    # 9c. Update Solver Settings
    # Pass the updated device_geometry and unique filename to the solver.
    fefd_solver.SetSimSettings(
        device_geometry=device_geometry,
        mesh=fem_mesh,
        wavelength=lams,
        stability=1.0,
        resolution=500,
        interpolation="nearest",
        method='direct',
        polarization='TM2.5',
        number_iterations=2,
        order=2,
        device_name=results_filename,
    )

    # 9d. Run Simulation
    results = fefd_solver.Run()

    # 9e. Visualize Results
    # Plots will be generated for every iteration.
    results.PlotField(show=False)
    results.PlotPort(show=False)
    results.PlotSParameters(s_param="S21",show=False)
    print( f"width : {w} --- done !")
plt.show()

# Show all generated plots after the loop finishes.
