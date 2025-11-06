from pyOptiShared.DeviceGeometry import DeviceGeometry
from pyOptiShared.Material import ConstMaterial

si02_mat = ConstMaterial(mat_name="SiO2", epsReal=1.45**2,color='lightgreen')
si_mat = ConstMaterial(mat_name="Si", epsReal=3.5**2,color='lightblue')
air_mat = ConstMaterial(mat_name="Air", epsReal=1**2,color='lightyellow')
    

device_geometry = DeviceGeometry()
stl_dict = dict()
stl_dict['coupler.stl'] = si_mat

device_geometry.SetFromSTL(
        stl_dict=stl_dict,
        buffers={'x':1.0,'y':1.0,'z':1.0},
        background_material=air_mat,substrate_material=si02_mat
    )


device_geometry.SetAutoPortSettings(
        direction="x",
        port_buffer=1.5,
    )

device_geometry.PlotSTL()
