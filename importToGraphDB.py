import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import requests
from pathlib import Path

# --- Configuration ---
# Adjust these values if necessary.
REPO_ID = "AbdelBachelor2025"
GRAPHDB_URL = f"http://localhost:7200/repositories/{REPO_ID}"

class GraphDBManager:
    """
    A simple GUI to import a Turtle file to GraphDB and clear the repository.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("GraphDB Importer & Manager")
        self.selected_ttl_path = None

        # --- GUI Setup ---
        
        # Frame for file selection and actions
        control_frame = tk.LabelFrame(root, text="Controls", padx=10, pady=10)
        control_frame.pack(padx=10, pady=10, fill="x")

        # File selection
        select_button = tk.Button(control_frame, text="1. Select 'output.ttl' File", command=self.select_file)
        select_button.pack(fill="x", pady=2)

        self.file_label = tk.Label(control_frame, text="No file selected", bg="lightgrey", anchor="w")
        self.file_label.pack(fill="x", pady=2)

        # Action buttons
        self.import_button = tk.Button(control_frame, text="2. Import File to GraphDB", command=self.import_ttl, state=tk.DISABLED)
        self.import_button.pack(fill="x", pady=5)

        clear_button = tk.Button(root, text="Clear Entire GraphDB Repository", bg="#ffcccc", command=self.clear_repository)
        clear_button.pack(padx=10, pady=5, fill="x")

        # Log area
        self.log_text = scrolledtext.ScrolledText(root, width=80, height=15)
        self.log_text.pack(padx=10, pady=(0, 10), expand=True, fill="both")

    def log(self, message):
        """Writes a message to the log area."""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def select_file(self):
        """Opens a file dialog to select the .ttl file."""
        filepath = filedialog.askopenfilename(
            title="Select the output.ttl file",
            filetypes=(("Turtle files", "*.ttl"), ("All files", "*.*"))
        )
        if filepath:
            self.selected_ttl_path = Path(filepath)
            self.file_label.config(text=f"Selected: {self.selected_ttl_path.name}")
            self.import_button.config(state=tk.NORMAL)
            self.log(f"✅ File selected: {self.selected_ttl_path}")
        else:
            self.log("... File selection cancelled.")

    def import_ttl(self):
        """Imports the selected .ttl file to GraphDB."""
        if not self.selected_ttl_path:
            messagebox.showerror("Error", "No file selected to import.")
            return

        self.log(f"\n🔄 Attempting to import '{self.selected_ttl_path.name}'...")
        try:
            headers = {'Content-Type': 'application/x-turtle'}
            with open(self.selected_ttl_path, 'rb') as f:
                response = requests.post(f"{GRAPHDB_URL}/statements", data=f, headers=headers)
            
            # Raise an error for bad status codes (4xx or 5xx)
            response.raise_for_status()
            
            self.log("✅ Success! Data imported into GraphDB.")
            messagebox.showinfo("Success", "File successfully imported into GraphDB.")

        except requests.exceptions.RequestException as e:
            error_message = f"❌ Error importing to GraphDB: {e}"
            self.log(error_message)
            if e.response is not None:
                self.log(f"    Response from server: {e.response.text}")
            messagebox.showerror("GraphDB Import Error", f"Failed to import data. Check logs for details.\n\n{e}")
        except Exception as e:
            self.log(f"❌ An unexpected error occurred: {e}")
            messagebox.showerror("Error", str(e))

    def clear_repository(self):
        """Sends a request to delete all statements in the repository."""
        if not messagebox.askyesno("Confirm Action", f"Are you sure you want to delete ALL data from the repository '{REPO_ID}'?"):
            self.log("\n... Clear repository operation cancelled by user.")
            return
            
        self.log(f"\n🗑️ Clearing all statements from repository '{REPO_ID}'...")
        try:
            response = requests.delete(f"{GRAPHDB_URL}/statements")
            response.raise_for_status()
            self.log("✅ Success! Repository has been cleared.")
            messagebox.showinfo("Success", "The repository has been cleared.")
        except requests.exceptions.RequestException as e:
            error_message = f"❌ Error clearing repository: {e}"
            self.log(error_message)
            if e.response is not None:
                self.log(f"    Response from server: {e.response.text}")
            messagebox.showerror("Clearing Error", f"Could not clear the repository. Check logs for details.\n\n{e}")
        except Exception as e:
            self.log(f"❌ An unexpected error occurred: {e}")
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = GraphDBManager(root)
    root.mainloop()
