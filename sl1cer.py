from Slicer import *

slicer=Slicer()

#slicer.load("guy.ply")
#slicer.load("nick.ply")
slicer.load("shawn-fraye.ply")
#slicer.load("alex-hornstein.ply")
#slicer.load("sphere.ply")

slicer.scale(50, 50, 60.0)
slicer.slice(.3) #1mm slices
