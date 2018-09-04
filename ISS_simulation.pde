import processing.net.*; 
Client myClient;

String data;
PImage earth;
PShape globe;
int r = 200, radius;
float angle = 0, x, y, z, theta, phi;

String thetaS, phiS;  
JSONObject json;

void setup()
{
  size(700, 700, P3D);

  // Initilize communication with python server
  myClient = new Client(this, "192.168.1.69", 8080);  

  // Load image to be used as texture
  earth = loadImage("earth.jpg");

  // Set shape with desired characteristics, no stroke and texture of earth
  noStroke();
  globe = createShape(SPHERE, r);
  globe.setTexture(earth);
}

void draw()
{
  background(0);
  translate(width/2, height/2);
  // ----------- Earth Model -------------- // 
  rotateX(-0.23);
  rotateY(angle);
  angle += 0.008;
  lights();
  shape(globe);

  // ----------- API request to get coordinates ------------ //
  // Too slow but can be improved, currently getting the wanted 
  // data from the python server
  
  //json = loadJSONObject("http://api.open-notify.org/iss-now.json");
  //// Get coordinates from JSON file
  //JSONObject iss = json.getJSONObject("iss_position");
  //thetaS = iss.getString("latitude");
  //phiS = iss.getString("longitude");
  //println(iss);
  
  // ---------- Fetch Server Data ------------//
  if (myClient.available() > 0) {    
    data = myClient.readStringUntil('\n');
  }
  // Splits the incoming string by spaces so different
  // values can be used for different coordinates
  String[] coord = split(data, ' ');
  int index = 0;
  
  // Loop to handle all the drawing on screen
  for (int i = 0; i <=1; i++) {
    if (i == 0) {
      index = 0;
      fill(255, 0, 0);
      radius = r + 50;
    } else { 
      index = 2;
      fill(0, 255, 0);
      radius = r;
    }
    // Get angle and convert to radians so it can be used in calculations
    theta = radians(float(coord[index]));
    phi = radians(float(coord[index + 1])) + PI;

    println("Theta: " + theta);
    println("Phi: " + phi);
    println("Radius: " + radius);

    // fix: in OpenGL, y & z axes are flipped from math notation of spherical coordinates  
    x = radius * cos(theta) * cos(phi);
    y = -radius * sin(theta);
    z = -radius * cos(theta) * sin(phi);

    pushMatrix();
    translate(x, y, z);
    sphere(3);
    popMatrix();
  }
}