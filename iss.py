# The position vector measures the satellite position in kilometers from the center of the earth.
# The velocity is the rate at which those three parameters are changing, expressed in kilometers per second.
# read data from spacetrack
from spacetrack import SpaceTrackClient

# sgp4 realated for calculations
from sgp4.earth_gravity import wgs72
from sgp4.io import twoline2rv
import math
from time import strftime, sleep
from jplephem.spk import SPK
from jdcal import gcal2jd
import numpy as np
import urllib2
import json
import argparse
import geocoder
import socket

# Handle command line arguments
parser = argparse.ArgumentParser(description="""Give coordinates of celestial body
													Format:
														- Mars
														- Earth
														- Saturn""")
parser.add_argument('-o', '--object', metavar='', required=True, help='Which object do you wish to track')
args = parser.parse_args()


def find_lat(x, y, z):
    return math.atan(y / x)


def find_lng(x, y, z):
    return math.atan(z / math.sqrt(x + y))


# ------------------------------------------------------------------- #
# Global variables
planets = ['ISS', 'Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter', 'Saturn', 'Neptune', 'Uranus', 'Pluto', 'Sun']
my_coord = [0, 0, 0]
obj_coord = [0, 0, 0]
obj = ''
message = ''
earthradius = 6371

# Gets my coordinates
me = geocoder.ip('me')

# Get date and time of request and format it to print
timeNow = strftime("%Y/%m/%d/%H/%M/%S").split('/', 5)
date = 'Date: ' + timeNow[2] + '/' + timeNow[1] + '/' + timeNow[0] + ' - ' + timeNow[3] + ':' + timeNow[4] + ':' + timeNow[5]
print(date)

# ------------------------------------------------------------------- #
# ----------------------- Set server -------------------------------- #
# Your IP address
HOST = '192.168.1.69'
PORT = 8080

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(1)

client, addr = s.accept()
print('Connected by', addr)

# ------------------------------------------------------------------- #
# ----------------------- Main code --------------------------------- #
kernel = SPK.open('de430.bsp')
ju = gcal2jd(timeNow[0], timeNow[1], timeNow[2])
julian = ju[0] + ju[1]

# Add my coordinates to the message
# Print my coordinates
print('My latitude: ' + str(me.lat) + '\n' + 'My longitude: ' + str(me.lng))

# Print which object we are looking at
print(args.object)

while True:
    # For the iss other api is used
    if args.object == 'ISS':
		req = urllib2.Request("http://api.open-notify.org/iss-now.json")
        response = urllib2.urlopen(req)

        obj = json.loads(response.read())

        # message = "Latitude: " + obj['iss_position']['latitude'] + ' ' + "Longitude: " + obj['iss_position']['longitude'] + '\n'
        message = obj['iss_position']['latitude'] + ' ' + obj['iss_position']['longitude'] + ' ' + str(me.lat) + ' ' + str(me.lng) + '\n'
        obj_lat = float(obj['iss_position']['latitude'])
        obj_lng = float(obj['iss_position']['latitude'])
        objradius = earthradius + 405

    elif args.object == 'Moon':
        pos = kernel[3, 301].compute(julian)  # 399 is the code for moon

    else:
        # calculations needed to get the distance from planet to the center of earth
        pos = kernel[0, planets.index(args.object)].compute(julian)
        pos -= kernel[0, planets.index('Earth')].compute(julian)
        pos -= kernel[3, 399].compute(julian)  # 399 is the code for moon

    try:
        # Calculate square of coordinates to get the spherical coordinates
        x = pos[0]**2
        y = pos[1]**2
        z = pos[2]**2

        # Find distance between center of earth and object
        radius = math.sqrt(x + y + z)
        objradius = radius - earthradius

        # Find the angles
        obj_lng = find_lat(pos[0], pos[1], pos[2])
        obj_lat = find_lng(pos[0], pos[1], pos[2])
    except Exception:
        pass

    print message

    my_phi = math.radians(me.lat)
    my_omega = math.radians(me.lng)
    print "My angles radians: % f % f " % (my_phi, my_omega)

    obj_phi = math.radians(obj_lat)
    obj_omega = math.radians(obj_lng)
    print "Obj angles radians: % f % f \n" % (obj_phi, obj_omega)

    #message = str(obj_phi) + ' ' + str(obj_omega)

    # Get my [X Y Z]
    my_coord[0] = earthradius * math.cos(my_omega) * math.sin(my_phi)
    my_coord[1] = earthradius * math.sin(my_omega) * math.sin(my_phi)
    my_coord[2] = earthradius * math.cos(my_phi)
    print "My coordinates: % f % f % f " % (my_coord[0], my_coord[1], my_coord[2])

    # Get obj [X Y Z]
    obj_coord[0] = objradius * math.cos(obj_omega) * math.sin(obj_phi)
    obj_coord[1] = objradius * math.sin(obj_omega) * math.sin(obj_phi)
    obj_coord[2] = objradius * math.cos(obj_phi)
    print "Obj coordinates: % f % f % f \n" % (obj_coord[0], obj_coord[1], obj_coord[2])

    # Create numpy array for matrix calculations
    my_array = np.asarray(my_coord)
    obj_array = np.asarray(obj_coord)

    # Get distance between the obj and me
    distance = np.subtract(my_array, obj_array)

    # Find angle cos()= dot()/mag()*mag()
    dot = np.dot(my_array, obj_array)
    my_mag = np.linalg.norm(my_array)
    obj_mag = np.linalg.norm(obj_array)

    var = dot / (my_mag * obj_mag)

    angle = math.acos(var)

    print "My magnitude: %.2f" % (my_mag)
    print "Obj magnitude: %.2f \n" % (obj_mag)
    print "Distance: %f" % (np.linalg.norm(distance))
    print "Angle vectors: %f" % (math.degrees(angle))

    print "--------------------------------"
    client.send(message)
    sleep(5)

s.close()
