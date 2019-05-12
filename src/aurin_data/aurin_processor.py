# -*- encoding: utf-8 -*-
#
# clean aurin database, and
# import aurin data into couchdb

import csv
import couchdb
from utils.geo_utils import LgaMapper, Sa4Mapper

couch = couchdb.Server('http://localhost:5984/')
couch.resource.credentials = ("admin", "admin")
# couch = couchdb.Server('http://45.113.235.192:5984/')
# couch.resource.credentials = ("SinsOnTwitter", "group68")

FILE_ADULT_HEALTH = "../resources/adult_health_risk_factor_estimates.csv"
FILE_CRIME_RATE = "../resources/crime_rate_2011_for_south_australia.csv"
FILE_DOMESTIC_VIOLENCE = "../resources/domestic_violence_incidents_by_location.csv"
FILE_PERSONAL_INCOME = "../resources/estimates_of_personal_income.csv"

DATABASE_ADULT_HEALTH = "adult_health"
DATABASE_DOMESTIC_VIOLENCE = "domestic_violence"
DATABASE_CRIME_RATE = "crime_rate"
DATABASE_PERSONAL_INCOME = "personal_income"


def get_violence_rate(value):
    """
    calculate violence rate,
    rate = value / 100000
    :param value: number per 100000 person
    :return: violence rate
    """
    try:
        return float(value) / 100000
    except:
        return None


def get_crime_rate(value):
    """
    calculate crime rate,
    rate = value / 1000
    :param value: number per 1000 person
    :return: violence rate
    """
    try:
        return float(value) / 1000
    except:
        return None


if __name__ == "__main__":
    lga_mapper = LgaMapper()
    sa4_mapper = Sa4Mapper()

    # adult health database
    with open(FILE_ADULT_HEALTH, encoding='utf-8') as file:
        if DATABASE_ADULT_HEALTH in couch:
            couch.delete(DATABASE_ADULT_HEALTH)
        db = couch.create(DATABASE_ADULT_HEALTH)

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
            doc["population"] = lga_mapper.get_lga_population(lga_name)
            doc["state_name"] = lga_mapper.get_state_name(lga_name)
            doc["state_code"] = lga_mapper.get_state_code(lga_name)
            db.save(doc)

    # personal income database
    with open(FILE_PERSONAL_INCOME) as file:
        if DATABASE_PERSONAL_INCOME in couch:
            couch.delete(DATABASE_PERSONAL_INCOME)
        db = couch.create(DATABASE_PERSONAL_INCOME)
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
            doc["state_name"] = sa4_mapper.get_state_name(sa4_name)
            doc["state_code"] = sa4_mapper.get_state_code(sa4_name)
            db.save(doc)

    # domestic violence database
    with open(FILE_DOMESTIC_VIOLENCE) as file:
        if DATABASE_DOMESTIC_VIOLENCE in couch:
            couch.delete(DATABASE_DOMESTIC_VIOLENCE)
        db = couch.create(DATABASE_DOMESTIC_VIOLENCE)
        reader = csv.reader(file)
        head_row = next(reader)
        for row in reader:
            doc = dict()
            violence_ratio = get_violence_rate(row[0])
            lga_code = row[4]
            lga_name = row[6]
            doc["violence_ratio"] = violence_ratio
            doc["lga_code"] = lga_code
            doc["lga_name"] = lga_name
            doc["population"] = lga_mapper.get_lga_population(lga_name)
            doc["state_name"] = lga_mapper.get_state_name(lga_name)
            doc["state_code"] = lga_mapper.get_state_code(lga_name)
            db.save(doc)

    # crime rate database
    with open(FILE_CRIME_RATE) as file:
        if DATABASE_CRIME_RATE in couch:
            couch.delete(DATABASE_CRIME_RATE)
        db = couch.create(DATABASE_CRIME_RATE)
        reader = csv.reader(file)
        head_row = next(reader)
        for row in reader:
            doc = dict()
            sexual_offences = get_crime_rate(row[0])
            person_offences = get_crime_rate(row[2])
            robbery_and_extortion_offences = get_crime_rate(row[5])
            lga_code = row[4]
            lga_name = row[1]
            state_code = row[3]
            doc["sexual_offences"] = sexual_offences
            doc["person_offences"] = person_offences
            doc["robbery_and_extortion_offences"] = robbery_and_extortion_offences
            doc["lga_code"] = lga_code
            doc["lga_name"] = lga_name
            doc["population"] = lga_mapper.get_lga_population(lga_name)
            doc["state_name"] = lga_mapper.get_state_name(lga_name)
            doc["state_code"] = state_code
            db.save(doc)
