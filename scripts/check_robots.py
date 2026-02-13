import requests
import csv
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

def get_robots_url(domain):
    if not domain.startswith('http'):
        domain = 'https://' + domain
    return domain.rstrip('/') + '/robots.txt'

def check_domain(domain):
    robots_url = get_robots_url(domain)
    rp = RobotFileParser()
    try:
        rp.set_url(robots_url)
        rp.read()
        
        can_fetch = rp.can_fetch("*", "/")
        return {
            'Domain': domain,
            'Robots_URL': robots_url,
            'Status': 'Allowed' if can_fetch else 'Disallowed',
            'Notes': 'Standard check'
        }
    except Exception as e:
        return {
            'Domain': domain,
            'Robots_URL': robots_url,
            'Status': 'Error',
            'Notes': str(e)
        }

def main():
    domains = []
    with open('domains.txt', 'r') as f:
        domains = [line.strip() for line in f if line.strip()]

    results = []
    print(f"Checking {len(domains)} domains...")
    
    for domain in domains:
        print(f"Checking {domain}...")
        result = check_domain(domain)
        results.append(result)

    with open('domain_compliance.csv', 'w', newline='') as f:
        fieldnames = ['Domain', 'Robots_URL', 'Status', 'Notes']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print("Done. Results saved to domain_compliance.csv")

if __name__ == '__main__':
    main()
