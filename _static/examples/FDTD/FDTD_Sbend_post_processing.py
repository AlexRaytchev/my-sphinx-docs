import numpy as np
from PIL import Image
from pyOptiShared.DeviceGeometry import DeviceGeometry
from pyOptiShared.LayerInfo import LayerStack
from pyOptiShared.Material import ConstMaterial
from pyFDTDKernel.pyFDTDSolver import pyFDTDSolver
from pyFDTDKernel.FDTDResults import FDTDResults
from matplotlib.colors import Normalize
import matplotlib.pyplot as plt
from scipy.interpolate import RegularGridInterpolator

def GenerateGif(data:np.ndarray, eps:np.ndarray=None, filename:str='output.gif'):
  data = (data/np.max(data))
  ni,nj,nk = data.shape
  x1 = np.linspace(0,1,nj)
  y1 = np.linspace(0,1,nk)
  x2 = np.linspace(0,1,2*nj)
  y2 = np.linspace(0,1,2*nk)
  X2,Y2 = np.meshgrid(x2,y2)
  frames = []
  alpha = 0.6

  if eps is not None:
      eps = eps/np.max(eps)
      eps = eps.transpose()
      perm_interp = RegularGridInterpolator((y1, x1), eps)
      permittivity_resampled = perm_interp((Y2, X2))
      # Normalize permittivity and convert to grayscale RGB
      perm_norm = Normalize(vmin=0, vmax=1)
      perm_gray = perm_norm(permittivity_resampled)
      perm_rgb = (np.stack([perm_gray]*3, axis=-1) * 255).astype(np.uint8)

  for ii in range(0,ni):
      Z = data[ii,:,:].transpose()
      interp = RegularGridInterpolator((y1, x1), Z)
      array_2d = interp((Y2, X2))
      norm = Normalize(vmin=0, vmax=1)
      cmap = plt.get_cmap('turbo')
      # Apply the colormap to the normalized array
      rgb_image = cmap(norm(array_2d))
      # Remove the alpha channel
      rgb_image = (rgb_image[:, :, :3] * 255).astype(np.uint8)
      if eps is not None: # Blend
          blend = ((1 - alpha) * perm_rgb + alpha * rgb_image).astype(np.uint8)
      else:
          blend = rgb_image
      frames.append(blend)

  # Convert each frame to an image
  images = [Image.fromarray(frame) for frame in frames]

  # Save as a GIF
  images[0].save(filename, save_all=True, append_images=images[1:], duration=10, loop=0)

# Load the Results
results = FDTDResults()
results.loadHDF5('results/sbend.hdf5')
# Get The field Data
field = results.runs[0].timemonitors["MyTimeMonitor1"]
field = np.abs(field.Get('Hz'))
# Get the Raw permittivity and average it out along Y
eps = results.permittivity.Get("EPS_Z")
eps = np.real(eps)[:,:,38]
eps = (eps[:,1:]+eps[:,0:-1])/2
# Create the gif
GenerateGif(field, eps, filename='Hz.gif')