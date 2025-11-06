from pyOptiShared.LayerInfo import LayerStack
from pyOptiShared.Material import ConstMaterial
from pyOptiShared.DeviceGeometry import DeviceGeometry

##########################################
###         Material Settings          ###
##########################################
myindex1p45 = ConstMaterial(mat_name="myindex1p45", epsReal=1.45**2)
myindex3p5 = ConstMaterial(mat_name="myindex3p5", epsReal=3.5**2)

##########################################
###       Layer Stack Settings         ###
##########################################
layer_stack = LayerStack()
layer_stack.addLayer(name="L1", number=1, thickness=0.25, zmin=0.0,
                    material=myindex3p5,cladding=myindex1p45)
layer_stack.addLayer(name="L2", number=2, thickness=0.25, zmin=0.25,
                    material=myindex3p5,cladding=myindex1p45)
layer_stack.setBGandSub(background=myindex1p45, substrate=myindex1p45)

##########################################
###   Device Geometry/Port Settings    ###
##########################################
device_geometry = DeviceGeometry()
device_geometry.SetFromGDS(
    layer_stack=layer_stack,
    gds_file=r"wgcrossing.gds",
    buffers={'x':1.5,'y':1.5,'z':1.5}
    )
device_geometry.SetAutoPortSettings(
    direction="both",
    port_buffer=[[2, 1.5],[1.5, 1.25]], # [[x_width, x_height],[y_width, y_height]]
    min=[0.2, 0.21], # [x_min, y_min]
    max=[0.51, 0.51], # [x_max, y_max]
)

device_geometry.PrintPorts()