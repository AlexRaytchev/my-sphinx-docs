import matplotlib.pyplot as plt
import numpy as np
import mpld3
from pyFDTDKernel.FDTDResults import FDTDResults

# Plotting Options
my_cmap = 'turbo' # For Colormap selection
save_svg = True # Save figure in SVG format
save_html = True # Uses mpld3 and export figure to HTML

# Load the Results Files
results_spx1 = FDTDResults()
results_spx1.loadHDF5('results/bend90_spx_1_50nm.hdf5')
results_spx2 = FDTDResults()
results_spx2.loadHDF5('results/bend90_spx_2_50nm.hdf5')
results_spx3 = FDTDResults()
results_spx3.loadHDF5('results/bend90_spx_1_25nm.hdf5')
results_spx4 = FDTDResults()
results_spx4.loadHDF5('results/bend90_spx_2_25nm.hdf5')

# Get the Material Cross sections
mat_grd_spx1 = results_spx1.permittivity.Get('EPS_X')[:,:,40].transpose()
mat_grd_spx2 = results_spx2.permittivity.Get('EPS_X')[:,:,40].transpose()
mat_grd_spx3 = results_spx3.permittivity.Get('EPS_X')[:,:,73].transpose()
mat_grd_spx4 = results_spx4.permittivity.Get('EPS_X')[:,:,73].transpose()

# Get the Fields
Hz_spx1 = results_spx1.runs[0].dftmonitors['MyDFTMonitor1'].Get('Hz')
Hz_spx2 = results_spx2.runs[0].dftmonitors['MyDFTMonitor1'].Get('Hz')
Hz_spx3 = results_spx3.runs[0].dftmonitors['MyDFTMonitor1'].Get('Hz')
Hz_spx4 = results_spx4.runs[0].dftmonitors['MyDFTMonitor1'].Get('Hz')

Hz_cs1 = Hz_spx1[11,:,:].transpose()
Hz_cs2 = Hz_spx2[11,:,:].transpose()
Hz_cs3 = Hz_spx3[11,:,:].transpose()
Hz_cs4 = Hz_spx4[11,:,:].transpose()

# General Plot Settings
def set_plot_settings(ax: plt.Axes, title:str=None) -> None:
    ax.set_title(title)
    ax.set_aspect('equal')
    ax.grid(False)
    ax.axis('off')

# HTML Saving Routine
def export_html(fig:plt.Figure, filename:str) -> None:
    html_str = mpld3.fig_to_html(fig)
    with open(filename+".html", "w") as f:
        f.write(html_str)

# Field Comparison Plots
fig = plt.figure(figsize=(16,5))
ax = plt.subplot(1,4,1)
ax.imshow(np.abs(Hz_cs1),origin='lower',cmap=my_cmap)
set_plot_settings(ax,"Space Step: 50nm - Subp. Level: 1")

ax = plt.subplot(1,4,2)
ax.imshow(np.abs(Hz_cs2),origin='lower',cmap=my_cmap)
set_plot_settings(ax,"Space Step: 50nm - Subp. Level: 2")

ax = plt.subplot(1,4,3)
ax.imshow(np.abs(Hz_cs3),origin='lower',cmap=my_cmap)
set_plot_settings(ax,"Space Step: 25nm - Subp. Level: 1")

ax = plt.subplot(1,4,4)
ax.imshow(np.abs(Hz_cs4),origin='lower',cmap=my_cmap)
set_plot_settings(ax,"Space Step: 25nm - Subp. Level: 2")

plt.tight_layout()
plt.suptitle("Magnetic Field - Hz")
if save_svg: plt.savefig('subpixel_Hz.svg',bbox_inches='tight', pad_inches=0.2)
if save_html: export_html(fig, "subpixel_Hz")

# Field Comparison Plots - Zoomed
fig = plt.figure(figsize=(18,7))
ax = plt.subplot(1,4,1)
ax.imshow(np.abs(Hz_cs1[40:150,100:175]),origin='lower',cmap=my_cmap)
set_plot_settings(ax,"$H_z$ - Space Step=50nm Sub. Av.=1->Off")

ax = plt.subplot(1,4,2)
ax.imshow(np.abs(Hz_cs2[40:150,100:175]),origin='lower',cmap=my_cmap)
set_plot_settings(ax,"$H_z$ - Space Step=50nm Sub. Av.=2")

ax = plt.subplot(1,4,3)
ax.imshow(np.abs(Hz_cs3[80:300,200:350]),origin='lower',cmap=my_cmap)
set_plot_settings(ax,"$H_z$ - Space Step=25nm Sub. Av.=1->Off")

