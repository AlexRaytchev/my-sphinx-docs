from pyOptiShared.DeviceGeometry import DeviceGeometry
from pyOptiShared.LayerInfo import LayerStack
from pyOptiShared.Material import ConstMaterial
from pyFDTDKernel.pyFDTDSolver import pyFDTDSolver

import gdstk

filename = "taper.gds"

length = 2
width1 = 0.5

lib = gdstk.Library()

strt_wg = lib.new_cell("taper")
vertices1 = [(5.0, -0.75), (0.0, -0.25), (0.0, 0.25), (5.0, 0.75)]
vertices2 = [(5.0, -3.75), (0.0, -3.25), (0.0, 3.25), (5.0, 3.75)]
	
strt_wg.add(gdstk.Polygon(vertices1, layer=1))
strt_wg.add(gdstk.Polygon(vertices2, layer=3))

lib.write_gds(filename)


# Material Settings
si02_mat = ConstMaterial(mat_name="SiO2", epsReal=1.45**2,color='lightgreen')
si_mat = ConstMaterial(mat_name="Si", epsReal=3.5**2,color='lightblue')
air_mat = ConstMaterial(mat_name="Air", epsReal=1**2,color='lightyellow')

# Layer Stack Settings
layer_stack = LayerStack()
layer_stack.AddLayer(name="L1", number=1, thickness=0.22, zmin=0.0,
                    material=si_mat, cladding=si02_mat,
                    sideWallAng=0)
layer_stack.AddLayer(name="L2", number=3, thickness=0.09, zmin=0.0,
                    material=si_mat, cladding=si02_mat,
                    sideWallAng=0)
layer_stack.SetBGandSub(background=si02_mat, substrate=si02_mat)


#Device Geometry Settings
device_geometry = DeviceGeometry()

domain_limits = dict()

domain_limits['x'] = [-50,50]
domain_limits['y'] = [-1,1]
domain_limits['z'] = [-2,2]

device_geometry.SetFromGDS(
            gds_file='taper.gds',
            layer_stack=layer_stack,
            buffers={'x':1.0,'y':1.0,'z':1.0},
            domain_limits=domain_limits)

device_geometry.SetAutoPortSettings(direction='x',port_buffer=1,min=0,max=50)

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


    
fdtd_solver.SetSimSettings(sim_time=tfinal, space_step=0.05, subpixel_level=2, results_path=r"results",device_name='taper',
                        device_geometry = device_geometry,export_mat_grid=True)
results = fdtd_solver.Run()


results.PlotDFTMonitor(mon_name='MyDFTMonitor1',field='Hz')
results.PlotPermittivity(cut='x',position=-0.5)
results.PlotPermittivity(cut='x',position=3)
results.PlotPermittivity(cut='z',position=0.11)
results.PlotSParameters()

