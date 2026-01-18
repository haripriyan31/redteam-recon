from typing import Dict, List, Any
import csv
import io

class ExportService:
    @staticmethod
    def to_spiderfoot_csv(scan_data: Dict[str, Any]) -> str:
        """
        Converts scan data to SpiderFoot compatible CSV format.
        Format: type,data,source,source_id (optional)
        SpiderFoot expects: type,data
        Example:
        Internet Name,example.com
        Email Address,admin@example.com
        """
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Headers (SpiderFoot often auto-detects, but let's stick to simple type,data)
        # writer.writerow(['type', 'data']) 
        
        domain = scan_data.get("domain", "")
        if domain:
             writer.writerow(['Internet Name', domain])
             
        # Subdomains
        subdomains = scan_data.get("subdomains", {}).get("subdomains", [])
        for sub in subdomains:
            writer.writerow(['Internet Name', sub])
            
        # Ports/IPs
        ports_data = scan_data.get("ports", [])
        for p_res in ports_data:
            ip = p_res.get("ip")
            if ip:
                writer.writerow(['IP Address', ip])
            
            # Open Ports (SpiderFoot doesn't digest ports easily in CSV import without custom modules, 
            # but we can list them as potentially unrelated data or just skip)
            
        # Emails
        osint = scan_data.get("osint_data", [])
        for item in osint:
            if item.get("type") == "email":
                writer.writerow(['Email Address', item.get("value")])
            elif item.get("type") == "phone":
                 writer.writerow(['Phone Number', item.get("value")])

        return output.getvalue()
