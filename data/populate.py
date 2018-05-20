import csv
import os
os.getcwd()
from profiles.models import *
from itertools import islice

path = '/home/t/tvdeniy4/handmaker.top/HelloDjango/data/'
os.chdir(path)
objs = ()
with open('_country.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    objs = (Country(id=row['country_id'], name=row['name']) for row in reader)


batch_size = 200
while True:
    batch = list(islice(objs, batch_size))
    if not batch:
        break
    Country.objects.bulk_create(batch, batch_size)
