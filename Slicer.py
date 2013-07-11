from operator import itemgetter, attrgetter
import svgwrite


class Slicer:
    vertices=[]
    triangles=[]
    elements=[]
    format=""
    version=""
    def __init__(self):
        self.vertices=[]
        self.triangles=[]

    # reads in data from .ply file, parses it into an array of vertices and triangles
    def load(self, filename):
        self.filename=filename.split('.')[0]
        model=open(filename,'r')
        lineNumber=0
        errorFlag=False
        error=""

        #the first line in any .ply file should just say "ply"
        line=model.readline().strip()
        if line!="ply":
            errorFlag=True
            error="not a PLY file"
            print error
        else:
            print "ok, it's a PLY file"

        #the second line in any .ply file should tell the format
            line=model.readline()
            parts=line.split(' ')
            self.format=parts[1]
            if len(parts)>2:
                version=parts[2]
                print "format is "+self.format
                
            while(line!="end_header"):
                line=model.readline().strip()
                parts=line.split(' ')
                if parts[0]=="comment":  #if it's a comment, print it out
                    print line
                    
                elif parts[0]=="element":
                    print "weyall, looks lahk we found arselves an element, boys"
                    element=Element(parts[1],int(parts[2]))
                    self.elements.append(element)
                    
                else:
                    print "there's no code to handle this line: "+line

            print "ok, moving on to the data"
            for element in self.elements:
                for i in range(element.units):
                    line=model.readline().strip()
                    parts=line.split(' ')
                    if(element.name=="vertex"):  # the number format is x y z r g b
                        numbers=[]
                        for part in parts:
                            numbers.append(float(part))
                        if len(numbers)==6:
                            self.vertices.append(Vertex(numbers[0],numbers[1],numbers[2],numbers[3], numbers[4], numbers[5]))
                        if len(numbers)==3:  #there's only x y z data, no color data
                            self.vertices.append(Vertex(numbers[0],numbers[1],numbers[2],128, 128, 128))
                        if len(numbers)==9:  #some jackass put normal data in here
                            self.vertices.append(Vertex(numbers[0],numbers[1],numbers[2],numbers[6], numbers[7], numbers[8]))
                        print "%f %f %f" % (numbers[0], numbers[1], numbers[2])
                    elif(element.name=="face"):  # the number format is x y z r g b
                        numbers=[]
                        for part in parts:
                            numbers.append(int(part))
                        vertices=numbers[0]
                        if vertices==3:
                            self.triangles.append(Triangle(numbers[1],numbers[2],numbers[3]))
                        elif vertices==4:
                            self.triangles.append(Triangle(numbers[1],numbers[2],numbers[3]))
                            self.triangles.append(Triangle(numbers[2],numbers[3],numbers[4]))
                        else:
                             print "yowza!  %d vertices is too rich for my blood" % vertices
                    else:
                        print "I'm totally ignoring any elements named "+ element.name


        #sort vertices of each triangle in order of decreasing Z value
        for triangle in self.triangles:
            triangle.vertices=sorted(triangle.vertices, key=lambda vertex: self.vertices[vertex].z, reverse=True)

        #sort triangles in order of increasing largest Z value
        self.triangles=sorted(self.triangles, key=lambda triangle: self.vertices[triangle.vertices[0]].z)



    def scale(self, bound):
        min=Vertex(1000000,1000000,1000000)
        max=Vertex(-1000000,-1000000,-1000000)
        for vertex in self.vertices:
            if vertex.x > max.x:
                max.x=vertex.x
            if vertex.z > max.y:
                max.y=vertex.y
            if vertex.z > max.z:
                max.z=vertex.z

            if vertex.x < min.x:
                min.x=vertex.x
            if vertex.y < min.y:
                min.y=vertex.y
            if vertex.z < min.z:
                min.z=vertex.z
                
        print min
        print max
        bounds=[max.x-min.x, max.y-min.y, max.z-min.z]
        bounds=sorted(bounds, reverse=True)
        print bounds
        scale=bound/bounds[0]
        print "scaling factor: %f" % scale
        #scale all vertices so that the largest dimension fits in the bounding box
        for i in range(len(self.vertices)):
            self.vertices[i].x=self.vertices[i].x*scale
            self.vertices[i].y=self.vertices[i].y*scale
            self.vertices[i].z=self.vertices[i].z*scale
            print self.vertices[i]

        #now shift the model up, so that the bottom is at the 0 and it's going up from there
        self.bottom=self.vertices[self.triangles[0].vertices[2]].z

        for vertex in self.vertices:
            vertex.z-=self.bottom
            vertex.x+=bound/2
            vertex.y+=bound/2

        self.bottom=0.0

        self.top=self.vertices[self.triangles[-1].vertices[0]].z

        #and now we're ready to slice, from bottom to top.



    def slice(self, thickness):
        print "bottom: %f" % self.bottom
        print "top:  %f" % self.top

        z=self.bottom  # start at the bottommost vertex
        slice=0
        while z<=self.top:
            filename="%s-%d.svg" % (self.filename, slice)
            dwg = svgwrite.Drawing(filename, profile='tiny')
            for triangle in self.triangles:
                if self.vertices[triangle.vertices[0]].z< z:  #if we've moved above the triangle, take it off the list!
                    self.triangles.remove(triangle)
                elif self.vertices[triangle.vertices[1]].z < z or self.vertices[triangle.vertices[2]].z < z:  # see if one of the other two points is below the slicing plane, otherwise there's no intersection
                    print "Z:  %f" %z

                    if self.vertices[triangle.vertices[1]].z<z:
                        planePoint1=self.intersectLineWithPlane(z, self.vertices[triangle.vertices[0]], self.vertices[triangle.vertices[1]])
                    else:
                        point1=True #point1 is above the slicing plane, as well, so both points 0 and 1 are above, and point 2 is below
                        planePoint1=self.intersectLineWithPlane(z, self.vertices[triangle.vertices[1]], self.vertices[triangle.vertices[2]])
                    if self.vertices[triangle.vertices[2]].z<z:
                        planePoint2=self.intersectLineWithPlane(z, self.vertices[triangle.vertices[0]], self.vertices[triangle.vertices[2]])
                    else:
                        Point2=True
                        planePoint2=self.intersectLineWithPlane(z, self.vertices[triangle.vertices[1]], self.vertices[triangle.vertices[2]])

                    dwg.add(dwg.line((planePoint1.x, planePoint1.y), (planePoint2.x, planePoint2.y), stroke=svgwrite.rgb(self.vertices[triangle.vertices[0]].r, self.vertices[triangle.vertices[0]].g, self.vertices[triangle.vertices[0]].b,  '%')))
            
            dwg.save()
            slice+=1
            z+=thickness

    def intersectLineWithPlane(self, z, vertex1, vertex2):
        r1=(z-vertex1.z)/(vertex2.z-vertex1.z)
        intersection=Vertex(vertex1.x+r1*(vertex2.x-vertex1.x),vertex1.y+r1*(vertex2.y-vertex1.y),vertex1.z+r1*(vertex2.z-vertex1.z))
        '''
        print "vertex 1: %s" % vertex1
        print "vertex 2: %s" % vertex2
        print "z:  %f" % z
        print vertex1.z
        print vertex2.z
        print "r:  %f" % r1
        print "intersection: %s" %intersection
        '''
        return intersection



class Element:
    name=""
    units=0
    def __init__(self, _name, _units):
        self.name=_name
        self.units=_units

    def __str__(self):
        return "%s:  %d elements" % (self.name, self.units)

class Vertex:
    def __init__(self, _x, _y, _z, _r=128, _g=128, _b=128):
        self.x=_x
        self.y=_y
        self.z=_z
        self.r=_r
        self.g=_g
        self.b=_b

    def __str__(self):
        return "vertex:  %f %f %f %d %d %d" % (self.x, self.y, self.z, self.r, self.g, self.b)

    def color(self):
        return "rgb(%d, %d, %d)" % (self.r, self.g, self.b)


class Triangle:
    vertices=[]
    def __init__(self, _a, _b, _c):
        self.vertices=[_a,_b,_c]

    def __str__(self):
        return "triangle:  %d %d %d" % (self.vertices[0], self.vertices[1], self.vertices[2])
