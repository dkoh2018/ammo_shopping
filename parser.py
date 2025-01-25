import json
from bs4 import BeautifulSoup
import os
import re
import uuid
from pathlib import Path


# ID Management System
class IDManager:
    def __init__(self, id_file="id_tracker.json"):
        self.id_file = id_file
        self.existing_ids = set()
        self.load_existing_ids()

    def load_existing_ids(self):
        if Path(self.id_file).exists():
            with open(self.id_file, "r") as f:
                self.existing_ids = set(json.load(f).get("ids", []))
        else:
            self.existing_ids = set()

    def save_ids(self):
        with open(self.id_file, "w") as f:
            json.dump({"ids": list(self.existing_ids)}, f)

    def generate_unique_id(self):
        while True:
            new_id = str(uuid.uuid4().int)[:8]  # Generate 8-digit numeric ID
            if new_id not in self.existing_ids:
                self.existing_ids.add(new_id)
                self.save_ids()
                return new_id


# Initialize ID manager
id_manager = IDManager()


def parse_ammoseek_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    results_data = []
    result_cards = soup.find_all("div", class_="results-card")

    for card in result_cards:
        item_data = {}
        try:
            # Generate unique ID for this item
            item_data["id"] = id_manager.generate_unique_id()

            # --- Retailer (Corrected) ---
            retailer_element = card.find("li", class_="retailer-name")
            item_data["Retailer"] = (
                retailer_element.text.strip() if retailer_element else "N/A"
            )

            # --- Description (Improved cleaning) ---
            description_element = card.find("section", class_="ga-desc")
            item_data["Description"] = (
                description_element.get_text(strip=True)
                if description_element
                else "N/A"
            )

            # --- Brand ---
            brand_element = card.find("li", class_="mfg")
            if brand_element:
                brand_text = brand_element.get_text(strip=True).replace("Brand", "")
                item_data["Brand"] = brand_text.split(maxsplit=1)[-1]
            else:
                item_data["Brand"] = "N/A"

            # --- Caliber ---
            caliber_element = card.find("li", class_="caliber")
            if caliber_element:
                caliber_text = caliber_element.get_text(strip=True).replace("Cal", "")
                item_data["Caliber"] = caliber_text.split(maxsplit=1)[-1]
            else:
                item_data["Caliber"] = "N/A"

            # --- Grains (More robust parsing) ---
            grains_element = card.find("li", class_="gr")
            item_data["Grains"] = None
            if grains_element:
                grains_text = grains_element.get_text(strip=True).replace("gr", "")
                item_data["Grains"] = (
                    int(grains_text) if grains_text.isdigit() else None
                )

            # --- Price (Improved range handling) ---
            price_element = card.find("span", class_="ga-totalprice")
            item_data["Price"] = None
            if price_element:
                price_text = price_element.get_text(strip=True, separator=" ")
                price_value_str = (
                    price_text.split()[0].replace("$", "").replace(",", "")
                )
                try:
                    item_data["Price"] = (
                        float(price_value_str) if price_value_str else None
                    )
                except ValueError:
                    pass

            # --- Rounds ---
            rounds_element = card.find("li", class_="count")
            item_data["Rounds"] = None
            if rounds_element:
                rounds_text = rounds_element.get_text(strip=True).replace("ct", "")
                item_data["Rounds"] = (
                    int(rounds_text) if rounds_text.isdigit() else None
                )

            # --- Casing ---
            casing_element = card.find("li", class_="casing")
            item_data["Casing"] = "N/A"
            if casing_element:
                if casing_element.find("span", class_="as-brass-badge"):
                    item_data["Casing"] = "brass"
                elif casing_element.find("span", class_="as-casing-badge"):
                    item_data["Casing"] = "steel"

            # --- S/H (Corrected navigation) ---
            shipping_element = card.find("li", class_="ga-shipping")
            item_data["S/H"] = "N/A"
            if shipping_element:
                score_span = shipping_element.find("span", class_="displayScore")
                if score_span:
                    item_data["S/H"] = score_span.get_text(strip=True)

            # --- Limits ---
            limit_element = card.find("div", class_="p-limit")
            item_data["Limits"] = (
                limit_element.text.replace("Limit:", "").strip()
                if limit_element
                else "N/A"
            )

            # --- New? (Condition) ---
            condition_element = card.find("li", class_="condition")
            item_data["New?"] = "N/A"
            if condition_element:
                status = condition_element.find(
                    "span", class_=lambda x: x in ["remanufactured", "new"]
                )
                item_data["New?"] = status["class"][0] if status else "N/A"

            # --- $/round (Corrected parsing with 3 decimal rounding) ---
            cpr_element = card.find("span", class_="ga-cpr")
            item_data["$/round"] = None
            if cpr_element:
                cpr_text = cpr_element.get_text(strip=True)
                if cpr_text.startswith("$"):
                    cpr_value = re.search(r"[\d.]+", cpr_text)
                    if cpr_value:
                        try:
                            item_data["$/round"] = round(float(cpr_value.group()), 3)
                        except ValueError:
                            pass
                else:
                    cpr_value = re.search(r"[\d.]+", cpr_text)
                    if cpr_value:
                        try:
                            item_data["$/round"] = round(
                                float(cpr_value.group()) / 100, 3
                            )
                        except ValueError:
                            pass

            # --- Link (renamed from Share) ---
            share_link = card.find("a", class_="sharethis-link")
            item_data["Link"] = share_link["href"] if share_link else "N/A"

            results_data.append(item_data)

        except Exception as e:
            print(f"Error processing card: {str(e)}")
            continue

    return {"results": results_data}


if __name__ == "__main__":
    data_dir = "data"
    output_dir = "output"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(data_dir):
        if filename.endswith(".json"):
            input_filepath = os.path.join(data_dir, filename)
            output_filename = filename.replace(".json", ".output.json")
            output_filepath = os.path.join(output_dir, output_filename)

            print(f"Processing file: {filename}")

            try:
                with open(input_filepath, "r") as infile:
                    json_data = json.load(infile)
                    html_content = json_data["results"][0]["content"]
                    parsed_data = parse_ammoseek_html(html_content)

                with open(output_filepath, "w") as outfile:
                    json.dump(parsed_data, outfile, indent=4)
                print(f"Parsed data from '{filename}' and saved to '{output_filename}'")

            except json.JSONDecodeError:
                print(f"Error: Invalid JSON in '{filename}'")
            except KeyError as e:
                print(f"Error: KeyError: {e} in '{filename}'")
            except FileNotFoundError:
                print(f"Error: Input file not found: '{input_filepath}'")
            except Exception as e:
                print(f"An error occurred while processing '{filename}': {e}")

    print("Parsing process complete.")
