"""
utility class
read LGA_StateMapping.csv, map lga to state
"""
import csv


class LgaMapper:
    def __init__(self):
        self.state_name_dict = dict()
        self.state_code_dict = dict()
        with open("../resources/LGA_StateMapping.csv") as file:
            reader = csv.reader(file)
            head_row = next(reader)
            for row in reader:
                # map LGA name to state name, e.g. { "melbourne" : "victoria"}
                self.state_name_dict[row[2]] = row[0]
                # map LGA name to state code, e.g. { "melbourne" : "2" }
                self.state_code_dict[row[2]] = row[1]

    def get_state_name(self, lga_name):
        """
        get state name
        :param lga_name: lga name
        :return: state name
        """
        return self.state_name_dict.get(lga_name)

    def get_state_code(self, lga_name):
        """
        get state code
        :param lga_name: lga name
        :return: state code
        """
        return self.state_code_dict.get(lga_name)


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
