from flask import Flask, render_template, request, redirect, session, jsonify
import requests
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # 用來管理 session

TDX_CLIENT_ID = os.environ.get("TDX_CLIENT_ID")
TDX_CLIENT_SECRET = os.environ.get("TDX_CLIENT_SECRET")
PASSWORD = "onlyme123"  # ✅ 修改這裡設定密碼

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

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("pw") == PASSWORD:
            session["authenticated"] = True
            return redirect("/home")
        else:
            return "❌ 密碼錯誤"
    return """
        <form method='post'>
            <input type='password' name='pw' placeholder='請輸入密碼'>
            <button type='submit'>進入</button>
        </form>
    """

@app.route("/home")
def index():
    if not session.get("authenticated"):
        return redirect("/")
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
