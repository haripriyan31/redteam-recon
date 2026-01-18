import requests
import time
import json

BASE_URL = "http://localhost:8000"

def test_scan_and_features():
    print("[*] Starting Test: Scan + Scoring + Export")
    
    # 1. Start Scan
    payload = {"domain": "scanme.nmap.org", "scan_types": ["ports"]}
    try:
        r = requests.post(f"{BASE_URL}/api/scan", json=payload)
        r.raise_for_status()
        scan_id = r.json()["id"]
        print(f"[+] Scan started. ID: {scan_id}")
    except Exception as e:
        print(f"[-] Failed to start scan: {e}")
        return

    # 2. Poll for completion (timeout 30s)
    for _ in range(10):
        time.sleep(3)
        try:
            r = requests.get(f"{BASE_URL}/api/scan/{scan_id}")
            data = r.json()
            status = data["status"]
            print(f"[*] Status: {status}")
            
            if status in ["completed", "failed"]:
                break
        except:
            pass
            
    # 3. Check Results
    if status == "completed":
        print("[+] Scan completed.")
        
        # Check Scoring
        score = data.get("attack_score", 0)
        print(f"[*] Attack Score: {score}")
        if score > 0:
            print("[+] Scoring verified (Score > 0).")
        else:
            print("[-] Scoring verification failed (Score is 0). verify logic.")
            
        # Check Vulns
        vulns = data.get("vulnerabilities", [])
        print(f"[*] Vulnerabilities Found: {len(vulns)}")
        for v in vulns:
            print(f"    - {v}")
            
        # Check Export
        print("[*] Testing SpiderFoot Export...")
        try:
            r_export = requests.get(f"{BASE_URL}/api/scan/{scan_id}/export/spiderfoot")
            if r_export.status_code == 200:
                print("[+] Export endpoint reachable.")
                content = r_export.text
                if "Internet Name,scanme.nmap.org" in content:
                    print("[+] CSV Content verified.")
                else:
                    print(f"[-] CSV Content malformed: {content[:50]}...")
            else:
                 print(f"[-] Export endpoint failed: {r_export.status_code}")
        except Exception as e:
            print(f"[-] Export test failed: {e}")

    else:
        print("[-] Scan timed out or failed.")

if __name__ == "__main__":
    test_scan_and_features()
