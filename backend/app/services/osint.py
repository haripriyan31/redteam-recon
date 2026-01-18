import requests
import re
import json
import subprocess
from bs4 import BeautifulSoup
from typing import List, Dict, Any

# Refined Regex - "More Straight" as requested
EMAIL_REGEX = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
PHONE_REGEX = r"\b(?:\+?\d{1,3}[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b"
PDF_LINK_REGEX = r"\bhttps?://[^\s/]+\/[^\s]+\.pdf\b"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (RedTeam-OSINT/1.0)"
}

class OsintService:
    @staticmethod
    def normalize(v: str, t: str, s: str, c: float = 0.6) -> Dict[str, Any]:
        return {
            "value": v,
            "type": t,
            "source": s,
            "confidence": c
        }

    @staticmethod
    def get_tech_stack(domain: str) -> List[str]:
        """
        Detects technologies using HTTP headers and HTML content.
        """
        technologies = set()
        url = f"http://{domain}"
        try:
            response = requests.get(url, timeout=5, verify=False, headers=HEADERS)
            headers = response.headers
            
            if 'Server' in headers:
                technologies.add(f"Server: {headers['Server']}")
            if 'X-Powered-By' in headers:
                technologies.add(f"Powered By: {headers['X-Powered-By']}")
            
            content = response.text.lower()
            if 'wp-content' in content:
                technologies.add("WordPress")
            if 'react' in content:
                technologies.add("React (Frontend)")
            if 'cf-ray' in headers:
                technologies.add("WAF: Cloudflare")

            return list(technologies)
        except:
            return []

    @staticmethod
    async def run_osint_scraper(domain: str, twitter_handle: str = None) -> List[Dict[str, Any]]:
        """
        Main runner for the OSINT scraper logic.
        """
        results = []
        
        # 1. Scraping Website (Emails/Phones)
        try:
            r = requests.get(f"https://{domain}", headers=HEADERS, timeout=10, verify=False)
            text = r.text
            
            # Emails
            for e in set(re.findall(EMAIL_REGEX, text)):
                results.append(OsintService.normalize(e, "email", "website", 0.9))
            
            # Phones
            for p in set(re.findall(PHONE_REGEX, text)):
                results.append(OsintService.normalize(p.strip(), "phone", "website", 0.7))
                
            # PDFs
            soup = BeautifulSoup(text, "lxml")
            for link in soup.find_all("a", href=True):
                href = link["href"]
                if href.lower().endswith(".pdf"):
                    if not href.startswith("http"):
                        href = f"https://{domain}/{href.lstrip('/')}"
                    results.append(OsintService.normalize(href, "pdf", "website", 0.8))
                
                # mailto/tel
                if href.startswith("mailto:"):
                    results.append(OsintService.normalize(href.replace("mailto:", ""), "email", "website", 0.95))
                if href.startswith("tel:"):
                    results.append(OsintService.normalize(href.replace("tel:", ""), "phone", "website", 0.85))
        except Exception as e:
            print(f"Website OSINT error: {e}")

        # 2. CRT.SH
        try:
            u = f"https://crt.sh/?q=%25.{domain}&output=json"
            r = requests.get(u, timeout=15)
            if r.status_code == 200:
                for c in r.json():
                    n = c.get("name_value", "")
                    for e in re.findall(EMAIL_REGEX, n):
                        results.append(OsintService.normalize(e, "email", "crt.sh", 0.75))
        except: pass

        # 3. Reddit
        try:
            u = f"https://www.reddit.com/search.json?q={domain}"
            r = requests.get(u, headers=HEADERS, timeout=10)
            if r.status_code == 200:
                d = r.json()
                for p in d.get("data", {}).get("children", []):
                    t = p["data"].get("title", "")
                    for e in re.findall(EMAIL_REGEX, t):
                        results.append(OsintService.normalize(e, "email", "reddit", 0.5))
        except: pass

        # 4. Nitter (Twitter)
        if twitter_handle:
            try:
                r = requests.get(f"https://nitter.net/{twitter_handle}", headers=HEADERS, timeout=10)
                if r.status_code == 200:
                    s = BeautifulSoup(r.text, "lxml")
                    tweets = s.find_all("div", class_="tweet-content")
                    for x in tweets[:5]:
                        for e in re.findall(EMAIL_REGEX, x.text):
                            results.append(OsintService.normalize(e, "email", "twitter", 0.6))
                        for p in re.findall(PHONE_REGEX, x.text):
                            results.append(OsintService.normalize(p.strip(), "phone", "twitter", 0.6))
            except: pass

        # Deduplicate
        unique_results = {json.dumps(i, sort_keys=True): i for i in results}
        return list(unique_results.values())

    @staticmethod
    def check_s3_buckets(domain: str) -> List[Dict[str, Any]]:
        """
        Checks for open S3 buckets based on domain permutations.
        """
        results = []
        base_name = domain.split('.')[0]
        permutations = [
            base_name,
            f"www.{base_name}",
            f"{base_name}-backup",
            f"{base_name}-dev",
            f"{base_name}-assets",
            f"{base_name}-public",
            domain.replace('.', '-')
        ]
        
        print(f"Checking {len(permutations)} potential S3 buckets...")
        
        for p in permutations:
            bucket_url = f"http://{p}.s3.amazonaws.com"
            try:
                # verify=False to avoid SSL errors on non-existent buckets sometimes
                r = requests.get(bucket_url, timeout=3, verify=False)
                if r.status_code == 200 and "ListBucketResult" in r.text:
                    results.append(OsintService.normalize(bucket_url, "s3_bucket", "bruteforce", 1.0))
                elif r.status_code == 403:
                     # Exists but private
                     results.append(OsintService.normalize(bucket_url, "s3_bucket", "bruteforce", 0.8)) # Found but locked
            except:
                pass
                
        return results
