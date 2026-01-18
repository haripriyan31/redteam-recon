from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Union, Any
from datetime import datetime

class ScanRequest(BaseModel):
    domain: str
    twitter_handle: Optional[str] = None # Added for OSINT scraper
    scan_types: List[str] = ["subdomains", "ports", "osint"]  # default to all

class OSINTArtifact(BaseModel):
    value: str
    type: str
    source: str
    confidence: float

class SubdomainResult(BaseModel):
    subdomains: List[str]
    count: int

class PortResult(BaseModel):
    ip: str
    ports: List[Union[int, Dict[str, Any]]]
    banners: Optional[Dict[str, str]] = None

class ScanResult(BaseModel):
    id: str
    domain: str
    status: str = "pending"
    timestamp: datetime
    subdomains: Optional[SubdomainResult] = None
    ports: Optional[List[PortResult]] = None
    technologies: Optional[List[str]] = None
    osint_data: Optional[List[OSINTArtifact]] = None # New field
    directories: Optional[List[str]] = None
    screenshots: Optional[Dict[str, str]] = None # subdomain -> b64
    vulnerabilities: Optional[List[str]] = None
    attack_score: int = 0

