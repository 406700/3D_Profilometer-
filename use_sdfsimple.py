#import sdfsimple

#sdf = sdfsimple.SDF("<filename>")
#sdf.show()

# The data is stored in three two-dimensional arrays: sdf.x, sdf.y and sdf.z
# Every unit is micron.
# If you want to plot the profile along the x-axis, at y=1000um,
# that could be done like this:
#plt.figure()

#yind = int(1000/sdf.yscale)

#plt.plot(sdf.x[yind,:],sdf.z[yind,:])

import sdfsimple
sdf = sdfsimple.SDF("./e944_sample_contact_overview.SDF")
sdf.show()
plt.figure()
