from flask import Flask, render_template, jsonify, request

app = Flask(__name__)


@app.route('/')
def home():
    crime_list = ['lust', 'wraith', 'sloth', 'gluttony']
    return render_template("home.html", crime_list=crime_list)


@app.route('/search', methods=['POST'])
def search():
    try:
        keyword_list = request.json["keywords"]
        crime = request.json["crime"]
        chart = request.json["chart"]
        sentiment = request.json["sentiment"]
        print(str(keyword_list))
        print(crime + " " + chart + " " + sentiment)
    except Exception as e:
        print(e)
    return jsonify()


@app.route('/bar_chart')
def bar():
    return render_template("home.html", content="this is a testing")


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
