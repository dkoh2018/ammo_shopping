import requests
from pprint import pprint
from dotenv import load_dotenv
import os
import json
import re
from tqdm import tqdm
import time

load_dotenv()

USERNAME = os.environ.get("USERNAME")
PASSWORD = os.environ.get("PASSWORD")


def normalize_ammo_name(name):
    """Normalizes an ammunition name for use in a URL and filename."""
    name = name.lower()
    name = " ".join(name.split())  # Removes extra spacing
    return name


def create_ammoseek_url(ammo_name):
    """Creates the ammoseek url from a normalized name"""
    normalized_name = normalize_ammo_name(ammo_name)
    return f"https://ammoseek.com/ammo/{normalized_name}"


def scrape_ammunition_data(
    ammo_names, max_retries=3, base_delay=5, timeout_duration=30
):
    """
    Scrapes data from ammoseek, saves the data, and handles retries.

    Args:
        ammo_names (list): List of ammo names.
        max_retries (int): Maximum number of retry attempts.
        base_delay (int): Base delay (in seconds) before a retry.
        timeout_duration(int): timeout for the request call

    Returns:
        tuple: (int successfully scraped, int total attempted)
    """
    os.makedirs("data", exist_ok=True)

    successful_scrapes = 0
    total_attempts = 0

    for ammo_name in tqdm(ammo_names, desc="Scraping Progress"):
        total_attempts += 1
        url = create_ammoseek_url(ammo_name)
        payload = {
            "source": "universal",
            "render": "html",
            "url": url,
        }

        retries = 0
        while retries <= max_retries:
            try:
                response = requests.request(
                    "POST",
                    "https://realtime.oxylabs.io/v1/queries",
                    auth=(USERNAME, PASSWORD),
                    json=payload,
                    timeout=timeout_duration,  # timeout only for the request itself
                )

                response.raise_for_status()
                data = response.json()

                normalized_filename = normalize_ammo_name(ammo_name)
                filepath = os.path.join("data", f"{normalized_filename}.json")
                with open(filepath, "w") as f:
                    json.dump(data, f, indent=4)

                successful_scrapes += 1
                break  # Break out of the retry loop if successful
            except requests.exceptions.RequestException as e:
                print(
                    f"Error scraping {ammo_name} ({url}): {e} (Retry {retries+1}/{max_retries})"
                )
                if retries == max_retries:
                    break  # If we've run out of retries, don't bother retrying
                retries += 1
                time.sleep(base_delay * (2 ** (retries - 1)))  # exponential backoff

    return successful_scrapes, total_attempts


if __name__ == "__main__":
    try:
        with open("calibers.json", "r") as f:
            ammo_types = json.load(f)
    except FileNotFoundError:
        print("Error: calibers.json not found")
        exit()
    except json.JSONDecodeError:
        print("Error: Invalid calibers.json format")
        exit()

    successful_count, total_count = scrape_ammunition_data(ammo_types)

    print(f"\nScraping Complete.")
    print(f"Successfully scraped: {successful_count}/{total_count}")
