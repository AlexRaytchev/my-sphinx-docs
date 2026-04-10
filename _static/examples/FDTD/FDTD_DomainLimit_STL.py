from pyOptiShared.DeviceGeometry import DeviceGeometry
from pyOptiShared.Material import ConstMaterial
from pyFDTDKernel.pyFDTDSolver import pyFDTDSolver

import pyvista as pv
import numpy as np

def extrude_and_export(filename,vertices,height):

    # Create the base polygon using PolyData
    n_points = len(vertices)
    faces = [n_points] + list(range(n_points))  # [n, 0, 1, 2, ..., n-1]
    polygon = pv.PolyData(vertices, faces=faces)

    # Extrude the polygon along the Z-axis
    extrusion_height = height
    extruded_mesh = polygon.extrude([0, 0, extrusion_height], capping=True)

    # Save as STL file
    extruded_mesh.save(filename)


vertices1 = np.array([(5.0, -0.75,0), (0.0, -0.25,0), (0.0, 0.25,0), (5.0, 0.75,0)])
vertices2 = np.array([(5.0, -3.75,0), (0.0, -3.25,0), (0.0, 3.25,0), (5.0, 3.75,0)])

extrude_and_export('taper_1_0.stl',vertices1,0.22)
extrude_and_export('taper_3_0.stl',vertices2,0.09)


# Material Settings
si02_mat = ConstMaterial(mat_name="SiO2", epsReal=1.45**2,color='lightgreen')
si_mat = ConstMaterial(mat_name="Si", epsReal=3.5**2,color='lightblue')
air_mat = ConstMaterial(mat_name="Air", epsReal=1**2,color='lightyellow')


stl_dict = dict()
stl_dict['taper_1_0.stl'] = si_mat
stl_dict['taper_3_0.stl'] = si_mat

#Device Geometry Settings
device_geometry = DeviceGeometry()

domain_limits = dict()

domain_limits['x'] = [-50,50]
domain_limits['y'] = [-1,1]
domain_limits['z'] = [-2,2]

device_geometry.SetFromSTL(
            stl_dict=stl_dict,
            background_material=si02_mat,
            buffers={'x':1.0,'y':1.0,'z':1.0},
            domain_limits=domain_limits)

device_geometry.SetAutoPortSettings(direction='x',port_buffer=1,min=0.1,max=2.51)
#device_geometry.PrintPorts()

device_geometry.PlotSTL()
# Simulation Settings and Runs
lmin = 1.5
lmax = 1.6
lcen = (lmax+lmin)/2
npts=51
tfinal = 1500

fdtd_solver = pyFDTDSolver()
fdtd_solver.SetExcitation(profile="gaussian-pw", lcenter=lcen, lmin=lmin, lmax=lmax, npts=npts, mode_indices=0,symmetries='1x1')
fdtd_solver.AddDFTMonitor(mon_type="2d-z-normal", z0=0.11, name="MyDFTMonitor1",
                        lmin=lmin, lmax=lmax,npts=npts,
                        save_ex=True, save_ey=True, save_ez=True,
                        save_hx=True, save_hy=True, save_hz=True)


    
fdtd_solver.SetSimSettings(sim_time=tfinal, space_step=0.05, subpixel_level=2, results_path=r"results",device_name='coupler',
                        device_geometry = device_geometry,export_mat_grid=True)
results = fdtd_solver.Run()


results.PlotDFTMonitor(mon_name='MyDFTMonitor1',field='Hz')
results.PlotPermittivity(cut='x',position=-0.5)
results.PlotPermittivity(cut='x',position=3)
results.PlotPermittivity(cut='z',position=0.11)
results.PlotSParameters()

