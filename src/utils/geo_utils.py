"""
utility class
read LGA_StateMapping.csv, map lga to state
"""
import csv


class GeoMapper:
    def __init__(self):
        self.lganame_statename = dict()
        self.lganame_statecode = dict()
        with open("../resources/LGA_StateMapping.csv") as file:
            reader = csv.reader(file)
            for row in reader:
                # map lga name to state name: { "melbourne" : "victoria"}
                self.lganame_statename[row[2]] = row[0]
                self.lganame_statecode[row[2]] = row[1]

    def get_state_name(self, lga_name):
        """
        get state name
        :param lga_name: lga name
        :return: state name
        """
        return self.lganame_statename[lga_name]

    def get_state_code(self, lga_name):
        """
        get state code
        :param lga_name: lga name
        :return: state code
        """
        return self.lganame_statecode[lga_name]
