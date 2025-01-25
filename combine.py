import json
import os

if __name__ == "__main__":
    output_dir = "output"
    output_file_path_all_calibers = (
        "all_calibers.json"  # Output in root folder (current directory)
    )
    combined_results = []

    for filename in os.listdir(output_dir):
        if filename.endswith(".output.json"):
            input_filepath = os.path.join(output_dir, filename)
            try:
                with open(input_filepath, "r") as infile:
                    json_data = json.load(infile)
                    if "results" in json_data and isinstance(
                        json_data["results"], list
                    ):
                        combined_results.extend(json_data["results"])
                    else:
                        print(
                            f"Warning: 'results' key not found or not a list in '{filename}'. Skipping file content."
                        )
            except json.JSONDecodeError:
                print(f"Error: Invalid JSON in '{filename}'. Skipping file.")
            except FileNotFoundError:
                print(
                    f"Error: Input file not found: '{input_filepath}'. Skipping file."
                )
            except Exception as e:
                print(
                    f"An error occurred while processing '{filename}': {e}. Skipping file."
                )

    # Prepare the final JSON structure
    all_calibers_data = {"results": combined_results}

    try:
        with open(output_file_path_all_calibers, "w") as outfile:
            json.dump(all_calibers_data, outfile, indent=4)
        print(
            f"Combined data saved to '{output_file_path_all_calibers}' in the root folder."
        )
    except Exception as e:
        print(f"Error saving combined data to '{output_file_path_all_calibers}': {e}")

    print("Combining process complete.")
