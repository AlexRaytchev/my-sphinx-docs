from pyOptiShared.DeviceGeometry import DeviceGeometry
from pyOptiShared.LayerInfo import LayerStack
from pyOptiShared.Material import ConstMaterial
import matplotlib.pyplot as plt
from FEMFy.FEFDSolver import FEFDSolver
from pyOptiShared.Simulator import PML_Params, Mesh
from pyFDTDKernel.FDTDResults import FDTDResults
import numpy as np
import gdstk

# Define the filename for the GDS geometry
filename = "mmi1x2_with_sbend.gds"


# ==========================================
# 1. Material Definitions
# ==========================================
# Define materials needed for the simulation.
si02_mat = ConstMaterial(mat_name="SiO2", epsReal=1.45**2, color='lightgreen')
si_mat = ConstMaterial(mat_name="Si", epsReal=3.5**2, color='lightblue')


# ==========================================
# 2. Layer Stack Configuration
# ==========================================
# Define the layer stack.
layer_stack = LayerStack()
layer_stack.AddLayer(name="L1", number=1, thickness=0.22, zmin=0.0,
                     material=si_mat, cladding=si02_mat)

# Set background and substrate materials.
layer_stack.SetBGandSub(background=si02_mat, substrate=si02_mat)


# ==========================================
# 3. Device Geometry Setup (GDS Import)
# ==========================================
# Initialize device geometry and load from GDS file.
device_geometry = DeviceGeometry()
device_geometry.SetFromGDS(
    layer_stack=layer_stack,
    gds_file=filename,
    buffers={'x': 1.0, 'y': 4.0, 'z': 1.0}
)


# ==========================================
# 4. Port Settings
# ==========================================
# Configure automatic port detection.
device_geometry.SetAutoPortSettings(direction='x', port_buffer=2, max=1.3, min=0.1, pad=False)


# ==========================================
# 5. Mesh Settings
# ==========================================
# Configure the finite element mesh size.
fem_mesh = Mesh(dx=0.04, dy=0.04, dz=0.04)
fem_mesh.SetMeshOptions(mode='quiet', gui=False, export=True)


# ==========================================
# 6. PML & Boundary Conditions
# ==========================================
# Initialize solver and PML parameters.
fefd_solver = FEFDSolver()
pml = PML_Params()

# Set explicit PML parameters for Min/Max X and Y boundaries.


# Apply boundaries to the solver.
fefd_solver.SetBoundaries(min_x="pml",
                          max_x="pml",
                          min_y="pml",
                          max_y="pml", params=pml)


# ==========================================
# 7. Excitation Settings
# ==========================================
# Define wavelength sweep range.
lmin = 1.5
lmax = 1.6
lams = np.linspace(start=lmin, stop=lmax, num=5)

# Set excitation wavelengths and reciprocity.
fefd_solver.SetExcitation(wavelength=lams,
                          reciprocity='1x2')


# ==========================================
# 8. Solver Configuration & Execution
# ==========================================
# Pass all settings to the solver.
fefd_solver.SetSimSettings(
    device_geometry=device_geometry,
    order=2,
    mesh=fem_mesh,
    wavelength=lams,
    stability=1.0,
    resolution=1000,
    interpolation="FEM",
    method='direct',
    polarization='TM2.5',
    number_iterations=2,
    results_path='',
)

# Run the FEFD simulation.
fefd_results = fefd_solver.Run()

# Visualize immediate FEFD results.
fefd_results.PlotField()
fefd_results.PlotSParameters("S21")
fefd_results.PlotSParameters("S31")
fefd_results.PlotPort()


# ==========================================
# 9. Validation: Compare with FDTD Results
# ==========================================
# This section loads pre-calculated FDTD results to benchmark the FEFD solver.

# 9a. Load FDTD data from HDF5 file
fdtd_results = FDTDResults()
# Note: This path is specific to the local machine and points to a previous simulation result.
fdtd_results.loadHDF5(r'fdtd_mmi1x2.hdf5')

# 9b. Extract Data for Comparison
# Extract S21 and S31 parameters from the loaded FDTD results.
fdtd_S21 = fdtd_results.sparameters['S21'].Get('data')
fdtd_S31 = fdtd_results.sparameters['S31'].Get('data')
fdtd_lam = fdtd_results.sparameters['S21'].Get('wavelength')

# Extract S21 and S31 parameters from the current FEFD run.
fefd_S21 = fefd_results.sparameters['S21'].Get('data')
fefd_S31 = fefd_results.sparameters['S31'].Get('data')
lam = fefd_results.sparameters['S21'].Get('wavelength')


# 9c. Plot Comparison (S31)
plt.figure()
plt.plot(lam, abs(fefd_S31), '--o', label='Abs S31_FEFD')
plt.plot(fdtd_lam, abs(fdtd_S31), label='Abs S31_FDTD')
plt.ylim([0.2, 1])
plt.xlabel('wavelength [um]')
plt.legend()


# 9d. Plot Comparison (S21)
plt.figure()
plt.plot(lam, abs(fefd_S21), '--o', label='Abs S21_FEFD')
plt.plot(fdtd_lam, abs(fdtd_S21), label='Abs S21_FDTD')
plt.xlabel('wavelength [um]')
plt.ylim([0.2, 1])
plt.legend()
