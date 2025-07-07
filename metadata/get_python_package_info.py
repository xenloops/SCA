import requests
import time
import csv

INPUT_FILE = "python_packages.txt"
OUTPUT_FILE = "python_metadata.csv"

PYPI_API = "https://pypi.org/pypi/{}/json"

HEADERS = {
    "User-Agent": "pypi-metadata-fetcher/1.0"
}

def fetch_pypi_package_info(pkg_name):
    try:
        url = PYPI_API.format(pkg_name)
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        info = data.get("info", {})
        name = info.get("name", pkg_name)
        description = info.get("summary", "No description provided").strip()
        publisher = info.get("maintainer") or info.get("author") or "Unknown"

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
            name, publisher, description = fetch_pypi_package_info(pkg)
            print(f"{name} → {publisher}")
            writer.writerow([name, publisher, description])
            time.sleep(1)  # polite delay to avoid rate limits

if __name__ == "__main__":
    main()
