import json
import os
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Any
from flask import Flask, request, jsonify

DB_PATH = os.environ.get("RTX_TELEMETRY_DB", os.path.join(os.path.dirname(__file__), "telemetry_data.json"))
HOST = os.environ.get("RTX_TELEMETRY_HOST", "0.0.0.0")
PORT = int(os.environ.get("RTX_TELEMETRY_PORT", "8080"))
ACTIVE_MINUTES = int(os.environ.get("RTX_TELEMETRY_ACTIVE_MINUTES", "10"))

lock = threading.Lock()
app = Flask(__name__)

def now_iso() -> str:
	return datetime.utcnow().isoformat() + "Z"

def load_db() -> Dict[str, Any]:
	if not os.path.exists(DB_PATH):
		return {
			"users": {},
			"totals": {
				"uniqueUsers": 0,
				"sessions": 0,
				"emailsSent": 0,
				"testEmailsSent": 0,
				"campaignsScheduled": 0,
				"campaignsRun": 0,
				"events": 0
			},
			"lastUpdated": now_iso()
		}
	with open(DB_PATH, "r", encoding="utf-8") as f:
		try:
			return json.load(f)
		except Exception:
			return {
				"users": {},
				"totals": {"uniqueUsers": 0, "sessions": 0, "emailsSent": 0, "testEmailsSent": 0, "campaignsScheduled": 0, "campaignsRun": 0, "events": 0},
				"lastUpdated": now_iso()
			}

def save_db(db: Dict[str, Any]) -> None:
	with open(DB_PATH, "w", encoding="utf-8") as f:
		json.dump(db, f, indent=2)

DB = load_db()


def record_events(payload: Dict[str, Any]) -> Dict[str, Any]:
	install_id = payload.get("installId") or "unknown"
	platform = payload.get("platform") or ""
	app_version = payload.get("appVersion") or ""
	events = payload.get("events") or []
	utc_now = now_iso()

	with lock:
		user = DB["users"].get(install_id) or {
			"firstSeen": utc_now,
			"lastSeen": utc_now,
			"lastAuthSuccess": None,
			"platform": platform,
			"versions": [],
			"sessions": 0,
			"emailsSent": 0,
			"testEmailsSent": 0
		}
		updated = False
		if platform and user.get("platform") != platform:
			user["platform"] = platform
			updated = True
		if app_version and app_version not in user["versions"]:
			user["versions"].append(app_version)
			updated = True

		for ev in events:
			etype = (ev.get("event") or "").lower()
			DB["totals"]["events"] += 1
			if etype == "app_start":
				user["sessions"] += 1
				DB["totals"]["sessions"] += 1
			elif etype == "auth_success":
				user["lastAuthSuccess"] = utc_now
			elif etype == "email_sent":
				user["emailsSent"] += 1
				DB["totals"]["emailsSent"] += 1
			elif etype == "test_email_sent":
				user["testEmailsSent"] += 1
				DB["totals"]["testEmailsSent"] += 1
			elif etype == "campaign_scheduled":
				DB["totals"]["campaignsScheduled"] += 1
			elif etype == "campaign_run":
				DB["totals"]["campaignsRun"] += 1

		user["lastSeen"] = utc_now
		DB["users"][install_id] = user
		DB["totals"]["uniqueUsers"] = len(DB["users"])
		DB["lastUpdated"] = utc_now
		save_db(DB)
		return user

@app.post("/telemetry")
def telemetry():
	try:
		payload = request.get_json(force=True, silent=False)
		user = record_events(payload or {})
		return jsonify({"ok": True, "user": user}), 200
	except Exception as e:
		return jsonify({"ok": False, "error": str(e)}), 400

@app.get("/")
def summary():
	with lock:
		db = DB
		cutoff = datetime.utcnow() - timedelta(minutes=ACTIVE_MINUTES)
		active = 0
		logged_in = 0
		for u in db["users"].values():
			try:
				last_seen = datetime.fromisoformat(u["lastSeen"].replace("Z", ""))
			except Exception:
				continue
			if last_seen >= cutoff:
				active += 1
				las = u.get("lastAuthSuccess")
				if las:
					try:
						if datetime.fromisoformat(las.replace("Z", "")) >= cutoff:
							logged_in += 1
					except Exception:
						pass
		summary_obj = {
			"uniqueUsers": db["totals"]["uniqueUsers"],
			"activeUsersLastMinutes": active,
			"loggedInUsersLastMinutes": logged_in,
			"sessions": db["totals"]["sessions"],
			"emailsSent": db["totals"]["emailsSent"],
			"testEmailsSent": db["totals"]["testEmailsSent"],
			"campaignsScheduled": db["totals"]["campaignsScheduled"],
			"campaignsRun": db["totals"]["campaignsRun"],
			"events": db["totals"]["events"],
			"lastUpdated": db["lastUpdated"]
		}
		return jsonify(summary_obj)


def dashboard_loop():
	while True:
		with lock:
			cutoff = datetime.utcnow() - timedelta(minutes=ACTIVE_MINUTES)
			active = 0
			logged_in = 0
			for u in DB["users"].values():
				try:
					last_seen = datetime.fromisoformat(u["lastSeen"].replace("Z", ""))
					if last_seen >= cutoff:
						active += 1
						las = u.get("lastAuthSuccess")
						if las and datetime.fromisoformat(las.replace("Z", "")) >= cutoff:
							logged_in += 1
				except Exception:
					pass
			os.system('cls' if os.name == 'nt' else 'clear')
			print("RTX Telemetry Collector (Ctrl+C to stop)\n")
			print(f"Unique users: {DB['totals']['uniqueUsers']}")
			print(f"Active (last {ACTIVE_MINUTES}m): {active}")
			print(f"Logged in (last {ACTIVE_MINUTES}m): {logged_in}")
			print(f"Sessions: {DB['totals']['sessions']}")
			print(f"Emails sent: {DB['totals']['emailsSent']}")
			print(f"Test emails sent: {DB['totals']['testEmailsSent']}")
			print(f"Campaigns scheduled: {DB['totals']['campaignsScheduled']}")
			print(f"Campaigns run: {DB['totals']['campaignsRun']}")
			print(f"Events: {DB['totals']['events']}")
			print(f"Last updated: {DB['lastUpdated']}")
		time.sleep(5)

if __name__ == "__main__":
	threading.Thread(target=dashboard_loop, daemon=True).start()
	app.run(host=HOST, port=PORT, debug=False, use_reloader=False) 