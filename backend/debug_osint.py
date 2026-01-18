import asyncio
import sys
import os

# Add the parent directory to sys.path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.osint import OsintService

async def test_scraper():
    domain = "google.com" # Test target
    print(f"Testing scraper on {domain}...")
    try:
        results = await OsintService.run_osint_scraper(domain)
        print(f"Scraper finished. Found {len(results)} items.")
        for item in results:
            print(f"- [{item['type']}] {item['value']} (Source: {item['source']})")
    except Exception as e:
        print(f"Scraper failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_scraper())
