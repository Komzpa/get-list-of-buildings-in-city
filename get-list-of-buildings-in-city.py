#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psycopg2
import json
import sys
import re
import lxml.etree
from lxml.etree import tostring
from lxml.builder import E

reload(sys)
sys.setdefaultencoding("utf-8")

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ atoi(c) for c in re.split('(\d+)', text) ]
database = "dbname=gis user=gis"

cities = {}

a = psycopg2.connect(database)
a.autocommit = True
cursor = a.cursor()

status_mapping = {u"улица": u"ул.", u"проспект": u"просп.", u"переулок": u"пер.", u"шоссе": u"шос.", u"поселок": u"пос.", u"посёлок": u"пос.", u"бульвар": u"бул.", u"площадь": u"пл."}
for v in status_mapping.values():
    status_mapping[v] = v

def mangle_street(street):
    street = street.replace(".", ". ")
    street = unicode(street).split()

    status = []
    restreet = []
    for part in street:
        if len(part) == 2 and part[1] == ".":
            continue
        if part.lower() in status_mapping:
            status.append(status_mapping[part.lower()])
        else:
            restreet.append(part)
    street = restreet + status
    street = " ".join(street)
    return street

cursor.execute("""select "addr:city" as city, "name" as street, "addr:housenumber" as house, ST_X(ST_Transform(ST_PointOnSurface(way), 4326)) as lon, ST_Y(ST_Transform(ST_PointOnSurface(way), 4326)) as lat from geocode_osm_line where tags?'highway' and "addr:city" is not null and "name" is not null;""")

names = [q[0] for q in cursor.description]

for row in cursor.fetchall():
    v = dict(map(None, names, row))
    cities[v['city']] = cities.get(v['city'], {})
    v["street"] = mangle_street(v["street"])
    cities[v['city']][v['street']] = cities[v['city']].get(v['street'], {})


cursor.execute("""select "addr:city" as city, "addr:street" as street, "addr:housenumber" as house, ST_X(ST_Transform(ST_PointOnSurface(way), 4326)) as lon, ST_Y(ST_Transform(ST_PointOnSurface(way), 4326)) as lat from geocode_osm_point where "addr:housenumber" is not null and "addr:city" is not null and "addr:street" is not null;""")

names = [q[0] for q in cursor.description]

for row in cursor.fetchall():
    v = dict(map(None, names, row))
    cities[v['city']] = cities.get(v['city'], {})
    v["street"] = mangle_street(v["street"])
    cities[v['city']][v['street']] = cities[v['city']].get(v['street'], {})
    cities[v['city']][v['street']][v['house']] = (v['lon'], v['lat'])


cursor.execute("""select "addr:city" as city, "addr:street" as street, "addr:housenumber" as house, ST_X(ST_Transform(ST_PointOnSurface(way), 4326)) as lon, ST_Y(ST_Transform(ST_PointOnSurface(way), 4326)) as lat from geocode_osm_polygon where "addr:housenumber" is not null and "addr:city" is not null and "addr:street" is not null;""")

names = [q[0] for q in cursor.description]

for row in cursor.fetchall():
    v = dict(map(None, names, row))
    cities[v['city']] = cities.get(v['city'], {})
    v["street"] = mangle_street(v["street"])
    cities[v['city']][v['street']] = cities[v['city']].get(v['street'], {})
    cities[v['city']][v['street']][v['house']] = (v['lon'], v['lat'])

for city, streets in cities.iteritems():
    addresses = lxml.etree.Element("addresses")
    streetnames = streets.keys()
    streetnames.sort(key=natural_keys)
    for street in streetnames:
        houses = streets[street]
        streetel = lxml.etree.Element("street", name=street)
        hnos = houses.keys()
        hnos.sort(key=natural_keys)
        for hno in hnos:
            coords = houses[hno]
            streetel.append(lxml.etree.Element("house", name=unicode(hno), lon=unicode(coords[0]), lat=unicode(coords[1])))
        addresses.append(streetel)
    c = open(city.replace('/','')+".xml", 'w')
    print >> c, tostring(addresses, pretty_print = True, encoding="utf-8")
    c.close()
