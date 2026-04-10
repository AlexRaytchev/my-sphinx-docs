from pyOptiShared.Material import ConstMaterial
# Silicon dioxide (n=1.444) for substrate and cladding
sio2_mat = ConstMaterial(mat_name="SiO2", epsReal=1.444**2, color='lightgreen')
   
# Silicon (n=3.48) for waveguide core
si_mat = ConstMaterial(mat_name="Si", epsReal=3.48**2, color='lightblue')
   
# Air (n=1.0) for background
air_mat = ConstMaterial(mat_name="Air", epsReal=1**2, color='lightyellow')