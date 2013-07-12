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
                        if len(numbers)==8:  #some jackass put normal data in here
                            self.vertices.append(Vertex(numbers[0],numbers[1],numbers[2],numbers[3], numbers[4], numbers[5]))
                        #print "%f %f %f" % (numbers[0], numbers[1], numbers[2])
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



    def scale(self, xBound, yBound, zBound):
        min=Vertex(1000000,1000000,1000000)
        max=Vertex(-1000000,-1000000,-1000000)
        i=0
        j=0
        k=0
        for vertex in self.vertices:
            if vertex.x > max.x:
                max.x=vertex.x
            if vertex.z > max.y:
                max.y=vertex.y
            if vertex.z > max.z:
                max.z=vertex.z
                k=i

            if vertex.x < min.x:
                min.x=vertex.x
            if vertex.y < min.y:
                min.y=vertex.y
            if vertex.z < min.z:
                j=i
                min.z=vertex.z
            i+=1
                
        print "lowest vertex:"
        print min
        print "highest vertex:"
        print max

        bounds=[xBound/(max.x-min.x), yBound/(max.y-min.y), zBound/(max.z-min.z)]
        sortedBounds=sorted(bounds)  # sort the scale factors for the bounding box, with the smallest scale factor first
        print sortedBounds
        scale=sortedBounds[0]
        print "scaling factor: %f" % scale
        print "model dimensions are %f x %f x %f" % (scale * (max.x-min.x), scale* (max.y-min.y), scale * (max.z-min.z))
        #scale all vertices so that the largest dimension fits in the bounding box
        for i in range(len(self.vertices)):
            self.vertices[i].x=self.vertices[i].x*scale
            self.vertices[i].y=self.vertices[i].y*scale
            self.vertices[i].z=self.vertices[i].z*scale
           # print self.vertices[i]

        #sort triangles in order of increasing largest Z value
        self.triangles=sorted(self.triangles, key=lambda triangle: self.vertices[triangle.vertices[0]].z)

        self.xBound=xBound
        self.yBound=yBound
        self.zBound=zBound

        self.bottom=self.vertices[j].z
        self.top=self.vertices[self.triangles[-1].vertices[0]].z
        
        print "bottom:  %f" % self.bottom
        print "top:  %f" % self.top

        for vertex in self.vertices:
            vertex.x+=xBound/2
            vertex.y+=yBound/2
            vertex.z-=self.bottom
            vertex.z+=(zBound-(self.top-self.bottom))/2

 
        #and now we're ready to slice, from bottom to top.



    def slice(self, thickness):
        print "bottom: %f" % self.bottom
        print "top:  %f" % self.top

        z=0
        slice=0
        sheet=0
        cornerMark=3 #3mm x 3mm
        margin=10
        padding=3
        while z<=self.zBound:
            print "cutting plane height:  %f" % z
            if slice%6==0:
                filename="%s-%d.svg" % (self.filename, sheet)
                svg=open(filename,'w')
                svg.write("<?xml version=\"1.0\" encoding=\"utf-8\" ?>\n")
                svg.write("<svg width=\"210mm\" height=\"297mm\" xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\">\n")
            xOffset=margin+((self.xBound+padding)*(slice%3))
            yOffset=margin+(self.yBound+padding)*int((slice%6)/3)

            # draw the corner boxes
#            svg.write("<rect x=\"%fmm\" y=\"%fmm\" width=\"%fmm\" height=\"%fmm\" stroke-width=\"1\" stroke=\"rgb(0,0,0)\" fill=\"rgb(255, 255, 255)\"/>" % (xOffset, yOffset, self.xBound, self.yBound))
            svg.write("<rect x=\"%fmm\" y=\"%fmm\" width=\"%fmm\" height=\"%fmm\" stroke-width=\"1\" stroke=\"rgb(0,0,0)\" fill=\"rgb(255, 0, 0)\"/>" % (xOffset, yOffset, cornerMark, cornerMark))
            svg.write("<rect x=\"%fmm\" y=\"%fmm\" width=\"%fmm\" height=\"%fmm\" stroke-width=\"1\" stroke=\"rgb(0,0,0)\" fill=\"rgb(255, 0, 0)\"/>" % (xOffset+self.xBound-cornerMark, yOffset, cornerMark, cornerMark))
            svg.write("<rect x=\"%fmm\" y=\"%fmm\" width=\"%fmm\" height=\"%fmm\" stroke-width=\"1\" stroke=\"rgb(0,0,0)\" fill=\"rgb(255, 0, 0)\"/>" % (xOffset, yOffset+self.yBound-cornerMark, cornerMark, cornerMark))
            svg.write("<rect x=\"%fmm\" y=\"%fmm\" width=\"%fmm\" height=\"%fmm\" stroke-width=\"1\" stroke=\"rgb(0,0,0)\" fill=\"rgb(255, 0, 0)\"/>" % (xOffset+self.xBound-cornerMark, yOffset+self.yBound-cornerMark, cornerMark, cornerMark))

            #draw the slice number
            svg.write("<text x=\"%dmm\" y=\"%dmm\" font-family=\"Verdana\" font-size=\"2mm\" fill=\"black\" >\n"% (xOffset+5, yOffset+2))
            svg.write("slice %d / %d " % (slice+1, self.zBound/thickness))
            svg.write("</text>\n")
            lineCount=0
            triangleCount=0
            intersectionCount=0
            for triangle in self.triangles:
                triangleCount+=1
                if self.vertices[triangle.vertices[0]].z< z:  #if we've moved above the triangle, take it off the list!
                    print "slice %d, checked %d out of %d triangles" % (slice, triangleCount, len(self.triangles))
