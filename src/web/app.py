from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def home():
    return render_template("home.html")


# add more pages
@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/map")
def map():
    return render_template("map.html")


if __name__ == '__main__':
    app.run()

