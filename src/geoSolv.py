#!/usr/bin/python3

from nominatim import Nominatim


def query(query_string):
    nom = Nominatim()
    results = nom.query(query_string) if query != '' else None

    if results is not None and len(results) >= 1:
        return results
    else:
        return None

def fuzzyTextMatch(housenumber='', streetname='', placename='', provincename='', countryname='Netherlands', postalcode='',\
                   max_diff=.4, interactive=True):
    from difflib import SequenceMatcher

    attrs = {'housenumber':housenumber, 'streetname':streetname,\
             'placename':placename, 'provincename':provincename,\
             'countryname':countryname, 'postalcode':postalcode}

    ask = True
    qresults = None
    while qresults is None:
        query_string = ', '.join([arg for arg in [attrs['housenumber'], attrs['streetname'], attrs['placename'],\
                              attrs['provincename'], attrs['countryname'], attrs['postalcode']] if arg != ''])
        streethouse = ' '.join([attrs['streetname'], attrs['housenumber']]) if attrs['housenumber'] != ''\
                        else attrs['streetname']
        pretty = ', '.join([arg for arg in [streethouse,\
                                                      attrs['placename'], attrs['postalcode'],\
                                                      attrs['provincename'], attrs['countryname']] if arg != ''])

        qresults = query(query_string)
        if qresults is None:
            if not interactive:
                (attrs, q, ask) = generalize_query(attrs, 'y')
            if ask:
                print("\nUnable to find a geo match on '{}'".format(pretty))
                q = input(" Generalize query? (y[es], n[o] (*), m[anual select]): ")
            if q == 'y' or q == 'm':
                (attrs, q, ask) = generalize_query(attrs, q)
            else:
                break

    if qresults is None:
        return None

    candidates = []
    for entry in qresults:
        d = SequenceMatcher(None, query_string.strip().lower(), entry['display_name'].strip().lower()).ratio()
        if d >= 1.0 - max_diff:
            candidates.append((d, entry['display_name'], entry['class'], entry['lat'], entry['lon']))

    nskipped = len(qresults) - len(candidates)
    if nskipped > 0:
        print(" - Skipped {} candidate(s) with diff >= {}".format(nskipped, max_diff))

    if candidates == []:
        return None

    candidates.sort(reverse=True) # dublicate entries?
    if not interactive:
        return (candidates[0][3], candidates[0][4])

    return fuzzyTextMatchUI(candidates, pretty)

def generalize_query(attrs, mode='y'):
    ask = True
    if mode == 'y':
        if attrs['countryname'] != '' and (attrs['placename'] != '' or attrs['postalcode'] != ''):
            if attrs['housenumber'] != '':
                attrs['housenumber'] = ''
            elif attrs['postalcode'] != '' and attrs['placename'] != '':
                attrs['postalcode'] = ''
            elif attrs['provincename'] != '':
                attrs['provincename'] = ''
        else:
            print(" - Failed to generalize geospatial entity")
            mode = 'n'
        ask = False
    elif mode == 'm':
        print(" Available attributes:")
        for k,v in attrs.items():
            if v != '':
                print("  {}\t :\t {}".format(k,v))

        r = input(" Omit attribute (empty cancels): ")

        if r in attrs.keys():
            attrs[r] = ''
        else:
            print(" - Key Error")

    return (attrs, mode, ask)

def fuzzyTextMatchUI(candidates, query_string):
    print("\nDetected Possible Geo Alignment on: {}".format(query_string))

    for i, (d, name, ctype, lat, lon) in enumerate(candidates, 1):
        print(" Candidate Solution ({}% match) {} / {}".format(int(d*100), i, len(candidates)))
        print(" Candidate: \t{}\t({})".format(name, ctype))
        print(" ( http://www.openstreetmap.org/?lat={}&lon={}&zoom=17&layers=M )".format(lat, lon))

        while True:
            q = input(" Align? (y[es] / n[o] / s[kip] (*)): ")
            if q == 'y':
                return (lat, lon)
            elif q == 'n':
                break
            else:
                return None

            print()

    return None
