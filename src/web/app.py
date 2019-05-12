# -*- encoding: utf-8 -*-
#
# flask app

from flask import Flask, render_template, jsonify, request

app = Flask(__name__, instance_relative_config=True)


@app.route('/')
def home():
    """
    home page
    :return: html template
    """
    option_list = [
        {"sin": "Lust", "states": ["New South Wales"], "databases": ["Rape", "Sexual Offences"]},
        {"sin": "Wrath", "states": ["All", "New South Wales", "South Australia"],
         "databases": ["Violence", "Street Brawl"]},
        {"sin": "Sloth", "states": ["Victoria", "Queensland"], "databases": ["Strike"]},
        {"sin": "Greed", "states": ["Tasmania"], "databases": ["Robbery", "Theft"]},
    ]
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
        database_list = request.json["databases"]
        chart = request.json["chart"]
        print(str(keyword_list))
        print(str(database_list))
        print(sin + " " + chart + " " + state)
    except Exception as e:
        print(e)
    return jsonify()


@app.route('/geoChart')
def geoChart():
    return render_template("geoChart.html", key="AIzaSyCCenQXMA4w-cRUrMjs8AhK3_CqHy-E-SI")


@app.route('/bar_chart')
def bar():
    return render_template("home.html", content="this is a testing")


if __name__ == '__main__':
    app.run()
