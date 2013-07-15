import hypermedia.video.*;

PImage a;
Blob[] blobs;
void setup()
{

OpenCV opencv = new OpenCV( this );
a=loadImage("multi.png");
size( a.width, a.height );
opencv.loadImage( "multi.png", width, height );   // fit OpenCV image to the PApplet size
opencv.threshold(80);    // set black & white threshold 
blobs = opencv.blobs( 10, width*height/2, 100, true, OpenCV.MAX_VERTICES*4 );
}

void draw()
{
image(a, 0, 0);             // show image source
stroke(0,255,0);
fill(255,0,0);
   // draw blob results
    for( int i=0; i<blobs.length; i++ ) {
        beginShape();
        for( int j=0; j<blobs[i].points.length; j++ ) {
            vertex( blobs[i].points[j].x, blobs[i].points[j].y );
        }
        endShape(CLOSE);
    }

}
