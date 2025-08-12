import tkinter as tk
from tkinter import filedialog, messagebox
import json
from pathlib import Path

def transform_json_file():
    """
    Prompts the user to select an input JSON file, transforms it by wrapping
    the main array in a 'rules' key, and saves it to a new file selected
    by the user.
    """
    # --- Step 1: Get the input file ---
    input_path_str = filedialog.askopenfilename(
        title="Select the INPUT JSON file",
        filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
    )
    # Exit if the user cancels
    if not input_path_str:
        messagebox.showinfo("Cancelled", "Operation cancelled. No input file was selected.")
        return
    
    input_path = Path(input_path_str)

    # --- Step 2: Get the output file location ---
    output_path_str = filedialog.asksaveasfilename(
        title="Select where to SAVE the TRANSFORMED file",
        defaultextension=".json",
        initialfile=f"{input_path.stem}_transformed.json",
        filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
    )
    # Exit if the user cancels
    if not output_path_str:
        messagebox.showinfo("Cancelled", "Operation cancelled. No output file location was selected.")
        return

    output_path = Path(output_path_str)

    # --- Step 3: Perform the transformation ---
    try:
        print(f"Reading from: {input_path}")
        original_content = input_path.read_text(encoding='utf-8')

        # Find the start and end of the JSON array.
        start_index = original_content.find('[')
        end_index = original_content.rfind(']')

        if start_index == -1 or end_index == -1:
            raise ValueError("Could not find a valid JSON array '[]' in the input file.")
        
        # Extract the array string and load it into a Python list
        json_array_str = original_content[start_index : end_index + 1]
        
        # Create the final Python dictionary
        transformed_data = {"rules": json.loads(json_array_str)}
        
        # Write the dictionary back to the chosen output JSON file
        print(f"Writing transformed data to: {output_path}")
        output_path.write_text(json.dumps(transformed_data, indent=2), encoding='utf-8')

        messagebox.showinfo("Success", f"Transformation complete!\n\nFile saved to:\n{output_path}")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during transformation:\n\n{e}")
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Create a simple root window to host the dialogs, then hide it.
    root = tk.Tk()
    root.withdraw()
    
    # Run the main function
    transform_json_file()
