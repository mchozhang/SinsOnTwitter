# -*- encoding: utf-8 -*-
#
# import aurin data into couchdb

import csv
import couchdb
from utils.geo_utils import GeoMapper

couch = couchdb.Server('http://localhost:5984/')
couch.resource.credentials = ("admin", "admin")

FILE_ADULT_HEALTH = "../resources/adult_health_risk_factor_estimates.csv"
FILE_CRIME_NUMBER = "../resources/crime_number_2011_for_south_australia.csv"
FILE_DOMESTIC_VIOLENCE = "../resources/domestic_violence_incidents_by_location.csv"
FILE_PERSONAL_INCOME = "../resources/estimates_of_personal_income.csv"

DATABASE_ADULT_HEALTH = "adult_health"
DATABASE_PERSONAL_INCOME = "personal_income"

geo_mapper = GeoMapper()

# adult health database
with open(FILE_ADULT_HEALTH, encoding='utf-8') as file:
    if DATABASE_ADULT_HEALTH not in couch:
        couch.create(DATABASE_ADULT_HEALTH)
    db = couch[DATABASE_ADULT_HEALTH]

    reader = csv.reader(file)
    head_row = next(reader)
    for row in reader:
        lga_name = row[0]
        lga_code = row[1]
        sloth_rate = row[2]
        doc = dict()
        doc["lga_name"] = lga_name
        doc["lga_code"] = lga_code
        doc["sloth_rate"] = sloth_rate
        doc["state_name"] = geo_mapper.get_state_name(lga_name)
        doc["state_code"] = geo_mapper.get_state_code(lga_name)
        db.save(doc)

# personal income database
with open(FILE_PERSONAL_INCOME) as file:
    if DATABASE_PERSONAL_INCOME not in couch:
        couch.create(DATABASE_PERSONAL_INCOME)
    db = couch[DATABASE_PERSONAL_INCOME]
    reader = csv.reader(file)
    head_row = next(reader)
    for row in reader:
        doc = dict()
        rich_poor_ratio = row[0]
        income_aud = row[1]
        sa4_name = row[2]
        sa4_code = row[3]
        doc["rich_poor_ratio"] = rich_poor_ratio
        doc["income_aud"] = income_aud
        doc["sa4_name"] = sa4_name
        doc["sa4_code"] = sa4_code
        db.save(doc)
