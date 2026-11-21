"""
Comprehensive Live Backend Verification Script for FloodSense FastAPI Service.

1. Spawns `uvicorn backend.app.main:app --host 127.0.0.1 --port 8000`.
2. Awaits startup and validates model loading.
3. Performs HTTP queries across all required endpoints and scenarios:
   - GET /health
   - GET /api/info
   - OPTIONS /api/analyze (CORS verification)
   - POST /api/analyze:
     * Critical: Active life threat (trapped families on roof, rising water)
     * High: Severe hazard (dam burst, water entering homes, collapsed bridge)
     * Moderate: Advisory (flood alert, river overflowing, precautions)
     * Low: Informational / emotional support (prayers for flood recovery)
     * Negated: Negative hazard claim (no flooding, no casualties)
     * Historical: Retrospective commentary (remembering 2018 floods)
     * Non-flood: Unrelated issue (traffic accident near market)
     * Validation Error: Empty message (HTTP 422)
4. Verifies response schemas, CORS headers, and status codes.
5. Shuts down the live server cleanly.
"""

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from typing import Any, Dict, Tuple

HOST = "127.0.0.1"
PORT = 8000
BASE_URL = f"http://{HOST}:{PORT}"


def http_request(
    method: str,
    path: str,
    data: Any = None,
    headers: Dict[str, str] = None,
) -> Tuple[int, Dict[str, str], Any]:
    url = f"{BASE_URL}{path}"
    req_headers = {"User-Agent": "FloodSense-Live-Verifier/1.0"}
    if headers:
        req_headers.update(headers)

    body = None
    if data is not None:
        body = json.dumps(data).encode("utf-8")
        req_headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=body, headers=req_headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            status_code = resp.status
            resp_headers = dict(resp.headers)
            content = resp.read().decode("utf-8")
            try:
                parsed_json = json.loads(content)
            except Exception:
                parsed_json = content
            return status_code, resp_headers, parsed_json
    except urllib.error.HTTPError as e:
        status_code = e.code
        resp_headers = dict(e.headers)
        content = e.read().decode("utf-8")
        try:
            parsed_json = json.loads(content)
        except Exception:
            parsed_json = content
        return status_code, resp_headers, parsed_json


