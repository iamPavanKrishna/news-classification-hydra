from flask import Flask, request, render_template
import requests
import validators
import subprocess

app = Flask(__name__)

SPARK_SERVER = "http://spark:9999/"
data = []
final_data = {}

category_list = ['POLITICS', "WELLNESS", 'ENTERTAINMENT',
                 "STYLE & BEAUTY", "TRAVEL", "PARENTING",
                 "FOOD & DRINK", "QUEER VOICES", "HEALTHY LIVING",
                 "BUSINESS", "COMEDY", "SPORTS", "HOME & LIVING",
                 "BLACK VOICES", "THE WORLDPOST", "WEDDINGS", "PARENTS",
                 "DIVORCE", "WOMEN", "IMPACT", "CRIME",
                 "MEDIA", "WEIRD NEWS", "WORLD NEWS", "TECH",
                 "GREEN", "TASTE", "RELIGION", "SCIENCE",
                 "MONEY", "STYLE", "ARTS & CULTURE", "ENVIRONMENT",
                 "WORLDPOST", "FIFTY", "GOOD NEWS", "LATINO VOICES",
                 "CULTURE & ARTS", "COLLEGE", "EDUCATION", "ARTS"]


@app.route("/",methods=["GET", "POST"])
def home():
    return render_template("index.html")


@app.route("/ping",methods=["GET","TRACE"])
def ping():
    if request.method == "GET":
        url = SPARK_SERVER + "ping"
        r = requests.get(url)
        return {'status':200, 'result':r.json()}
    elif request.method == "TRACE":
        return "ping trace method"


@app.route("/classify_news",methods=["POST","TRACE"])
def classify_news():
    global data, final_data
    if request.method == "POST":
        url = request.form.get("url")
        if validators.url(url):
            spark_url = SPARK_SERVER + 'classify_news'
            r = requests.post(spark_url, data=str(url)).json()

            predictions = r['pred']
            probabilities = r['probs']
            original_data = r['o_data']
            data = []
            num = 1
            for o_data, pred, prob in zip(original_data, predictions, probabilities):
                temp = {"num": num, "data": o_data, "pred": category_list[pred], "prob": round(prob * 100)}
                data.append(temp)
                num += 1
            final_data = {"data": data, "len": len(data)}
        else:
            return render_template("index.html", data="invalid")
    return render_template("admin/index.html", data=final_data)


@app.route("/add_news",methods=["POST","TRACE"])
def add_news():
    given_request = request.get_json()
    if request.method == "POST":
        if {'timeout','topic'} == set(given_request.keys()):
            topic = given_request.pop('topic')
            proc1 = subprocess.Popen(f"python3 /app/news_streamer.py '{topic}' {given_request['timeout']}", shell = True)
            url = SPARK_SERVER + "add_news"
            r = requests.post(url, json=given_request)
            return {'status':201, 'result':r.json()}
        else:
            return {'status':501, 'result':'all required keys are not given'}
    elif request.method == "TRACE":
        return given_request


@app.route("/train",methods=["POST","TRACE"])
def train():
    given_request = request.get_json()
    if request.method == "POST":
        url = SPARK_SERVER + "train"
        r = requests.post(url)
        return {'status':200, 'result':r.json()}
    elif request.method == "TRACE":
        return given_request