ax = plt.subplot(1,4,4)
ax.imshow(np.abs(Hz_cs4[80:300,200:350]),origin='lower',cmap=my_cmap)
set_plot_settings(ax,"$H_z$ - Space Step=25nm Sub. Av.=2")

plt.tight_layout()
if save_svg: plt.savefig('subpixel_Hz_zoomed.svg',bbox_inches='tight', pad_inches=0.2)
if save_html: export_html(fig, "subpixel_Hz_zoomed")

# Material Comparison Plots - Zoomed
fig = plt.figure(figsize=(18,7))
ax = plt.subplot(1,4,1)
ax.imshow(np.real(mat_grd_spx1[40:150,100:175]),origin='lower',cmap=my_cmap)
set_plot_settings(ax,"$\\epsilon_{r,x}$ - Space Step=50nm Sub. Av.=1->Off")

ax = plt.subplot(1,4,2)
ax.imshow(np.real(mat_grd_spx2[40:150,100:175]),origin='lower',cmap=my_cmap)
set_plot_settings(ax,"$\\epsilon_{r,x}$ - Space Step=50nm Sub. Av.=2")

ax = plt.subplot(1,4,3)
ax.imshow(np.real(mat_grd_spx3[80:300,200:350]),origin='lower',cmap=my_cmap)
set_plot_settings(ax,"$\\epsilon_{r,x}$ - Space Step=25nm Sub. Av.=1->Off")

ax = plt.subplot(1,4,4)
ax.imshow(np.real(mat_grd_spx4[80:300,200:350]),origin='lower',cmap=my_cmap)
set_plot_settings(ax,"$\\epsilon_{r,x}$ - Space Step=25nm Sub. Av.=2")

plt.tight_layout()
if save_svg: plt.savefig('subpixel_epsx_zoomed.svg',bbox_inches='tight', pad_inches=0.2)
if save_html: export_html(fig, "subpixel_epsx_zoomed")

# Get Wavelength and S21 Data
lam = abs(results_spx1.sparameters['S21'].Get('wavelength'))

# Get SParameter Data - S21 - Transmission
s21_spx1 = results_spx1.sparameters['S21'].Get('data')
s21_spx2 = results_spx2.sparameters['S21'].Get('data')
s21_spx3 = results_spx3.sparameters['S21'].Get('data')
s21_spx4 = results_spx4.sparameters['S21'].Get('data')

# Plot Transmittance - |S21|^2
fig = plt.figure()
fig.suptitle('Transmittance - $|S_{21}|^2$')
plt.plot(lam,abs(s21_spx1)**2,label="Space Step=50nm Sub. Av.=1->Off",linestyle='--')
plt.plot(lam,abs(s21_spx2)**2,label="Space Step=50nm Sub. Av.=2",linestyle='--')
plt.plot(lam,abs(s21_spx3)**2,label="Space Step=25nm Sub. Av.=1->Off")
plt.plot(lam,abs(s21_spx4)**2,label="Space Step=25nm Sub. Av.=2")
plt.xlabel('Wavelength (um)')
plt.ylabel('Amplitude')
plt.legend(loc="center right")
if save_svg: plt.savefig('subpixel_s21.svg',bbox_inches='tight', pad_inches=0.2)
if save_html: export_html(fig, "subpixel_s21")

# Get SParameter Data - S11 - Reflection
s11_spx1 = results_spx1.sparameters['S11'].Get('data')
s11_spx2 = results_spx2.sparameters['S11'].Get('data')
s11_spx3 = results_spx3.sparameters['S11'].Get('data')
s11_spx4 = results_spx4.sparameters['S11'].Get('data')

# Plot Reflectance - |S11|^2
fig = plt.figure()
fig.suptitle('Reflectance - $|S_{11}|^2$')
plt.plot(lam,abs(s11_spx1)**2,label="Space Step=50nm Sub. Av.=1->Off",linestyle='--')
plt.plot(lam,abs(s11_spx2)**2,label="Space Step=50nm Sub. Av.=2",linestyle='--')
plt.plot(lam,abs(s11_spx3)**2,label="Space Step=25nm Sub. Av.=1->Off")
plt.plot(lam,abs(s11_spx4)**2,label="Space Step=25nm Sub. Av.=2")
plt.xlabel('Wavelength (um)')
plt.ylabel('Amplitude')
plt.legend(loc="upper right")
if save_svg: plt.savefig('subpixel_s11.svg',bbox_inches='tight', pad_inches=0.2)
if save_html: export_html(fig, "subpixel_s11")
plt.show()
