import matplotlib.pyplot as plt
from matplotlib.patches import Polygon


def waveguide(port_width=0.4,waveguide_length=1.00,input_port_center=(0,0)):
    wg_pts=[(input_port_center[0],input_port_center[1]-(port_width/2)),
                (input_port_center[0]+waveguide_length,input_port_center[1]-(port_width/2)),
                (input_port_center[0]+waveguide_length,input_port_center[1]+(port_width/2)),
                (input_port_center[0],input_port_center[1]+(port_width/2))]
    return wg_pts

parameters=(0.4,1.00,(0,0))

waveguide_points=waveguide(*parameters)

fig, ax = plt.subplots()
polygon = Polygon(waveguide_points, closed=True, facecolor="lightcoral", edgecolor="black")
ax.add_patch(polygon)
plt.ylim([-1,1])
plt.xlabel('X [um]')
plt.ylabel('Y [um]')

file_name='SetFromFun'+'.svg'

plt.savefig(file_name, bbox_inches='tight')


