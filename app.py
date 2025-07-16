from flask import Flask, render_template, request, redirect, session, jsonify
import requests
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

TDX_CLIENT_ID = os.environ.get("TDX_CLIENT_ID")
TDX_CLIENT_SECRET = os.environ.get("TDX_CLIENT_SECRET")
PASSWORD = "onlyme123"

def get_tdx_token():
    url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": TDX_CLIENT_ID,
        "client_secret": TDX_CLIENT_SECRET
    }
    r = requests.post(url, headers=headers, data=data)
    return r.json().get("access_token") if r.status_code == 200 else None

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("pw") == PASSWORD:
            session["authenticated"] = True
            return redirect("/home")
        return "❌ 密碼錯誤"
    return """
        <form method='post'>
            <input type='password' name='pw' placeholder='請輸入密碼'>
            <button type='submit'>進入</button>
        </form>
    """

@app.route("/home")
def home():
    if not session.get("authenticated"):
        return redirect("/")
    return render_template("index.html")

@app.route("/api/stations")
def get_stations():
    token = get_tdx_token()
    url = "https://tdx.transportdata.tw/api/basic/v2/Rail/TRA/Station"
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(url, headers=headers)
    return jsonify(r.json())

@app.route("/api/timetable")
def get_timetable():
    origin = request.args.get("from")
    destination = request.args.get("to")
    date = request.args.get("date")
    token = get_tdx_token()

    # 表定資料
    timetable_url = f"https://tdx.transportdata.tw/api/basic/v2/Rail/TRA/DailyTimetable/OD/{origin}/to/{destination}/{date}"
    timetable = requests.get(timetable_url, headers={"Authorization": f"Bearer {token}"}).json()

    # 即時資料
    realtime_url = "https://tdx.transportdata.tw/api/basic/v2/Rail/TRA/RealTimeTrain/Today"
    realtime_resp = requests.get(realtime_url, headers={"Authorization": f"Bearer {token}"})
    try:
        realtime = realtime_resp.json()
    except:
        realtime = []

    if not isinstance(realtime, list):
        realtime = []

    realtime_map = {item["TrainNo"]: item for item in realtime}

    # 合併資訊
    enriched = []
    for item in timetable:
        train_no = item["DailyTrainInfo"]["TrainNo"]
        dep = item["OriginStopTime"]["DepartureTime"]
        arr = item["DestinationStopTime"]["ArrivalTime"]
        delay = 0
        status = "無即時資訊"
        if train_no in realtime_map:
            delay = realtime_map[train_no].get("DelayTime", 0)
            status = "🚆 誤點 {} 分鐘".format(delay) if delay else "✅ 準點"
        enriched.append({
            "TrainNo": train_no,
            "DepartureTime": dep,
            "ArrivalTime": arr,
            "Delay": delay,
            "Status": status
        })
    return jsonify(enriched)

if __name__ == "__main__":
    app.run()
