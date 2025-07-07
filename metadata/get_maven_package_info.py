import requests
import xml.etree.ElementTree as ET
import csv
import time
import random

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; Python script)",
    "Accept": "application/xml",
}

def get_latest_version(group_id, artifact_id):
    query = f'https://search.maven.org/solrsearch/select?q=g:"{group_id}"+AND+a:"{artifact_id}"&rows=1&wt=json'
    for attempt in range(3):
        try:
            resp = requests.get(query, headers=HEADERS)
            #resp = requests.get(query)
            resp.raise_for_status()
            docs = resp.json().get('response', {}).get('docs', [])
            if docs:
                return docs[0]['latestVersion']
            break # success
        except requests.RequestException:
            wait = 2 ** attempt + random.random()
            print(f"Retrying in {wait:.2f} seconds...")
            time.sleep(wait)
        #except Exception as e:
        #    print(f"Error getting version for {group_id}:{artifact_id} - {e}")
    else:
        return "Error: Could not fetch POM after retries"
    #return None

def parse_pom(pom_url):
    for attempt in range(3):
        try:
            resp = requests.get(pom_url, headers=HEADERS)
            #resp = requests.get(pom_url)
            resp.raise_for_status()
            root = ET.fromstring(resp.text)
            ns = {'m': 'http://maven.apache.org/POM/4.0.0'}

            desc = root.findtext('m:description', default='No description', namespaces=ns)

            org_name = root.findtext('m:organization/m:name', default='', namespaces=ns)
            if not org_name:
                dev = root.find('m:developers/m:developer/m:name', namespaces=ns)
                org_name = dev.text if dev is not None else "Unknown"

            return org_name.strip(), desc.strip()
        except requests.RequestException:
            wait = 2 ** attempt + random.random()
            print(f"Retrying in {wait:.2f} seconds...")
            time.sleep(wait)
        # except Exception as e:
        #     return "Error", f"Could not parse POM: {e}"
    else:
        return "Error: Could not fetch POM after retries"


def main(input_file, output_csv):
    with open(input_file) as f:
        packages = [line.strip() for line in f if ":" in line.strip()]

    with open(output_csv, "w", newline='', encoding='utf-8') as out:
        writer = csv.writer(out)
        writer.writerow(["package_name", "publisher", "description"])

        for pkg in packages:
            group_id, artifact_id = pkg.split(":")
            latest_version = get_latest_version(group_id, artifact_id)
            if not latest_version:
                writer.writerow([pkg, "Not found", "No latest version found"])
                continue

            pom_url = f"https://repo1.maven.org/maven2/{group_id.replace('.', '/')}/{artifact_id}/{latest_version}/{artifact_id}-{latest_version}.pom"
            publisher, description = parse_pom(pom_url)
            writer.writerow([pkg, publisher, description])
            time.sleep(0.2)

    print(f"Done. Output in {output_csv}")

if __name__ == "__main__":
    main("maven_packages.txt", "maven_metadata.csv")
