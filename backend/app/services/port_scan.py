import socket
import shodan
import nmap
from typing import List, Dict

class PortScanService:
    
    COMMON_PORTS = [
        21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 
        465, 587, 993, 995, 1433, 3306, 3389, 5432, 5900, 6379, 
        8000, 8080, 8443, 27017
    ]

    @staticmethod
    def scan_common_ports(ip: str) -> List[int]:
        """
        Attempts to use Nmap first. If not found/fails, falls back to socket scan.
        """
        try:
            return PortScanService.scan_nmap(ip)
        except Exception as e:
            print(f"Nmap failed ({e}), falling back to socket scan...")
            
        # Fallback Socket Scan
        open_ports = []
        socket.setdefaulttimeout(0.5)
        
        for port in PortScanService.COMMON_PORTS:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = s.connect_ex((ip, port))
                if result == 0:
                    open_ports.append(port)
                s.close()
            except Exception:
                pass
                
        return open_ports

    @staticmethod
    def scan_nmap(ip: str) -> List[Dict]:
        """
        Scan using Nmap binary with service version detection (-sV).
        Returns a list of dicts: {'port': int, 'service': str, 'version': str}
        """
        nm = nmap.PortScanner()
        # -sV: Probe open ports to determine service/version info
        # -T4: Aggressive timing template
        # --open: Only show open ports
        ports_str = ",".join(map(str, PortScanService.COMMON_PORTS))
        try:
            nm.scan(ip, ports_str, arguments='-sV -T4 --open')
        except Exception as e:
            print(f"Nmap scan error: {e}")
            return []
        
        results = []
        if ip in nm.all_hosts():
            for proto in nm[ip].all_protocols():
                lport = nm[ip][proto].keys()
                for port in lport:
                    if nm[ip][proto][port]['state'] == 'open':
                        service_name = nm[ip][proto][port].get('product', '')
                        version = nm[ip][proto][port].get('version', '')
                        full_version = f"{service_name} {version}".strip()
                        
                        results.append({
                            "port": port,
                            "service": nm[ip][proto][port]['name'],
                            "version": full_version,
                            "banner": full_version # Using version as banner for now
                        })
        
        return results

    @staticmethod
    def get_shodan_info(ip: str, api_key: str) -> Dict:
        """
        Fetch open ports and banner info from Shodan.
        """
        if not api_key:
            return {}
            
        api = shodan.Shodan(api_key)
        try:
            full_info = api.host(ip)
            return {
                "ports": full_info.get('ports', []),
                "os": full_info.get('os', None),
                "hostnames": full_info.get('hostnames', []),
                "vulns": list(full_info.get('vulns', []))
            }
        except shodan.APIError as e:
            print(f"Shodan API Error: {e}")
            return {}
