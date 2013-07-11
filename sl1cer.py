from Slicer import *

slicer=Slicer()

#slicer.load("shawn-fraye.ply")
slicer.load("alex-hornstein.ply")
#slicer.load("sphere.ply")

'''
for element in slicer.elements:
    print element
for vertex in slicer.vertices:
    print vertex
for triangle in slicer.triangles:
    print triangle

for triangle in slicer.triangles:
    print "%d %d %d %f %f %f" % (triangle.vertices[0],triangle.vertices[1],triangle.vertices[2],slicer.vertices[triangle.vertices[0]].z,slicer.vertices[triangle.vertices[1]].z,slicer.vertices[triangle.vertices[2]].z)
'''
slicer.scale(100.0)
slicer.slice(1.0) #1mm slices
