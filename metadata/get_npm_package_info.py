import requests
import time
import csv

INPUT_FILE = "npm_packages.txt"
OUTPUT_FILE = "npm_metadata.csv"

SEARCH_API = "https://registry.npmjs.org/-/v1/search?text={pkg}&size=1"

HEADERS = {
    "User-Agent": "npm-metadata-fetcher/1.0"
}

def fetch_npm_package_info(pkg_name):
    try:
        url = SEARCH_API.format(pkg=pkg_name)
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if data["objects"]:
            pkg = data["objects"][0]["package"]
            name = pkg.get("name", pkg_name)
            description = pkg.get("description", "No description provided")
            publisher = pkg.get("publisher", {}).get("username", "Unknown")
        else:
            name = pkg_name
            description = "Package not found"
            publisher = "N/A"

        return name, publisher, description

    except Exception as e:
        return pkg_name, "Error", f"Error: {str(e)}"

def main():
    with open(INPUT_FILE, "r") as f:
        packages = [line.strip() for line in f if line.strip()]

    with open(OUTPUT_FILE, "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["package_name", "publisher", "description"])

        for pkg in packages:
            name, publisher, description = fetch_npm_package_info(pkg)
            print(f"{name} → {publisher}")
            writer.writerow([name, publisher, description])
            time.sleep(1)  # polite delay

if __name__ == "__main__":
    main()
