#!/usr/bin/python3

from nominatim import Nominatim


def asWGS84(housenumber='', streetname='', placename='', provincename='', countryname='', postalcode=''):
    nom = Nominatim()

    query = ', '.join([arg for arg in [housenumber, streetname, placename, provincename, countryname, postalcode] if arg != ''])
    results = nom.query(query) if query != '' else None

    if results is not None and len(results) >= 1:
        return (results[0]['lat'], results[0]['lon'])
    else:
        return None

