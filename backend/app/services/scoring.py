from typing import Dict, List, Any

class ScoringService:
    @staticmethod
    def calculate_score(scan_data: Dict[str, Any]) -> int:
        """
        Calculates an Attack Surface Risk Score (0-100+) based on findings.
        """
        score = 0
        
        # 1. Open Ports
        ports = scan_data.get("ports", [])
        if ports:
            # ports is a list of PortResult objects (dicts)
            # We need to flatten it or iterate correctly. 
            # In main.py, ports is [PortResult(ip=..., ports=[80, 443])].
            # Let's assume the passed data structure matches the final DB schema or dict.
            for p_result in ports:
                # If it's a dict from DB/Schema
                open_ports = p_result.get("ports", [])
                if isinstance(open_ports, list):
                     for port_info in open_ports:
                        # Handle both int (old) and dict (new)
                        port_num = port_info if isinstance(port_info, int) else port_info.get("port")
                        
                        score += 5 # Base score for any open port
                        
                        # Critical Ports
                        if port_num in [21, 22, 23, 3389, 445, 1433, 3306, 27017]:
                             score += 10
        
        # 2. Subdomains
        subdomains = scan_data.get("subdomains", {}).get("subdomains", [])
        score += len(subdomains) * 2
        
        # 3. OSINT - Emails/Phones
        osint = scan_data.get("osint_data", [])
        for item in osint:
            if item.get("type") == "email":
                score += 5
            if item.get("type") == "phone":
                score += 3
                
        # 4. Technologies (Wappalyzer/Headers)
        techs = scan_data.get("technologies", [])
        score += len(techs) * 2
        
        # 5. Vulnerabilities (Mock/Real)
        vulns = scan_data.get("vulnerabilities", [])
        score += len(vulns) * 20
        
        return min(score, 100) # Cap at 100? Or let it go higher for "Critical"? Let's cap for UI.
