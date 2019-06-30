import re
import numpy as np
from PIL import Image
import struct
import scipy.ndimage
import matplotlib.pyplot as plt

class SDF:
    def __init__(self,filename):
        self.filename = filename
        try:
            self.read_ascii()
        except UnicodeDecodeError:
            self.read_binary()

    def read_ascii(self):
        with open(self.filename) as f:
            headerdata = {}
            for line in f:
                if line == "*\n":
                    break
                try:
                    name,value = re.split(r"\s+=\s+",line.strip())
                    headerdata[name] = float(value)
                except ValueError:
                    continue

            self.xscale = headerdata["Xscale"]*1e6 # Use microns
            self.yscale = headerdata["Yscale"]*1e6
            self.zscale = headerdata["Zscale"]#*1e6

            rows = int(headerdata["NumProfiles"])
            columns = int(headerdata["NumPoints"])

            data = np.zeros((rows,columns))
            data_ravel = data.ravel()

            i = 0
            for line in f:
                if line == "*\n":
                    break
                for num in re.split("\s+",line.strip()):
                    if num == "BAD":
                        num = np.nan
                    else:
                        num = float(num)
                    data_ravel[i] = num
                    i += 1

            self.z = np.flip(data * self.zscale,axis=0)

            x = np.linspace(0,self.xscale*columns,columns)
            y = np.linspace(0,self.yscale*rows,rows)

            self.x, self.y = np.meshgrid(x,y)
            f.close() #edited by Michael
    def read_binary(self):
        with open(self.filename,"rb") as f:
            f.read(8+10+12+12) # Version, etc. We don't care
            (xlen,ylen,xscale,yscale,zscale,zresolution,compression,datatype,checktype) = struct.unpack("<HHddddBBB",f.read(39))

            self.xscale = xscale*1e6 # Use microns
            self.yscale = yscale*1e6
            self.zscale = zscale*1e6

            print("Reading {xlen}x{ylen} file, size {xscale*xlen*1e3:.3}mm by {yscale*ylen*1e3:.3}mm. Scale: {xscale*1e6:.2} x {yscale*1e6:.2} um")
            #dont understand what happens here
            assert datatype==7

            data = np.fromfile(f,dtype="<f8").reshape(ylen,xlen)
            data[data==2.2250738585072014e-308] = np.nan

            self.z = np.flip(data * self.zscale,axis=0)
            x = np.linspace(0,self.xscale*xlen,xlen)
            y = np.linspace(0,self.yscale*ylen,ylen)

            self.x, self.y = np.meshgrid(x,y)

            f.close() #ling

    def save_image(self):
        z_max = np.nanmax(self.z)
        z_min = np.nanmin(self.z)
        rescaled = (self.z-z_min)/(z_max-z_min)*255
        img = Image.fromarray(rescaled.astype(np.uint8), mode='L')
        img.save(self.filename + ".png")

    def flatten_corners(self,average=60):

        tl = np.nanmedian(self.z[0:average,0:average])
        tr = np.nanmedian(self.z[0:average,-average:])
        bl = np.nanmedian(self.z[-average:,0:average])
        br = np.nanmedian(self.z[-average:,-average:])

        rows = self.z.shape[0]
        cols = self.z.shape[1]

        top_row = np.linspace(tl,tr,cols)
        bottom_row = np.linspace(bl,br,cols)

        complete = np.linspace(1,0,rows)[:,None] * top_row + np.linspace(0,1,rows)[:,None]*bottom_row
        self.z -= complete

    def rotate_rescale(self,p1_img,p1_real,p2_img,p2_real,p3_img,p3_real,width=512,height=512):
        assert self.xscale == self.yscale # Otherwise, more complicated to handle
        scale = self.xscale

        # Create transformation matrix
        p = np.ones((3,3))
        p[0:2,0] = np.array(p1_real)/scale
        p[0:2,1] = np.array(p2_real)/scale
        p[0:2,2] = np.array(p3_real)/scale
        o = np.stack((np.array(p1_img),np.array(p2_img),np.array(p3_img)),axis=1)
        res = np.dot(o,np.linalg.inv(p))
        A = res[:,0:2]
        C = res[:,2]

        self.z = scipy.ndimage.affine_transform(self.z,A,C,order=1,output_shape=(int(height/scale),int(width/scale)))

        ylen = self.z.shape[0]
        xlen = self.z.shape[1]
        y = np.linspace(0,0+self.yscale*(ylen-1),ylen)
        x = np.linspace(0,0+self.xscale*(xlen-1),xlen)
        self.x,self.y = np.meshgrid(x,y)

    def show(self):
        plt.imshow(self.z,extent=(self.x[0,0], self.x[0,-1], self.y[-1,0],self.y[0,0]))
        plt.colorbar()
