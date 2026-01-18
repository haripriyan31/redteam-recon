from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import sys

# Fix for Playwright on Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from uuid import uuid4
from datetime import datetime
from typing import Dict, List

from .schemas import ScanRequest, ScanResult, SubdomainResult, PortResult
from .services.subdomain import SubdomainService
from .services.port_scan import PortScanService
from .services.osint import OsintService
from .services.fuzzing import FuzzingService
from .services.fuzzing import FuzzingService
from .services.visual_recon import VisualReconService
from .services.scoring import ScoringService
from .services.export import ExportService
from .database import scan_collection

import asyncio

app = FastAPI(title="Red Team Recon API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for scan results (for quick access before DB persistence)
SCAN_RESULTS: Dict[str, dict] = {}

async def run_scan_task(scan_id: str, domain: str, twitter_handle: str = None):
    """
    Background task to run ALL recon services and update MongoDB.
    """
    print(f"Starting scan for {domain} (ID: {scan_id})")
    try:
        # Update Status to Running (In-Memory)
        if scan_id in SCAN_RESULTS:
            SCAN_RESULTS[scan_id]["status"] = "running"
        
        # Update DB (Best Effort)
        try:
             await scan_collection.update_one({"id": scan_id}, {"$set": {"status": "running"}})
        except: pass

        # 1. Subdomain Discovery
        print("Running Subdomain Discovery...")
        passive_subs = SubdomainService.get_subdomains_crtsh(domain)
        if not passive_subs:
            all_subs = [domain]
        else:
            all_subs = list(set(passive_subs))

        sub_result = SubdomainResult(subdomains=all_subs, count=len(all_subs))
        
        # 2. Port Scanning
        print("Running Port Scan...")
        import socket
        ports_list = []
        try:
            ip = socket.gethostbyname(domain)
            open_ports = PortScanService.scan_common_ports(ip)
            port_result = PortResult(ip=ip, ports=open_ports)
            ports_list = [port_result]
        except Exception as e:
            print(f"Port scan failed: {e}")

        # 3. OSINT - Tech Stack
        print("Running Tech Stack Detection...")
        try:
            tech_stack = OsintService.get_tech_stack(domain)
        except:
            tech_stack = []

        # 4. OSINT - Scraper (Emails, Phones, PDFs)
        print("Running OSINT Scraper...")
        try:
            osint_artifacts = await OsintService.run_osint_scraper(domain, twitter_handle)
        except Exception as e:
            print(f"OSINT Scraper failed: {e}")
            osint_artifacts = []

        # 5. Directory Fuzzing
        print("Running Directory Fuzzing...")
        try:
           directories = FuzzingService.brute_force_directories(domain)
        except:
            directories = []

        # 6. Visual Recon
        print("Running Visual Recon...")
        screenshots = {}
        try:
            targets_for_screen = [domain] + [s for s in all_subs if s != domain][:4]
            screenshots = await VisualReconService.take_screenshots(targets_for_screen)
        except Exception as e:
             print(f"Visual recon failed: {e}")

        # 7. Vuln Scan (Mock)
        vulns = []
        for tech in tech_stack:
            if "Apache" in tech:
                vulns.append("Apache: Check for Path Traversal (CVE-2021-41773)")
            if "PHP" in tech:
                 vulns.append("PHP: Check for Info Disclosure")
        
        # 7.5 Real Vuln Correlation from Ports
        for p_res in ports_list:
            if isinstance(p_res, PortResult): # It's a Pydantic model
                # PortResult.ports is a list of ANY (int or dict)
                for p_info in p_res.ports:
                     if isinstance(p_info, dict):
                         banner = p_info.get("banner", "")
                         if "Apache" in banner:
                             vulns.append(f"Apache Detected on port {p_info.get('port')}: Check CVEs for {banner}")

        # 8. Scoring
        scan_data_for_scoring = {
            "ports": [p.dict() for p in ports_list],
            "subdomains": sub_result.dict(),
            "osint_data": osint_artifacts,
            "technologies": tech_stack,
            "vulnerabilities": vulns
        }
        attack_score = ScoringService.calculate_score(scan_data_for_scoring)

        # Update Result in DB
        result_update = {
            "status": "completed",
            "subdomains": sub_result.dict(),
            "ports": [p.dict() for p in ports_list],
            "technologies": tech_stack,
            "osint_data": osint_artifacts,
            "directories": directories,
            "screenshots": screenshots,
            "vulnerabilities": vulns,
            "attack_score": attack_score
        }
        
        # Save to In-Memory
        if scan_id in SCAN_RESULTS:
            SCAN_RESULTS[scan_id].update(result_update)

        # Save to DB (Best Effort)
        try:
            await scan_collection.update_one(
                {"id": scan_id},
                {"$set": result_update}
            )
        except Exception as e:
            print(f"DB Final Update Failed: {e}")
            
        print(f"Scan {scan_id} completed.")

    except Exception as e:
        print(f"Scan failed: {e}")
        if scan_id in SCAN_RESULTS:
             SCAN_RESULTS[scan_id]["status"] = "failed"
        try:
            await scan_collection.update_one(
                {"id": scan_id},
                {"$set": {"status": "failed"}}
            )
        except: pass

@app.get("/")
def read_root():
    return {"message": "Recon API is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/scan", response_model=ScanResult)
async def start_scan(request: ScanRequest, background_tasks: BackgroundTasks):
    scan_id = str(uuid4())
    new_scan = ScanResult(
        id=scan_id,
        domain=request.domain,
        status="pending",
        timestamp=datetime.now()
    )
    
    # Save to In-Memory
    SCAN_RESULTS[scan_id] = new_scan.dict()

    # Save to MongoDB
    try:
        await scan_collection.insert_one(new_scan.dict())
    except Exception as e:
        print(f"DB Write Failed: {e}")
    
    background_tasks.add_task(run_scan_task, scan_id, request.domain, request.twitter_handle)
    return new_scan

@app.get("/api/scan/{scan_id}", response_model=ScanResult)
async def get_scan_result(scan_id: str):
    # Try DB first
    try:
        scan = await scan_collection.find_one({"id": scan_id})
        if scan:
            return ScanResult(**scan)
    except Exception as e:
        print(f"DB Read Failed: {e}. Checking in-memory.")
    
    # Fallback to in-memory
    if scan_id in SCAN_RESULTS:
        return ScanResult(**SCAN_RESULTS[scan_id])
        
    raise HTTPException(status_code=404, detail="Scan not found")

@app.get("/api/scans", response_model=List[ScanResult])
async def get_scan_history():
    try:
        cursor = scan_collection.find({}).sort("timestamp", -1)
        scans = []
        async for document in cursor:
            document.pop("_id", None) # Remove MongoDB's _id field
            scans.append(document)
        return [ScanResult(**scan) for scan in scans]
    except Exception as e:
        print(f"DB List Failed: {e}. Returning in-memory.")
        return [ScanResult(**scan) for scan in SCAN_RESULTS.values()]

from fastapi.responses import Response

@app.get("/api/scan/{scan_id}/export/spiderfoot")
async def export_spiderfoot(scan_id: str):
    # Fetch result
    scan_data = None
    try:
        scan = await scan_collection.find_one({"id": scan_id})
        if scan:
            scan_data = scan
    except: pass
    
    if not scan_data and scan_id in SCAN_RESULTS:
        scan_data = SCAN_RESULTS[scan_id]
        
    if not scan_data:
        raise HTTPException(status_code=404, detail="Scan not found")
        
    csv_content = ExportService.to_spiderfoot_csv(scan_data)
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=spiderfoot_export_{scan_id}.csv"}
    )
