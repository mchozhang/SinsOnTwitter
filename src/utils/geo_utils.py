"""
utility class
read LGA_StateMapping.csv, map lga to state
"""
import csv
from collections import Counter

states = ["Western Australia", "Queensland", "Tasmania",
          "Victoria", "New South Wales", "South Australia"]

class LgaMapper:
    def __init__(self):
        self.state_name_dict = dict()
        self.state_code_dict = dict()
        self.lga_population_dict = dict()
        self.state_population_counter = Counter()

        with open("../resources/LGA_StateMapping.csv") as file:
            reader = csv.reader(file)
            head_row = next(reader)
            for row in reader:
                # map LGA name to state name, e.g. { "melbourne" : "victoria"}
                self.state_name_dict[row[2]] = row[0]
                # map LGA name to state code, e.g. { "melbourne" : "2" }
                self.state_code_dict[row[2]] = row[1]

        with open("../resources/LGA_Codes_and_Names.csv") as file:
            reader = csv.reader(file)
            head_row = next(reader)
            for row in reader:
                # map LGA name to lga population, e.g. { "melbourne" : "128980"}
                lga_name = row[1]
                pop = row[3]
                population = int(float(row[3]))
                self.lga_population_dict[lga_name] = population
                self.state_population_counter.update({self.get_state_name(lga_name): population})

    def get_state_name(self, lga_name):
        """
        get state name
        :param lga_name: lga name
        :return: state name
        """
        name = self.state_name_dict.get(lga_name)
        if is_state(name):
            return name
        return None

    def get_state_code(self, lga_name):
        """
        get state code
        :param lga_name: lga name
        :return: state code
        """
        return self.state_code_dict.get(lga_name)

    def get_lga_population(self, lga_name):
        """
        get population of a LGA area
        :param lga_name: lga name
        :return: LGA population
        """
        return self.lga_population_dict.get(lga_name, 0)

    def get_state_population(self, state_name):
        """
        get population of a state
        :param state_name: state name
        :return: state population
        """
        return self.state_population_counter.get(state_name)


class Sa4Mapper:
    def __init__(self):
        self.state_name_dict = dict()
        self.state_code_dict = dict()
        with open("../resources/SA4_2016_AUST.csv") as file:
            reader = csv.reader(file)
            head_row = next(reader)
            for row in reader:
                # map sa4 name to state name: { "melbourne" : "victoria"}
                self.state_name_dict[row[1]] = row[5]

                # map sa4 name to state code, e.g. { "melbourne" : "2" }
                self.state_code_dict[row[1]] = row[4]

    def get_state_name(self, sa4_name):
        """
        get state name
        :param sa4_name: sa4 name
        :return: state name
        """
        return self.state_name_dict.get(sa4_name)

    def get_state_code(self, sa4_name):
        """
        get state code
        :param sa4_name: sa4 name
        :return: state code
        """
        return self.state_code_dict.get(sa4_name)


def is_state(name):
    return name in states


def get_state_list():
    return states
