#!/usr/bin/python3

import getopt
import sys
from collections import namedtuple

rd_x_min = -7e3
rd_x_max = 3e5
rd_y_min = 289e3
rd_y_max = 629e3

x0 = 155e3
y0 = 463e3

lat0 = 52.15517440
lon0 = 5.38720621

def fromWGS84toRD(lat, lon):
    coefficients_C = [
        (0, 1, 190066.98903),
        (1, 1, -11830.85831),
        (2, 1, -114.19754),
        (0, 3, -32.38360),
        (1, 0, -0.705),
        (3, 1, -2.34078),
        (1, 3, -0.60639),
        (2, 3, 0.15774),
        (0, 2, -0.608),
        (4, 1, -0.04158),
        (0, 5, -0.00661)]

    coefficients_D = [
        (1, 0, 309020.31810),
        (0, 2, 3638.36193),
        (2, 0, 72.97141),
        (1, 2, -157.95222),
        (3, 0, 59.79734),
        (0, 1, 0.433),
        (2, 2, -6.43481),
        (0, 4, 0.09351),
        (3, 2, -0.07379),
        (1, 4, -0.05419),
        (1, 1, 0.092),
        (4, 0, -0.03444)]


    x = x0
    y = y0

    lat = 0.36 * (lat - lat0)
    lon = 0.36 * (lon - lon0)

    for p, q, c in coefficients_C:
        x += (p+q) * c * lat**p * lon**q
    for p, q, c in coefficients_D:
        y += (p+q) * c * lat**p * lon**q

    if x < rd_x_min or x > rd_x_max:
        print('error -> x-value out of bounds')
        sys.exit(3)
    if y < rd_y_min or y > rd_y_max:
        print('error -> y-value out of bounds')
        sys.exit(3)

    CoordinatesRD = namedtuple('RD', ['x', 'y'])

    return CoordinatesRD(x=x, y=y)

def fromRDtoWGS84(x, y):
    coefficients_A = [
        (0, 1, 3235.65389),
        (2, 0, -32.58297),
        (0, 2, -0.24750),
        (2, 1, -0.84987),
        (0, 3, -0.06550),
        (2, 2, -0.01709),
        (1, 0, -0.00738),
        (4, 0, 0.00530),
        (2, 3, -0.00039),
        (4, 1, 0.00033),
        (1, 1, -0.00012)]
    
    coefficients_B = [
        (1, 0, 5260.52916),
        (1, 1, 105.94684),
        (1, 2, 2.45656),
        (3, 0, -0.81885),
        (1, 3, 0.05594),
        (3, 1, -0.05607),
        (0, 1, 0.01199),
        (3, 2, -0.00256),
        (1, 4, 0.00128),
        (0, 2, 0.00022),
        (2, 0, -0.00922),
        (5, 0, 0.00026)]

    if x < rd_x_min or x > rd_x_max:
        print('error -> x-value out of bounds')
        sys.exit(3)
    if y < rd_y_min or y > rd_y_max:
        print('error -> y-value out of bounds')
        sys.exit(3)


    # RD -> Bessel (spherical coords, approximation)

    x = (x - x0) * 1e-6
    y = (y - y0) * 1e-6

    lat = lat0
    lon = lon0

    for p, q, c in coefficients_A:
        lat += ((p+q)*c * x**p * y**q) / 3600
    for p, q, c in coefficients_B:
        lon += ((p+q)*c * x**p * y**q) / 3600

    CoordinatesWGS84 = namedtuple('WGS84', ['lat', 'lon'])

    return CoordinatesWGS84(lat=lat, lon=lon)

def main(argv):
    x, y, lat, lon = None, None, None, None

    try:
        opts, args = getopt.getopt(argv, "x:y:", ["lat=", "lon="])
    except getopt.GetoptError:
        print("""Available flags:\n\t-x <x-coordinate> -y <y-coordinate>\t(RD -> WGS84)\n\t--lat
              <latitude> --lon <lonitude>\t(WGS84 -> RD)""")
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print("""Convert RD coordinates to WGS84 spherical coordinates.\nAvailable flags:\n\t-x <x-coordinate> -y
                  <y-coordinate> \t(RD -> WGS84)\n\t--lat <latitude> --lon <lonitude>\t(WGS84 -> RD)""")
            sys.exit(0)
        elif opt in ("-x"):
            x = float(arg)
        elif opt in ("-y"):
            y = float(arg)
        elif opt in ("--lat"):
            lat = float(arg)
        elif opt in ("--lon"):
            lon = float(arg)

    if x is not None and y is not None:
        print(fromRDtoWGS84(x, y))
        sys.exit(0)
    if lat is not None and lon is not None:
        print(fromWGS84toRD(lat, lon))
        sys.exit(0)

    sys.exit(1)

if __name__ == "__main__":
    main(sys.argv[1:])
