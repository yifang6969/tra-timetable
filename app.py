from flask import Flask, render_template, request, redirect, session, jsonify
import requests
import os

USE_DOTENV = True
if USE_DOTENV:
    from dotenv import load_dotenv
    load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

TDX_CLIENT_ID = os.environ.get("TDX_CLIENT_ID")
TDX_CLIENT_SECRET = os.environ.get("TDX_CLIENT_SECRET")
PASSWORD = "123"

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

    headers = {"Authorization": f"Bearer {token}"}

    # 查表定時刻
    timetable_url = f"https://tdx.transportdata.tw/api/basic/v2/Rail/TRA/DailyTimetable/OD/{origin}/to/{destination}/{date}"
    timetable = requests.get(timetable_url, headers=headers).json()

    # 查出發站的 LiveBoard（即時動態）
    
    live_url = f"https://tdx.transportdata.tw/api/basic/v2/Rail/TRA/LiveBoard/Station/{origin}"
    live_data = requests.get(live_url, headers=headers).json()
    live_map = {item["TrainNo"]: item.get("DelayTime", 0) for item in live_data}
    #print(live_data)

    enriched = []
    for item in timetable:
        train_no = item["DailyTrainInfo"]["TrainNo"]
        dep = item["OriginStopTime"]["DepartureTime"]
        arr = item["DestinationStopTime"]["ArrivalTime"]
        delay = live_map.get(train_no)
        if delay is not None:
            status = f"🚆 誤點 {delay} 分鐘" if delay else "✅ 準點"
        else:
            status = "無即時資訊"
        enriched.append({
            "TrainNo": train_no,
            "DepartureTime": dep,
            "ArrivalTime": arr,
            "Delay": delay,
            "Status": status
        })
    return jsonify(enriched)

if __name__ == "__main__":
    app.run(debug=True)
