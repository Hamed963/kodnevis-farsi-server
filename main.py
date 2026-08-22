from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import tempfile
import os

app = Flask(__name__)
CORS(app)


@app.get("/")
def home():
    return jsonify({
        "status": "online",
        "message": "Python server is running"
    })


@app.get("/health")
def health():
    return jsonify({
        "status": "ok"
    })


@app.post("/run")
def run_python():

    data = request.get_json(silent=True) or {}

    code = data.get("code", "")

    if not code.strip():
        return jsonify({
            "success": False,
            "error": "کد Python ارسال نشده است."
        }), 400

    filename = None

    try:

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8"
        ) as file:

            file.write(code)
            filename = file.name

        result = subprocess.run(
            ["python", filename],
            capture_output=True,
            text=True,
            timeout=5
        )

        return jsonify({
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr
        })

    except subprocess.TimeoutExpired:

        return jsonify({
            "success": False,
            "error": "زمان اجرای کد تمام شد."
        }), 408

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

    finally:

        if filename and os.path.exists(filename):
            os.remove(filename)


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )
