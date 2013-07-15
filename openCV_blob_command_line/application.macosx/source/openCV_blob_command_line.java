import processing.core.*; 
import processing.data.*; 
import processing.event.*; 
import processing.opengl.*; 

import hypermedia.video.*; 

import java.util.HashMap; 
import java.util.ArrayList; 
import java.io.File; 
import java.io.BufferedReader; 
import java.io.PrintWriter; 
import java.io.InputStream; 
import java.io.OutputStream; 
import java.io.IOException; 

public class openCV_blob_command_line extends PApplet {



PImage a;
Blob[] blobs;
String output;
public void setup()
{
String rawImage=args[0];
println(args);
String[] parts=split(rawImage, ".");
println(parts);
output=parts[0]+"-mask."+parts[1];
OpenCV opencv = new OpenCV( this );
a=loadImage(rawImage);
size( a.width, a.height );
opencv.loadImage(rawImage, width, height );   // fit OpenCV image to the PApplet size
opencv.threshold(20);    // set black & white threshold 
blobs = opencv.blobs( 10, width*height*95/100, 100, false, OpenCV.MAX_VERTICES*4 );
println(blobs.length);
noLoop();
}

public void draw()
{
background(0);
stroke(255);
fill(255);
   // draw blob results
    for( int i=0; i<blobs.length; i++ ) {
        beginShape();
        for( int j=0; j<blobs[i].points.length; j++ ) {
            vertex( blobs[i].points[j].x, blobs[i].points[j].y );
        }
        endShape(CLOSE);
    }
saveFrame(output);
exit();
}
  static public void main(String[] passedArgs) {
    String[] appletArgs = new String[] { "openCV_blob_command_line" };
    if (passedArgs != null) {
      PApplet.main(concat(appletArgs, passedArgs));
    } else {
      PApplet.main(appletArgs);
    }
  }
}
