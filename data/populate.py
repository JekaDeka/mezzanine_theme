import csv
import os
from profiles.models import *
from itertools import islice

path = '/home/t/tvdeniy4/handmaker.top/HelloDjango/data/'
os.chdir(path)
os.getcwd()
objs = ()

country_list = []
region_list = []
city_list = []
with open('_country.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        a = Country(id=row['country_id'], name=row['name'])
        country_list.append(a)


with open('_region.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        cnt = 0
        for country in country_list:
            if country.id == row['country_id']:
                cnt = country
        b = Region(id=row['region_id'], name=row['name'], country=cnt)
        region_list.append(b)

with open('_city.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        cnt = 0
        reg = 0
        for country in country_list:
            if country.id == row['country_id']:
                cnt = country

        for region in region_list:
            if region.id == row['region_id']:
                reg = region

        c = City(id=row['city_id'], name=row['name'], country=cnt, region=reg)
        city_list.append(c)

Country.objects.bulk_create(country_list)
Region.objects.bulk_create(region_list)
City.objects.bulk_create(city_list)

# with open('_country.csv') as csvfile:
#     reader = csv.DictReader(csvfile)
#     objs = (Country(id=row['country_id'], name=row['name']) for row in reader)
# csvfile.close()
#
# batch_size = 200
# while True:
#     batch = list(islice(objs, batch_size))
#     if not batch:
#         break
#     Country.objects.bulk_create(batch, batch_size)
