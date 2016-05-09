# -*- coding: utf-8 -*-
# Copyright (C) 2012 Riccardo Apolloni
'''
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

For detail about GNU see <http://www.gnu.org/licenses/>.
'''
import math

# CONSTANTS
EARTH_RADIUS = 60.0*360/(2*math.pi)  # in Nautical Miles
# for an idealized spherical Earth.


# FUNCTIONS
def offset(latA, lonA, Distance, Heading):
    # Takes a position (lat,lon)
    # a distance in nautical miles and a direction in 0-360
    # calculates where you would end up if you started a journey at that
    # heading and moved in a "straight line" (Great Circle)
    # Does not function correctly near the poles
    # I think this is the cosine method
    # haversine would be more accurate
    a = Distance * 1.0 / EARTH_RADIUS
    latB = latA + a * math.cos(Heading)
    if math.copysign(latA-latB, 1) <= math.radians(0.1/3600.0):
        q = math.cos(latA)
    else:
        Df = math.log(math.tan(latB/2+math.pi/4)
                      / math.tan(latA/2+math.pi/4),
                      math.e)
        q = (latB - latA) / Df
    lonB = lonA - a * math.sin(Heading) / q
    return latB, lonB


def loxodrome(latA, lonA, latB, lonB):  # lossodromica
    # Rhumb line navigation
    # Takes two points on earth and returns:
    # the distance and constant (true) bearing one would need to
    # follow to reach it.
    # Doesn't function near poles:
    # but you shouldn't be sailing near the poles anyways!
    # when latB = -90: math domain error log(0)
    # when latA = -90 [zero divison error]
    # when A==B returns (0.0,0.0)
    # if latA == latB:
    if math.copysign(latA-latB, 1) <= math.radians(0.1/3600.0):
        q = math.cos(latA)
    else:
        Df = math.log(math.tan(latB/2+math.pi/4)
                      / math.tan(latA/2+math.pi/4), math.e)
        q = (latB-latA) * 1.0/Df
    Distance = EARTH_RADIUS * ((latA-latB)**2+(q*(lonA-lonB))**2)**0.5
    Heading = math.atan2(-q*(lonB-lonA), (latB-latA))
    if Heading < 0:
        Heading = Heading + 2.0 * math.pi  # atan2:[-pi,pi]
    return Distance, Heading


def orthodrome(latA, lonA, latB, lonB):  # ortodromica
    # Great Circle Navigation
    # For two points on the earths surface:
    # returns the INITIAL heading and distance needed to
    # arrive at the second point starting at the first.
    # should be parallel to "offset" above
    Distance = (math.cos(latA)
                * math.cos(latB)
                * math.cos(lonB-lonA)
                + math.sin(latA)
                * math.sin(latB)
                )
    Distance = EARTH_RADIUS * math.acos(Distance)
    x = (math.cos(latA)
         * math.sin(latB)
         - math.sin(latA)
         * math.cos(latB)
         * math.cos(lonB-lonA)
         )
    y = (math.sin(lonB-lonA)
         * math.cos(latB)
         )
    Heading = math.atan2(-y, x)
    if Heading < 0:
        Heading = Heading + 2.0 * math.pi  # atan2:[-pi,pi]
    return Distance, Heading


def range360(radians):  # def riduci360(alfa):
    # input is in radians
    # cannot get my head around this yet
    n = int(radians * 0.5/math.pi)
    n = math.copysign(n, 1)
    if radians > 2.0 * math.pi:  # 6.28319 for argument
        radians = radians - n * 2.0 * math.pi
    if radians < 0:
        radians = (n+1) * 2.0 * math.pi + radians
    if radians > 2.0 * math.pi or radians < 0:
        print "error range360"
    return radians


def range180(radians):  # def riduci180(alfa):
    # input in radians
    if radians > math.pi:
        radians = radians - 2 * math.pi
    if radians < -math.pi:
        radians = 2 * math.pi + radians
    if radians > math.pi or radians < -math.pi:
        print "error range180"
    return radians


def delta(route1, route2):  # def scartorotta(rotta1, rotta2):
    # return the smallest angle between two routes
    delta = math.copysign(route1 - route2, 1)
    if delta > math.pi:
        delta = 2 * math.pi - delta
    return delta


def print_lat(lat):  # def stampalat(lat):
    # returns a string in the format xxDegrees,xxMinutes, N/S
    lat_decimal = math.copysign(math.degrees(lat), 1)  # latdecimali
    lat_degree = int(lat_decimal)  # latgradi
    lat_minute = (lat_decimal - lat_degree) * 60  # latprimi
    if lat_minute > 59.51:
        lat_degree = lat_degree + 1
        lat_minute = 0
    else:
        if lat_minute - int(lat_minute) > 0.51:
            lat_minute = int(lat_minute) + 1
        else:
            lat_minute = int(lat_minute)
    if lat > 0:
        hemisphere = "N"  # segno
    else:
        hemisphere = "S"
    gradi = "%2d" % lat_degree  # gradi
    primi = "%2d" % lat_minute  # primi
    lat = (gradi.replace(" ", "0") + u"°" + primi.replace(" ", "0")
           + "'" + hemisphere)
    return lat


def print_lon(lon):  # def stampalon(lon):
    # returns a string in the format xxDegrees,xxMinutes, N/S
    lon_decimal = math.copysign(math.degrees(lon), 1)  # londecimali
    lon_degree = int(lon_decimal)  # longradi
    lon_minutes = (lon_decimal - lon_degree) * 60  # lonprimi
    if lon_minutes > 59.51:
        lon_degree = lon_degree + 1
        lon_minutes = 0
    else:
        if lon_minutes - int(lon_minutes) > 0.51:
            lon_minutes = int(lon_minutes) + 1
        else:
            lon_minutes = int(lon_minutes)
    if lon > 0:
        hemisphere = "W"
    else:
        hemisphere = "E"
    degrees = "%3d" % lon_degree  # gradi
    minutes = "%2d" % lon_minutes
    lon = (degrees.replace(" ", "0") + u"°" + minutes.replace(" ", "0")
           + "'" + hemisphere)
    return lon
