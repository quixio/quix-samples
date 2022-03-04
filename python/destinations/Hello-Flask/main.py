from flask import Flask

app = Flask("Hello Flask")

@app.route("/")
def hello_world():
    return "<p>Hello, Flask!</p>"

app.run(debug=True, host="0.0.0.0", port=80)