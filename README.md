# ISS_Tracker
Simple program that gets the current position of the International Space Station and outputs in a processing simulation.


The code might seem a bit confusing but it is because the initial idea was to be able to get the position of the ISS and of any planet in the solar system and use an Arduino controlled arm to point to the current position of that planet. I still plan to implement such idea but I don't have time now, so I just made a simple simulation in Processing.

The code works by using the open-notify api which returns in JSON format the current latitude and longitude of the ISS. I am not sure why but when I make the API request from Processing the simulation gets very slow so I decided to continue using the python code which was already finished and just transmit the data through an TCP server.

