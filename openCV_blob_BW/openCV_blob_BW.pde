import hypermedia.video.*;

PImage a;
Blob[] blobs;
void setup()
{
rawImage=args[0];
println(rawImage);
OpenCV opencv = new OpenCV( this );
a=loadImage(rawImage);
size( a.width, a.height );
opencv.loadImage(rawImage, width, height );   // fit OpenCV image to the PApplet size
opencv.threshold(10);    // set black & white threshold 
blobs = opencv.blobs( 10, width*height*95/100, 100, false, OpenCV.MAX_VERTICES*4 );
println(blobs.length);
noLoop();
}

void draw()
{
  background(255);
//image(a, 0, 0);             // show image source
stroke(0,0,0);
fill(0,0,0);
   // draw blob results
    for( int i=0; i<blobs.length; i++ ) {
        beginShape();
        for( int j=0; j<blobs[i].points.length; j++ ) {
            vertex( blobs[i].points[j].x, blobs[i].points[j].y );
        }
        endShape(CLOSE);
    }
      
   //saveFrame("
  
}