def run_live_verification():
    print(f"--- Starting Live FastAPI Server on {BASE_URL} ---")
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "backend.app.main:app",
            "--host",
            HOST,
            "--port",
            str(PORT),
            "--log-level",
            "info",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    try:
        # Wait for server readiness
        print("Waiting for server startup...")
        server_ready = False
        for attempt in range(25):
            time.sleep(0.5)
            try:
                status, headers, body = http_request("GET", "/health")
                if status == 200 and body.get("analyzer_ready") is True:
                    server_ready = True
                    print(f"Server is online! (Attempt {attempt + 1})")
                    break
            except Exception:
                pass

        if not server_ready:
            print("ERROR: Server failed to start within timeout.")
            if proc.poll() is not None:
                stdout, _ = proc.communicate()
                print("Server crash log:\n", stdout)
            sys.exit(1)

        results = {}

        # 1. GET /health
        print("\n[1] Verifying GET /health...")
        status, headers, body = http_request("GET", "/health")
        print(f"Status: {status}")
        print("Response:", json.dumps(body, indent=2))
        assert status == 200
        assert body["status"] == "online"
        assert body["analyzer_ready"] is True
        results["health"] = {"status": status, "body": body}

        # 2. GET /api/info
        print("\n[2] Verifying GET /api/info...")
        status, headers, body = http_request("GET", "/api/info")
        print(f"Status: {status}")
        print("Response:", json.dumps(body, indent=2))
        assert status == 200
        assert body["system"] == "FloodSense"
        assert "humanitarian_classifier" in body["models"]
        results["info"] = {"status": status, "body": body}

        # 3. CORS Preflight Check (OPTIONS /api/analyze)
        print("\n[3] Verifying CORS Headers...")
        cors_headers = {
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        }
        status, headers, body = http_request("OPTIONS", "/api/analyze", headers=cors_headers)
        allow_origin = headers.get("access-control-allow-origin") or headers.get("Access-Control-Allow-Origin")
        print(f"OPTIONS Status: {status}")
        print(f"Access-Control-Allow-Origin header: {allow_origin}")
        assert allow_origin in ["*", "http://localhost:5173"]
        results["cors"] = {"status": status, "allow_origin": allow_origin}

        # 4. Realistic Test Messages
        test_cases = [
            (
                "Critical - Life Threat",
                "Water is rising rapidly near Aluva! 4 families are trapped on the terrace and need immediate boat rescue!",
                "Critical",
                True,
            ),
            (
                "High - Structural Ingress & Dam Burst",
                "The dam has burst and water is entering houses rapidly. Highway bridge collapsed.",
                "High",
                True,
            ),
            (
                "Moderate - Flood Warning & Advisory",
                "Flood alert issued for coastal zones. Flood warning in effect, river overflowing.",
                "Moderate",
                True,
            ),
            (
                "Low - Emotional Support / Prayers",
                "Heartfelt prayers and support for everyone dealing with flood recovery in Kerala.",
                "Low",
                True,
            ),
            (
                "Negated - Hazard Denied",
                "Situation is completely normal here, no flooding and no casualties reported.",
                "Not Applicable",
                False,
            ),
            (
                "Historical - Retrospective",
                "Remembering the devastating flood in 2018 when many people died and bridges were destroyed.",
                "Low",
                True,
            ),
            (
                "Non-Flood - Traffic Accident",
                "Car accident on main street near the vegetable market, police investigating.",
                "Not Applicable",
                False,
            ),
        ]

        print("\n[4] Sending Realistic Messages to POST /api/analyze...")
        results["test_cases"] = []

        for label, message, expected_sev, expected_flood in test_cases:
            print(f"\n--- Testing: {label} ---")
            payload = {"message": message}
            status, headers, body = http_request("POST", "/api/analyze", data=payload)
            print(f"HTTP Status: {status}")
            print(f"Flood Detected: {body.get('flood_detected')}")
            print(f"Severity Level: {body.get('severity', {}).get('level')}")
            print(f"Priority Score: {body.get('priority', {}).get('score')} ({body.get('priority', {}).get('tier')})")
            print(f"Humanitarian Context: {body.get('humanitarian_context')}")
            print(f"Supporting Indicators: {body.get('supporting_indicators')}")

            assert status == 200, f"Expected 200, got {status}"
            assert body["flood_detected"] == expected_flood
            if expected_flood:
                assert body["severity"]["level"] == expected_sev or (
                    expected_sev == "Moderate" and body["severity"]["level"] in ["Moderate", "High"]
                )

            results["test_cases"].append({
                "label": label,
                "input_message": message,
                "status_code": status,
                "flood_detected": body["flood_detected"],
                "severity_level": body["severity"]["level"],
                "priority_score": body["priority"]["score"],
                "priority_tier": body["priority"]["tier"],
                "humanitarian_category": body.get("humanitarian_context", {}).get("category") if body.get("humanitarian_context") else None,
                "supporting_indicators": body.get("supporting_indicators", []),
            })

        # 5. Error Handling & Validation
        print("\n[5] Verifying Error Handling...")
        # Empty string
        status, headers, body = http_request("POST", "/api/analyze", data={"message": ""})
        print(f"Empty message HTTP Status: {status} (Expected 422 Unprocessable Entity)")
        assert status == 422
        results["empty_validation"] = {"status": status}

        # Save verification log
        os.makedirs("reports/evaluation", exist_ok=True)
        with open("reports/evaluation/live_backend_verification.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print("\nFull verification results saved to reports/evaluation/live_backend_verification.json")

    finally:
        print("\n--- Shutting down test server ---")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        print("Server shutdown cleanly.")


if __name__ == "__main__":
    run_live_verification()
