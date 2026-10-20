import requests
import sys
import argparse
import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

REQUEST_HEADERS = {
    "User-Agent": "WebEnumeration/1.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def enumerate_directories(url, wordlist_path):
    try:
        with open(wordlist_path, 'r') as wordlist:
            directories = wordlist.read().splitlines()
    except FileNotFoundError:
        print(f"Error: Wordlist file '{wordlist_path}' not found.")
        return

    print(f" Scanning for directories on {url}...\n")

    for dir_name in directories:
        cleaned_dir_name = url.rstrip('/')
        target_url = f"{cleaned_dir_name}/{dir_name.lstrip('/')}"

        try:
            response = requests.get(
                target_url,
                headers=REQUEST_HEADERS,
                timeout=5,
                allow_redirects=False,
                verify=False,
            )
            if 300 <= response.status_code < 400:
                continue

            if response.status_code == 200:
                print(f"[+] Found: {target_url} (Status Code: {response.status_code})")
            elif response.status_code == 403:
                print(f"[!] Forbidden: {target_url} (Status Code: {response.status_code})")
            elif response.status_code == 404:
                continue
            else:
                print(f"[?] Response: {target_url} (Status Code: {response.status_code})")
        except requests.RequestException as error:
            print(f"[!] Request failed: {target_url} ({error})")

def enumerate_subdomains(domain, wordlist_path):
    try:
        with open(wordlist_path, 'r') as wordlist:
            subdomains = wordlist.read().splitlines()
    except FileNotFoundError:
        print(f"Error: Wordlist file '{wordlist_path}' not found.")
        return
    
    print(f" Scanning for subdomains on {domain}...\n")

    for sub in subdomains:
        target_subdomain = f"{sub}.{domain}"
        try:
            response = requests.get(
                f"http://{target_subdomain}",
                headers=REQUEST_HEADERS,
                timeout=5,
                allow_redirects=False,
                verify=False,
            )
            if 300 <= response.status_code < 400:
                continue

            if response.status_code == 200:
                print(f"[+] Found: {target_subdomain} (Status Code: {response.status_code})")
            elif response.status_code == 403:
                print(f"[!] Forbidden: {target_subdomain} (Status Code: {response.status_code})")
            elif response.status_code == 404:
                continue
            else:
                print(f"[?] Response: {target_subdomain} (Status Code: {response.status_code})")
        except requests.RequestException as error:
            print(f"[!] Request failed: {target_subdomain} ({error})")
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Directory and Subdomain Enumeration Tool")
    parser.add_argument("-u", "--url", help="Target URL to scan for directories")
    parser.add_argument("-d", "--domain", help="Target domain to scan for subdomains")
    parser.add_argument("-w", "--wordlist", required=True, help="Path to the wordlist file")
    args = parser.parse_args()

    if args.url:
        enumerate_directories(args.url, args.wordlist)
    elif args.domain:
        enumerate_subdomains(args.domain, args.wordlist)
    else:
        print("Error: Please provide either a URL (-u) or a domain (-d) to scan.")
        sys.exit(1)
