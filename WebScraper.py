import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import os
from main import check_url_for_software_dev_company
import threading


# Main Application Class
class WebScraperTool:
    def __init__(self, root):
        self.root = root
        self.root.title("WebPage Extraction Tool")
        self.root.geometry("600x450")
        self.file_path = None
        self.csv_file_path = None
        self.results = []
        self.is_paused = False
        self.is_running = False
        self.scraping_thread = None

        # UI Setup
        self.create_widgets()

    # Function to create UI components
    def create_widgets(self):
        # Title
        title_label = tk.Label(self.root, text="WebPage Extraction Tool", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=10)

        # File Upload Section
        upload_frame = tk.Frame(self.root)
        upload_frame.pack(pady=10)

        self.upload_button = tk.Button(upload_frame, text="Upload XLSX File", command=self.upload_file)
        self.upload_button.grid(row=0, column=0, padx=5)

        self.file_label = tk.Label(upload_frame, text="No file selected")
        self.file_label.grid(row=0, column=1, padx=5)

        # Button Section
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        self.start_button = tk.Button(button_frame, text="Start", state="disabled", command=self.start_script)
        self.start_button.grid(row=0, column=0, padx=5)

        self.pause_button = tk.Button(button_frame, text="Pause", state="disabled", command=self.pause_script)
        self.pause_button.grid(row=0, column=1, padx=5)

        self.clear_button = tk.Button(button_frame, text="Clear", command=self.clear_ui)
        self.clear_button.grid(row=0, column=2, padx=5)

        self.download_button = tk.Button(button_frame, text="Download Excel", command=self.download_log)
        self.download_button.grid(row=0, column=3, padx=5)

        # Status Box
        status_label = tk.Label(self.root, text="Status Log:")
        status_label.pack()

        self.status_text = tk.Text(self.root, height=10, width=60, state="disabled")
        self.status_text.pack(padx=10)

        # Progress Bar
        self.progress = ttk.Progressbar(self.root, length=500, mode="determinate")
        self.progress.pack(pady=10)

    # Upload File Functionality
    def upload_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
        if file_path:
            self.file_path = file_path
            self.file_label.config(text=os.path.basename(file_path))
            self.convert_to_csv()
        else:
            messagebox.showerror("Error", "No file selected!")

    # Convert XLSX to CSV
    def convert_to_csv(self):
        try:
            self.log_status("Converting XLSX to CSV...")
            df = pd.read_excel(self.file_path)
            self.csv_file_path = self.file_path.replace(".xlsx", ".csv")
            df.to_csv(self.csv_file_path, index=False)
            self.log_status("File converted to CSV successfully!")
            self.start_button.config(state="normal")
            self.pause_button.config(state="normal")
        except Exception as e:
            messagebox.showerror("Conversion Error", f"Failed to convert file: {e}")
            self.log_status(f"Error: {e}")

    # Start Script Functionality
    def start_script(self):
        if not self.csv_file_path:
            messagebox.showerror("Error", "CSV file not found!")
            return

        if self.is_running:
            messagebox.showwarning("Warning", "Scraping is already in progress!")
            return

        self.is_running = True
        self.scraping_thread = threading.Thread(target=self.run_scraping, daemon=True)
        self.scraping_thread.start()

    def run_scraping(self):
        try:
            self.log_status("Starting scraping process...")
            df = pd.read_csv(self.csv_file_path)
            total_rows = len(df)

            for i, row in df.iterrows():
                while self.is_paused:
                    self.log_status("Paused... waiting to resume")
                    self.root.after(100)

                if not self.is_running:
                    break

                url = row.get("Website", None)
                if url:
                    result = check_url_for_software_dev_company(url)
                    result["website"] = url
                    self.results.append(result)
                    self.log_status(f"Scraping site: {url} - {result['website']}")
                else:
                    self.log_status("Empty URL found, skipping...")

                self.progress["value"] = (i + 1) / total_rows * 100
                self.root.update_idletasks()

            self.log_status("Scraping process completed!")
        except Exception as e:
            messagebox.showerror("Error", f"Error in script execution: {e}")
            self.log_status(f"Error: {e}")
        finally:
            self.is_running = False

    # Pause/Resume script functionality
    def pause_script(self):
        if not self.is_running:
            messagebox.showwarning("Warning", "No scraping process to pause!")
            return

        self.is_paused = not self.is_paused
        self.pause_button.config(text="Resume" if self.is_paused else "Pause")
        self.log_status("Scraping paused..." if self.is_paused else "Scraping resumed...")

    # Function to log messages in the status box
    def log_status(self, message):
        self.status_text.config(state="normal")
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.config(state="disabled")
        self.status_text.see(tk.END)

    # Clear UI Functionality
    def clear_ui(self):
        self.file_path = None
        self.csv_file_path = None
        self.file_label.config(text="No file selected")
        self.start_button.config(state="disabled")
        self.pause_button.config(state="disabled", text="Pause")
        self.progress["value"] = 0
        self.status_text.config(state="normal")
        self.status_text.delete(1.0, tk.END)
        self.status_text.config(state="disabled")
        self.log_status("Cleared previous data!")
        self.results = []
        self.is_running = False
        self.is_paused = False

    # Download Log Functionality
    def download_log(self):
        if not self.results:
            messagebox.showwarning("Warning", "No log data to download!")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
        if file_path:
            try:
                df = pd.DataFrame(self.results)
                df.to_excel(file_path, index=False)
                messagebox.showinfo("Success", "Log file downloaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to download file: {e}")


# Run the Application
if __name__ == "__main__":
    root = tk.Tk()
    app = WebScraperTool(root)
    root.mainloop()
