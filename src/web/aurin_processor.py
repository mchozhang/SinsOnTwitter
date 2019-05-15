# -*- encoding: utf-8 -*-
#
# 1.clean aurin database
# 2.import aurin data into couchdb

import csv
import os
import couchdb
from collections import Counter
from utils.config import *
from utils.geo_utils import LgaMapper, Sa4Mapper

basedir = os.path.dirname(os.path.abspath(__file__))

couch = couchdb.Server(COUCHDB_URL)
couch.resource.credentials = (COUCHDB_USER, COUCHDB_PW)

FILE_ADULT_HEALTH = "resources/adult_health_risk_factor_estimates.csv"
FILE_CRIME_RATE = "resources/crime_rate_2011_for_south_australia.csv"
FILE_DOMESTIC_VIOLENCE = "resources/domestic_violence_incidents_by_location.csv"
FILE_PERSONAL_INCOME = "resources/estimates_of_personal_income.csv"


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
        return 0


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
        return 0


if __name__ == "__main__":
    lga_mapper = LgaMapper()
    sa4_mapper = Sa4Mapper()

    if DATABASE_AURIN in couch:
        couch.delete(DATABASE_AURIN)
    aurin_db = couch.create(DATABASE_AURIN)

    # adult health database
    with open(os.path.join(basedir, FILE_ADULT_HEALTH)) as file:
        if DATABASE_ADULT_HEALTH in couch:
            couch.delete(DATABASE_ADULT_HEALTH)
        db = couch.create(DATABASE_ADULT_HEALTH)

        sloth_count = Counter()
        total_population = Counter()
        reader = csv.reader(file)
        head_row = next(reader)
        for row in reader:
            if "null" in row:
                continue
            lga_name = row[0]
            lga_code = row[1]
            sloth_rate = float(row[2]) / 100
            population = lga_mapper.get_lga_population(lga_name)
            state_name = lga_mapper.get_state_name(lga_name)
            doc = dict()
            doc["lga_name"] = lga_name
            doc["lga_code"] = lga_code
            doc["sloth_rate"] = sloth_rate
            doc["population"] = population
            doc["state_name"] = state_name
            doc["state_code"] = lga_mapper.get_state_code(lga_name)
            db.save(doc)

            if state_name is not None:
                total_population.update({state_name: population})
                sloth_count.update({state_name: sloth_rate * population})

        sloth_rate = dict()
        for state in sloth_count.keys():
            sloth_rate[state] = float(sloth_count[state] / total_population[state])
        aurin_db["sloth_rate"] = sloth_rate

    # personal income database
    with open(os.path.join(basedir, FILE_PERSONAL_INCOME)) as file:
        if DATABASE_PERSONAL_INCOME in couch:
            couch.delete(DATABASE_PERSONAL_INCOME)
        db = couch.create(DATABASE_PERSONAL_INCOME)
        reader = csv.reader(file)
        head_row = next(reader)
        for row in reader:
            if "null" in row:
                continue

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
    with open(os.path.join(basedir, FILE_DOMESTIC_VIOLENCE)) as file:
        if DATABASE_DOMESTIC_VIOLENCE in couch:
            couch.delete(DATABASE_DOMESTIC_VIOLENCE)
        db = couch.create(DATABASE_DOMESTIC_VIOLENCE)

        state = "New South Wales"
        violence_count = 0
        total_population = 0
        reader = csv.reader(file)
        head_row = next(reader)
        for row in reader:
            if "null" in row:
                continue

            doc = dict()
            violence_ratio = get_violence_rate(row[0])
            lga_code = row[4]
            lga_name = row[6]
            population = lga_mapper.get_lga_population(lga_name)
            doc["violence_ratio"] = violence_ratio
            doc["lga_code"] = lga_code
            doc["lga_name"] = lga_name
            doc["population"] = population
            doc["state_name"] = lga_mapper.get_state_name(lga_name)
            doc["state_code"] = lga_mapper.get_state_code(lga_name)
            db.save(doc)
            total_population += population
            violence_count += population * violence_ratio
        violence_rate = float(violence_count / total_population)
        aurin_db["violence_rate"] = {state: violence_rate}

    # crime rate database
    with open(os.path.join(basedir, FILE_CRIME_RATE)) as file:
        if DATABASE_CRIME_RATE in couch:
            couch.delete(DATABASE_CRIME_RATE)
        db = couch.create(DATABASE_CRIME_RATE)
        state = "South Australia"
        reader = csv.reader(file)
        head_row = next(reader)
        total_population = 0
        sexual_offences_count = 0
        person_offences_count = 0
        robbery_count = 0
        for row in reader:
            doc = dict()
            sexual_offences = get_crime_rate(row[0])
            person_offences = get_crime_rate(row[2])
            robbery_and_extortion_offences = get_crime_rate(row[5])
            lga_code = row[4]
            lga_name = row[1]
            state_code = row[3]
            population = lga_mapper.get_lga_population(lga_name)

            doc["sexual_offences"] = sexual_offences
            doc["person_offences"] = person_offences
            doc["robbery_and_extortion_offences"] = robbery_and_extortion_offences
            doc["lga_code"] = lga_code
            doc["lga_name"] = lga_name
            doc["population"] = population
            doc["state_name"] = lga_mapper.get_state_name(lga_name)
            doc["state_code"] = state_code
            db.save(doc)

            total_population += population
            sexual_offences_count += population * sexual_offences
            person_offences_count += population * person_offences
            robbery_count += population * robbery_and_extortion_offences

        sexual_offences_rate = float(sexual_offences_count / total_population)
        person_offences_rate = float(person_offences_count / total_population)
        robbery_rate = float(robbery_count / total_population)

        aurin_db["sexual_offences_rate"] = {state: sexual_offences_rate}
        aurin_db["person_offences_rate"] = {state: person_offences_rate}
        aurin_db["robbery_rate"] = {state: robbery_rate}
