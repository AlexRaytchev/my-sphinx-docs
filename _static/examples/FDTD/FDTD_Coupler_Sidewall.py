from pyOptiShared.DeviceGeometry import DeviceGeometry
from pyOptiShared.LayerInfo import LayerStack
from pyOptiShared.Material import ConstMaterial
from pyFDTDKernel.pyFDTDSolver import pyFDTDSolver
import matplotlib.pyplot as plt

import gdstk

filename = "coupler.gds"

length = 25
width1 = 0.5
width2 = 0.5
gap = 0.15+0.25
lib = gdstk.Library()

strt_wg = lib.new_cell("Straight_WG")
vertices1 = [(0, -width1/2+gap), (length, -width1/2+gap), (length, width1/2+gap), (0, width1/2+gap)]
vertices2 = [(0, -width2/2-gap), (length, -width2/2-gap), (length, width2/2-gap), (0, width2/2-gap)]

strt_wg.add(gdstk.Polygon(vertices1, layer=1))
strt_wg.add(gdstk.Polygon(vertices2, layer=1))

lib.write_gds(filename)

sidewall_angles = [0,10,20]

for swa in sidewall_angles:
    # Define Materials
    si02_mat = ConstMaterial(mat_name="SiO2", epsReal=1.45**2,color='lightgreen')
    si_mat = ConstMaterial(mat_name="Si", epsReal=3.5**2,color='lightblue')
    air_mat = ConstMaterial(mat_name="Air", epsReal=1**2,color='lightyellow')

    # Creates the Layer Stack
    layer_stack = LayerStack()
    layer_stack.addLayer(name="L1", number=1, thickness=0.22, zmin=0.0,
                        material=si_mat, cladding=si02_mat,
                        sideWallAng=swa)

    layer_stack.setBGandSub(background=si02_mat, substrate=si02_mat)

    # Defines the Device Geometry
    device_geometry = DeviceGeometry()
    device_geometry.SetFromGDS(
        layer_stack=layer_stack,
        gds_file='coupler.gds',
        buffers={'x':1.0,'y':1.0,'z':1.0}
    )
    device_geometry.SetAutoPortSettings(direction='x',port_buffer=0.5)

    # General Simulation Settings and Simulation Run
    lmin = 1.5
    lmax = 1.6
    lcen = (lmax+lmin)/2
    npts=21
    tfinal = 550

    fdtd_solver = pyFDTDSolver()
    fdtd_solver.SetPorts(profile="gaussian-pw", lcenter=lcen, lmin=lmin, lmax=lmax, npts=npts, mode_indices = 0,symmetries='2x2')
    fdtd_solver.AddDFTMonitor(mon_type="2d-z-normal", z0=0.11, name="MyDFTMonitor1",
                                                        lmin=lmin, lmax=lmax,npts=npts,
                                                        save_hz=True)
    fdtd_solver.SetSimSettings(sim_time=tfinal, space_step=0.05, subpixel_level=2, save_path=r"results",results_filename='coupler_sidewall',
                                                        device_geometry = device_geometry,auto_shutoff_limit=1e-3,export_mat_grid=True)
    results = fdtd_solver.Run()

    s21 = results.sparameters['S31'].Get('data')
    lam = results.sparameters['S31'].Get('wavelength')

    plt.plot(lam,abs(s21)**2,label='Sidewall Angle = {} deg.'.format(swa))


plt.xlabel('Wavelength (um)')
plt.ylabel('|S31|^2')
plt.legend()
plt.show()

