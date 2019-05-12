# -*- encoding: utf-8 -*-
#
# flask app

from flask import Flask, render_template, jsonify, request

app = Flask(__name__, instance_relative_config=True)

SIN_LIST = []


@app.route('/')
def home():
    """
    home page
    :return: html template
    """
    # option_list = get_aurin_databases();
    option_list = [
        {"sin": "Wrath", "states": ["nsw"], "databases": ["Domestic Violence"]},
        {"sin": "Greed", "states": ["south_au"],
         "databases": [" Robbery And Extortion Offences Rate per 1000 Population"]},
        {"sin": "Lust", "states": ["south_au"], "databases": ["Sexual Assaults Rate per 1000 Population"]},
        {"sin": "Sloth", "states": ["all"],
         "databases": ["Estimated Number of People Who Did Low or No Exercise – ASR per 100 Population"]},
        {"sin": "Greed", "states": ["all"], "databases": ["Income Imbalance P80/P20"]},

    ];

    option = [
        {"sin": "Wrath", "datasets": [{"states": "nsw", "database": ["Domestic Violence"]},
                                      {"states": "south_au", "database": "Person assault"}]},

        {"sin": "Greed", "datasets": [{"states": "south_au", "database": [" All Robbery And Extortion Offences"]}]},

        {"sin": "Lust",
         "datasets": [{"states": "south_au", "database": ["Sexual Assaults Rate per 1000 Population"]}]},

        {"sin": "Sloth", "datasets": [{"states": "all", "database": [
            "Estimated Number of People Who Did Low or No Exercise – ASR per 100 Population"]}]},

    ];

    return render_template("home.html", option_list=option_list)


@app.route('/sin', methods=['GET'])
def get_options():
    """
    get state and aurin database name option by choosing sin
    :return:
    """
    result = dict()
    try:
        sin = request.json["sin"]
    except Exception as e:
        print(e)
    return jsonify(result)


@app.route('/search', methods=['POST'])
def search():
    try:
        keyword_list = request.json["keywords"]
        sin = request.json["sin"]
        state = request.json["state"]
        database = request.json["database"]
        field = request.json["field"]
        chart = request.json["chart"]

        print(str(keyword_list))
        print(str(database))
        print(sin + " " + chart + " " + state)
        return_data = {}

        # get_aurin_data(database, field)
    except Exception as e:
        print(e)
    return_data = {
        "Wrath": {
            "vic":
                {"percentage_of_tweets": 0.19, "aurin_data": 0.2},
            "nsw":
                {"percentage_of_tweets": 0.5, "aurin_data": 0.1},
            "que":
                {"percentage_of_tweets": 0.5, "aurin_data": 0.3},
            "tas":
                {"percentage_of_tweets": 0.2, "aurin_data": 0.3},
            "west_au":
                {"percentage_of_tweets": 0.5, "aurin_data": 0.5},
            "south_au":
                {"percentage_of_tweets": 0.09, "aurin_data": 0.8}},

        "Lust": {
            "vic":
                {"percentage_of_tweets": 0.19, "aurin_data": 0.4},
            "nsw":
                {"percentage_of_tweets": 0.5, "aurin_data": 0.23},
            "que":
                {"percentage_of_tweets": 0.5, "aurin_data": 0.6},
            "tas":
                {"percentage_of_tweets": 0.2, "aurin_data": 0.21},
            "west_au":
                {"percentage_of_tweets": 0.5, "aurin_data": 0.56},
            "south_au":
                {"percentage_of_tweets": 0.09, "aurin_data": 0.11}},
        "Sloth":
            {
                "vic":
                    {"percentage_of_tweets": 0.19, "aurin_data": 0.2},
                "nsw":
                    {"percentage_of_tweets": 0.5, "aurin_data": 0.03},
                "que":
                    {"percentage_of_tweets": 0.5, "aurin_data": 0.32},
                "tas":
                    {"percentage_of_tweets": 0.2, "aurin_data": 0.67},
                "west_au":
                    {"percentage_of_tweets": 0.5, "aurin_data": 0.5},
                "south_au":
                    {"percentage_of_tweets": 0.09, "aurin_data": 0.53}},
        "Greed": {
            "vic":
                {"percentage_of_tweets": 0.19, "aurin_data": 0.62},
            "nsw":
                {"percentage_of_tweets": 0.5, "aurin_data": 0.16},
            "que":
                {"percentage_of_tweets": 0.5, "aurin_data": 0.43},
            "tas":
                {"percentage_of_tweets": 0.2, "aurin_data": 0.6},
            "west_au":
                {"percentage_of_tweets": 0.5, "aurin_data": 0.52},
            "south_au":
                {"percentage_of_tweets": 0.09, "aurin_data": 0.13}}
    }

    return jsonify(return_data)


@app.route('/geoChart')
def geoChart():
    return render_template("geoChart.html", key="AIzaSyCCenQXMA4w-cRUrMjs8AhK3_CqHy-E-SI")


@app.route('/bar_chart')
def bar():
    return render_template("home.html", content="this is a testing")


def connect_db():
    return;


def get_twitter_data(sin, keyword_list, state):
    """

    :param sin:
    :param keyword_list: a  list of keywordList to search tweets
    :param state: state name
    :return: get TwitterData result, for example, percentage of number of swearing tweets in the state
     {"sin": "Lust", "state": "New South Wales", "percentage of sin twitter": 0.19]
     ... },
    """
    return;


def get_aurin_data(database, field):
    """

    :param database: database_id
    :param field: the field to view
    :return: the statisc number of each state
    {"state":"New South Wales", "value of field": 0.23}
    """
    return;


def get_aurin_databases():
    """
    get the list of aurin
    :param sin:
    :return: what databases are there for each sin, for example,
       {"sin": "Lust", "states": ["New South Wales"], "databases_name": ["Rape", "Sexual Offences"]},
       ...}
    """
    return;


labels = [
    'JAN', 'FEB', 'MAR', 'APR',
    'MAY', 'JUN', 'JUL', 'AUG',
    'SEP', 'OCT', 'NOV', 'DEC'
]

values = [
    967.67, 1190.89, 1079.75, 1349.19,
    2328.91, 2504.28, 2873.83, 4764.87,
    4349.29, 6458.30, 9907, 16297
]

colors = [
    "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
    "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
    "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]

if __name__ == '__main__':
    app.run()
