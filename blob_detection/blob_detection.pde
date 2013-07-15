import blobDetection.*;

BlobDetection theBlobDetection;
PGraphics img;

// ==================================================
// setup()
// ==================================================
void setup()
{
  // Works with Processing 1.5
  // img = createGraphics(640, 480,P2D);

  PImage outline=loadImage("multi.png");

  // Works with Processing 2.0b3
  img = createGraphics(outline.width, outline.height);

  img.beginDraw();
  img.image(outline,0,0);
  img.endDraw();

  theBlobDetection = new BlobDetection(img.width, img.height);
  theBlobDetection.setPosDiscrimination(false);
  theBlobDetection.setThreshold(0.99f);
  theBlobDetection.setConstants(1000, 100000, 500000);
  theBlobDetection.computeTriangles();
  theBlobDetection.computeBlobs(img.pixels);
  println(theBlobDetection.getBlob(0).getTriangleNb());

  // Size of applet
  size(img.width, img.height);
}

// ==================================================
// draw()
// ==================================================
void draw()
{
  image(img, 0, 0, width, height);
  fillBlobs();
//  drawBlobsAndEdges(false, true);
}

// ==================================================
// drawBlobsAndEdges()
// ==================================================
void drawBlobsAndEdges(boolean drawBlobs, boolean drawEdges)
{
  noFill();
  Blob b;
  EdgeVertex eA, eB, eC;
  for (int n=0 ; n<theBlobDetection.getBlobNb() ; n++)
  {
    b=theBlobDetection.getBlob(n);
    if (b!=null)
    {
      // Edges
      if (drawEdges)
      {
        strokeWeight(2);
        stroke(0, 255, 0);
        for (int m=0;m<b.getEdgeNb();m++)
        {
          eA = b.getEdgeVertexA(m);
          eB = b.getEdgeVertexB(m);
          if (eA !=null && eB !=null)
            line(
            eA.x*width, eA.y*height, 
            eB.x*width, eB.y*height
              );
        }
      }

      // Blobs
      if (drawBlobs)
      {
        strokeWeight(1);
        stroke(255, 0, 0);
        rect(
        b.xMin*width, b.yMin*height, 
        b.w*width, b.h*height
          );
      }
    }
  }
}

// ==================================================
// drawBlobsAndEdges()
// ==================================================
void fillBlobs()
{
  fill(0);
  Blob b;
  EdgeVertex eA, eB, eC;
  for (int n=0 ; n<theBlobDetection.getBlobNb() ; n++)
  {
    b=theBlobDetection.getBlob(n);
    if (b!=null)
    {
        stroke(50);
        fill(255,0,0);        
        beginShape();
        int m;
        for (m=0;m<b.getEdgeNb();m++)
        {
          eA = b.getEdgeVertexA(m);
          vertex(eA.x, eA.y);
        }
        eA=b.getEdgeVertexB(m-1);
        vertex(eA.x, eA.y);
        endShape(CLOSE);
        
    }
  }
}

