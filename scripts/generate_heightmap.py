from PIL import Image
import numpy as np

path = "/home/adron/data/projects/WARR/terrain_data/DTM_ver2.csv"

data = np.loadtxt(open(path, "rb"), delimiter=",", skiprows=2)

w, h = data.shape
data -= np.min(data)
data /= np.max(data)
data *= 255
data = np.stack((data,)*3, axis=-1)

img = Image.fromarray(np.uint8(data), 'RGB')
img = img.resize((129, 129), resample=Image.BICUBIC)
img.save("rover_sim/worlds/terrain.png")
img.show()
