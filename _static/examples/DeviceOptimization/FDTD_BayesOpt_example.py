from pyOptiShared.LayerInfo import LayerStack
from pyOptiShared.Material import ConstMaterial
from pyOptiShared.DeviceGeometry import DeviceGeometry
from pyOptiShared.Designs import flex_taper
from pyFDTDKernel.pyFDTDSolver import pyFDTDSolver
from pyOptiShared.OptimizeVerse import bayes_opt 
import numpy as np

##########################################
###         Material Settings          ###
##########################################
SiO2 = ConstMaterial(mat_name="SiO2", epsReal=1.45**2)
Si = ConstMaterial(mat_name="Si", epsReal=3.5**2)

##########################################
###       Layer Stack Settings         ###
##########################################
layer_stack = LayerStack()
layer_stack.AddLayer(name="L1", number=1, thickness=0.25, zmin=0.0,
                    material=Si,cladding=SiO2)
layer_stack.SetBGandSub(background=SiO2, substrate=SiO2)

##########################################
###    Construct the initial device    ###
##########################################
# set up flex_taper function initial parameter parameters
num_parameters:int=5 # number of sections
min_width=0.25
max_width=1.0
taper_length=2.0
in_width=0.5
out_width=2.0
input_length=0.5
resolution=5*num_parameters
layer=1
write=False
widths=np.linspace(min_width,max_width,num_parameters+2)
widths=widths[1:-1]+np.random.uniform(-0.05, 0.05, size=num_parameters)
widths=np.array([0.77307158, 0.59015701, 0.7915417,  0.89978674, 0.98164113 ])
init_params=(widths,input_length,taper_length,in_width,out_width,resolution,layer,write)
component=flex_taper(*init_params)
component.write_gds('Initial_flexTaper.gds')

##########################################
# Set bounds on widths for the optimization
width_bound = np.ones((num_parameters, 2)) * np.array([min_width, max_width])

##########################################
###   Device Geometry/Port Settings    ###
##########################################
device_geometry = DeviceGeometry()
device_geometry.SetFromFun(
    func=flex_taper,
    layer_stack=layer_stack,
    parameters=init_params,
    buffers={'x':1.5,'y':1.5,'z':1.5}
    )


device_geometry.SetAutoPortSettings(
    direction="x",
    port_buffer=1.2, # [[x_width, x_height],[y_width, y_height]]
    min=0, # [x_min, y_min]
    max=2.1, # [x_max, y_max]
)



# Simulation Settings and Runs
lmin = 1.5
lmax = 1.6
lcen = (lmax+lmin)/2
npts=21
tfinal = 1500

fdtd_solver = pyFDTDSolver()
fdtd_solver.SetExcitation(profile="gaussian-pw", lcenter=lcen, lmin=lmin, lmax=lmax, npts=npts, mode_indices=0,symmetries='1x1')
fdtd_solver.AddDFTMonitor(mon_type="2d-z-normal", z0=0.11, name="MyDFTMonitor1",
                        lmin=lmin, lmax=lmax,npts=npts,
                        save_ex=True, save_ey=True, save_ez=True,
                        save_hx=True, save_hy=True, save_hz=True)


      
fdtd_solver.SetSimSettings(sim_time=tfinal, space_step=0.050, subpixel_level=1, results_path=r"results",device_name='flex_taper',
                        device_geometry = device_geometry,export_mat_grid=True)


# Computation function takes input parameters as an argument and outputs the results of this simulation
def compute_fn(widths):
    params=(widths,input_length,taper_length,in_width,out_width,resolution)
    device_geometry.UpdateScriptParams(params)
    results = fdtd_solver.Run()
    S21 = results.sparameters['S21'].Get('data')[11]
    value = (1.0-np.abs(S21)**2) # maximize the output power
    return value


compute_fn(widths=widths)

# Generate Random Seed
seed = 0
np.random.seed(seed)
N_total = 100 # total number of simulations
N_initial = 40 # total number of initial simulations



cur_best_w, cur_best_y = bayes_opt(compute_fn, num_parameters, N_total, N_initial, width_bound, ['LCB1', 0.3],
                                       store=False, verbose=True, file_suffix=str(seed))

print("-" * 70)
print('Best design parameters are : ',cur_best_w)
print('Current best performance : ',cur_best_y)
widths=np.array(cur_best_w)
# Generate GDS of the best design
best_params=(widths,input_length,taper_length,in_width,out_width,resolution,layer,write)
component=flex_taper(*best_params)
component.write_gds('BestDesign_flexTaper.gds')
