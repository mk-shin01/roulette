# -*- coding: utf-8 -*-
import os, sys, webbrowser, logging, traceback, ctypes
from flask import Flask, jsonify, request, render_template
from roulette_core import RouletteStore

# ---- 로깅 설정 (사용자 홈 폴더) ----
def _log_path():
    base = os.path.join(os.path.expanduser("~"), ".roulette")
    os.makedirs(base, exist_ok=True)
    return os.path.join(base, "roulette_app.log")

logging.basicConfig(
    filename=_log_path(),
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    encoding="utf-8"
)
logging.info("===== App start =====")

# ---- PyInstaller 템플릿 경로 ----
BASE_PATH = getattr(sys, "_MEIPASS", os.path.abspath("."))
TEMPLATE_DIR = os.path.join(BASE_PATH, "templates")
logging.info(f"BASE_PATH={BASE_PATH}")
logging.info(f"TEMPLATE_DIR={TEMPLATE_DIR}")

def _msgbox(txt: str):
    try:
        ctypes.windll.user32.MessageBoxW(0, txt, "Roulette", 0)
    except Exception:
        pass

app = Flask(__name__, template_folder=TEMPLATE_DIR)
store = RouletteStore()
logging.info("Flask app + store initialized")

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/api/items")
def get_items():
    return jsonify({
        "menus": store.list_menus(),
        "places": store.list_places(),
        **store.get_weights(),
    })

@app.post("/api/add")
def add_item():
    data = request.get_json(force=True)
    kind = data.get("type")
    name = (data.get("name") or "").strip()
    w = data.get("weight")
    if not name or kind not in ("menu","place"):
        return jsonify({"error":"bad request"}), 400
    if kind == "menu":
        store.add_menu(name, w)
    else:
        store.add_place(name, w)
    return jsonify({"ok": True})

@app.post("/api/remove")
def remove_item():
    data = request.get_json(force=True)
    kind = data.get("type")
    name = (data.get("name") or "").strip()
    if not name or kind not in ("menu","place"):
        return jsonify({"error":"bad request"}), 400
    if kind == "menu":
        store.remove_menu(name)
    else:
        store.remove_place(name)
    return jsonify({"ok": True})

@app.post("/api/weight")
def set_weight():
    data = request.get_json(force=True)
    kind = data.get("type")
    name = (data.get("name") or "").strip()
    w = data.get("weight")
    if not name or kind not in ("menu","place") or w is None:
        return jsonify({"error":"bad request"}), 400
    try:
        if kind == "menu":
            store.set_menu_weight(name, float(w))
        else:
            store.set_place_weight(name, float(w))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"ok": True})

@app.post("/api/spin")
def spin():
    try:
        res = store.spin()
        return jsonify(res)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    # 개발 환경에서는 debug=True로 실행
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
    try:
        port = 5000  # 필요하면 5050 등으로 변경
        url = f"http://127.0.0.1:{port}"
        logging.info(f"Starting server on {url}")
        try:
            webbrowser.open(url)
        except Exception as e:
            logging.exception(f"webbrowser.open failed: {e}")
        app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)
    except Exception as e:
        logging.exception("FATAL in app.run")
        _msgbox("Fatal error:\n" + traceback.format_exc())