#                    self.triangles.remove(triangle)
                    #print "removing a triangle.  
                elif self.vertices[triangle.vertices[1]].z < z or self.vertices[triangle.vertices[2]].z < z:  # see if one of the other two points is below the slicing plane, otherwise there's no intersection
                    print "%d intersections, checked %d out of %d triangles" % (intersectionCount, triangleCount, len(self.triangles))
                    for vertex in triangle.vertices:
                        print self.vertices[vertex]
                    if self.vertices[triangle.vertices[1]].z<z:
                        planePoint1=self.intersectLineWithPlane(z, self.vertices[triangle.vertices[0]], self.vertices[triangle.vertices[1]])
                        planePoint1.r=(self.vertices[triangle.vertices[0]].r+self.vertices[triangle.vertices[1]].r)/2
                        planePoint1.g=(self.vertices[triangle.vertices[0]].g+self.vertices[triangle.vertices[1]].g)/2
                        planePoint1.b=(self.vertices[triangle.vertices[0]].b+self.vertices[triangle.vertices[1]].b)/2
                    else:
                        planePoint1=self.intersectLineWithPlane(z, self.vertices[triangle.vertices[1]], self.vertices[triangle.vertices[2]])
                        planePoint1.r=(self.vertices[triangle.vertices[2]].r+self.vertices[triangle.vertices[1]].r)/2
                        planePoint1.g=(self.vertices[triangle.vertices[2]].g+self.vertices[triangle.vertices[1]].g)/2
                        planePoint1.b=(self.vertices[triangle.vertices[2]].b+self.vertices[triangle.vertices[1]].b)/2
                    
                    if self.vertices[triangle.vertices[2]].z<z:
                        planePoint2=self.intersectLineWithPlane(z, self.vertices[triangle.vertices[0]], self.vertices[triangle.vertices[2]])
                        planePoint2.r=(self.vertices[triangle.vertices[0]].r+self.vertices[triangle.vertices[2]].r)/2
                        planePoint2.g=(self.vertices[triangle.vertices[0]].g+self.vertices[triangle.vertices[2]].g)/2
                        planePoint2.b=(self.vertices[triangle.vertices[0]].b+self.vertices[triangle.vertices[2]].b)/2
                    else:
                        planePoint2=self.intersectLineWithPlane(z, self.vertices[triangle.vertices[1]], self.vertices[triangle.vertices[2]])
                        planePoint2.r=(self.vertices[triangle.vertices[1]].r+self.vertices[triangle.vertices[2]].r)/2
                        planePoint2.g=(self.vertices[triangle.vertices[1]].g+self.vertices[triangle.vertices[2]].g)/2
                        planePoint2.b=(self.vertices[triangle.vertices[1]].b+self.vertices[triangle.vertices[2]].b)/2
                    svg.write("<linearGradient id=\"gradient-%d\" x1=\"0%%\" y1=\"0%%\" x2=\"100%%\" y2=\"100%%\">" % lineCount )
                    svg.write("<stop offset=\"0%%\" style=\"stop-color:rgb(%d, %d, %d);stop-opacity:1\" />" % (planePoint1.r, planePoint1.g, planePoint1.b))
                    svg.write("<stop offset=\"100%%\" style=\"stop-color:rgb(%d, %d, %d);stop-opacity:1\" />"% (planePoint2.r, planePoint2.g, planePoint2.b))
                    svg.write("</linearGradient>")
#                    svg.write("<line x1=\"%fmm\" y1=\"%fmm\" x2=\"%fmm\" y2=\"%fmm\" stroke=\"url(#gradient-%d)\" style=\"stroke-linecap:round\"/>" % (planePoint1.x+xOffset, planePoint1.y+yOffset, planePoint2.x+xOffset, planePoint2.y+yOffset, lineCount))
#                    svg.write("<line x1=\"%fmm\" y1=\"%fmm\" x2=\"%fmm\" y2=\"%fmm\" stroke=\"url(#gradient-%d)\" stroke-width=\"3\" style=\"stroke-linecap:round\"/>" % (planePoint1.x+xOffset, planePoint1.y+yOffset, planePoint2.x+xOffset, planePoint2.y+yOffset, lineCount))
                    svg.write("<line x1=\"%fmm\" y1=\"%fmm\" x2=\"%fmm\" y2=\"%fmm\" stroke=\"url(#gradient-%d)\" stroke-width=\"1mm\"/>" % (planePoint1.x+xOffset, planePoint1.y+yOffset, planePoint2.x+xOffset, planePoint2.y+yOffset, lineCount))
                    lineCount+=1
            print "cutting plane height: %f / %f, %d triangles" % (z, self.zBound, lineCount)

            if slice%6==5:
                svg.write("</svg>")
                svg.close()
                sheet+=1
            slice+=1
            z+=thickness
        if slice%6!=5:
            svg.write("</svg>")
            svg.close()


    def intersectLineWithPlane(self, z, vertex1, vertex2):
        r1=(z-vertex1.z)/(vertex2.z-vertex1.z)
        intersection=Vertex(vertex1.x+r1*(vertex2.x-vertex1.x),vertex1.y+r1*(vertex2.y-vertex1.y),vertex1.z+r1*(vertex2.z-vertex1.z))
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
