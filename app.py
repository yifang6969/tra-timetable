from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

TDX_CLIENT_ID = os.environ.get("TDX_CLIENT_ID")
TDX_CLIENT_SECRET = os.environ.get("TDX_CLIENT_SECRET")

def get_tdx_token():
    url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
    headers = { "Content-Type": "application/x-www-form-urlencoded" }
    data = {
        "grant_type": "client_credentials",
        "client_id": TDX_CLIENT_ID,
        "client_secret": TDX_CLIENT_SECRET
    }
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print("Token error:", response.text)
        return None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/stations")
def get_stations():
    token = get_tdx_token()
    if not token:
        return jsonify({"error": "token error"}), 500
    r = requests.get("https://tdx.transportdata.tw/api/basic/v2/Rail/TRA/Station", headers={"Authorization": f"Bearer {token}"})
    return jsonify(r.json())

@app.route("/api/timetable")
def get_timetable():
    origin = request.args.get("from")
    destination = request.args.get("to")
    date = request.args.get("date")
    token = get_tdx_token()
    if not token:
        return jsonify({"error": "token error"}), 500
    url = f"https://tdx.transportdata.tw/api/basic/v2/Rail/TRA/DailyTimetable/OD/{origin}/to/{destination}/{date}"
    r = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    return jsonify(r.json())

if __name__ == "__main__":
    app.run()
