import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import subprocess
import os
import threading

class BDATApp:
    def __init__(self, master):
        self.master = master
        master.title("BDAT Conversion Toolset")

        # Extract Section
        self.extract_frame = ttk.LabelFrame(master, text="Extract BDAT to JSON")
        self.extract_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.extract_label = ttk.Label(self.extract_frame, text="Path to directory containing BDAT files:")
        self.extract_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.extract_path = tk.StringVar()
        self.extract_entry = ttk.Entry(self.extract_frame, textvariable=self.extract_path, width=50)
        self.extract_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.extract_button = ttk.Button(self.extract_frame, text="Browse", command=self.browse_extract_input)
        self.extract_button.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        self.extract_output_label = ttk.Label(self.extract_frame, text="Path to output directory:")
        self.extract_output_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.extract_output_path = tk.StringVar()
        self.extract_output_entry = ttk.Entry(self.extract_frame, textvariable=self.extract_output_path, width=50)
        self.extract_output_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.extract_output_button = ttk.Button(self.extract_frame, text="Browse", command=self.browse_extract_output)
        self.extract_output_button.grid(row=1, column=2, padx=5, pady=5, sticky="w")

        self.extract_progress = ttk.Progressbar(self.extract_frame, orient="horizontal", length=200, mode="determinate")
        self.extract_progress.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

        self.extract_log = tk.Text(self.extract_frame, height=10, width=60)
        self.extract_log.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

        self.extract_start_button = ttk.Button(self.extract_frame, text="Extract", command=self.extract_bdat)
        self.extract_start_button.grid(row=4, column=0, columnspan=3, padx=5, pady=5)

        # Pack Section
        self.pack_frame = ttk.LabelFrame(master, text="Pack JSON to BDAT")
        self.pack_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.pack_label = ttk.Label(self.pack_frame, text="Path to directory containing JSON files:")
        self.pack_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.pack_path = tk.StringVar()
        self.pack_entry = ttk.Entry(self.pack_frame, textvariable=self.pack_path, width=50)
        self.pack_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.pack_button = ttk.Button(self.pack_frame, text="Browse", command=self.browse_pack_input)
        self.pack_button.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        self.pack_output_label = ttk.Label(self.pack_frame, text="Path to output BDAT file:")
        self.pack_output_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.pack_output_path = tk.StringVar()
        self.pack_output_entry = ttk.Entry(self.pack_frame, textvariable=self.pack_output_path, width=50)
        self.pack_output_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.pack_output_button = ttk.Button(self.pack_frame, text="Browse", command=self.browse_pack_output)
        self.pack_output_button.grid(row=1, column=2, padx=5, pady=5, sticky="w")

        self.pack_progress = ttk.Progressbar(self.pack_frame, orient="horizontal", length=200, mode="determinate")
        self.pack_progress.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

        self.pack_log = tk.Text(self.pack_frame, height=10, width=60)
        self.pack_log.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

        self.pack_start_button = ttk.Button(self.pack_frame, text="Pack", command=self.pack_bdat)
        self.pack_start_button.grid(row=4, column=0, columnspan=3, padx=5, pady=5)

        # Configure grid weights to make the UI resizable
        for i in range(3):
            self.extract_frame.columnconfigure(i, weight=1)
            self.pack_frame.columnconfigure(i, weight=1)
        self.extract_frame.rowconfigure(1, weight=1)
        self.pack_frame.rowconfigure(1, weight=1)
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)
        master.rowconfigure(1, weight=1)

    def browse_extract_input(self):
        dirname = filedialog.askdirectory()
        self.extract_path.set(dirname)

    def browse_extract_output(self):
        dirname = filedialog.askdirectory()
        self.extract_output_path.set(dirname)

    def browse_pack_input(self):
        dirname = filedialog.askdirectory()
        self.pack_path.set(dirname)

    def browse_pack_output(self):
        dirname = filedialog.askdirectory()
        self.pack_output_path.set(dirname)

    def extract_bdat(self):
        bdat_dir = self.extract_path.get()
        if not bdat_dir:
            self.log_extract("Error: No BDAT directory selected.")
            return

        output_dir = self.extract_output_path.get()
        if not output_dir:
            self.log_extract("Error: No output directory selected.")
            return

        files = [f for f in os.listdir(bdat_dir) if f.endswith(".bdat")]
        num_files = len(files)
        self.extract_progress["maximum"] = num_files
        self.extract_progress["value"] = 0
        threading.Thread(target=self._extract_bdat, args=(bdat_dir, output_dir, files, self.extract_progress)).start()

    def _extract_bdat(self, bdat_dir, output_dir, files, progress_bar):
        for i, filename in enumerate(files):
            bdat_file = os.path.join(bdat_dir, filename)
            file_name_without_extension = os.path.splitext(filename)[0]
            output_path = os.path.join(output_dir, file_name_without_extension) # Use the filename without extension as the output directory name
            os.makedirs(output_path, exist_ok=True)

            toolset_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bdat-toolset.exe")
            command = f"\"{toolset_path}\" extract \"{bdat_file}\" -o \"{output_path}\" -f json --pretty"
            self.run_command(command, self.extract_log, progress_bar, i+1)

    def pack_bdat(self):
        json_dir = self.pack_path.get()
        if not json_dir:
            self.log_pack("Error: No JSON directory selected.")
            return

        output_dir = self.pack_output_path.get()
        if not output_dir:
            self.log_pack("Error: No output directory selected.")
            return

        self.pack_progress["maximum"] = 1
        self.pack_progress["value"] = 0

        threading.Thread(target=self._pack_bdat, args=(json_dir, output_dir, self.pack_progress)).start()

    def _pack_bdat(self, json_dir, output_dir, progress_bar):
        for item in os.listdir(json_dir):
            item_path = os.path.join(json_dir, item)
            if os.path.isdir(item_path):
                toolset_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bdat-toolset.exe")
                command = f"\"{toolset_path}\" pack \"{item_path}\" -o \"{output_dir}\" -f json"
                self.run_command(command, self.pack_log, progress_bar, 1)

    def run_command(self, command, log_window, progress_bar, progress_value):
        try:
            log_window.delete("1.0", tk.END)
            log_window.insert(tk.END, f"Running: {command}\n")
            log_window.see(tk.END)

            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            while True:
                output = process.stdout.readline()
                if output:
                    log_window.insert(tk.END, output)
                    log_window.see(tk.END)
                    log_window.update_idletasks()  # Update the GUI
                else:
                    return_code = process.poll()
                    if return_code is not None:
                        log_window.insert(tk.END, f"Return code: {return_code}\n")
                        log_window.see(tk.END)
                        log_window.update_idletasks()
                        break

            progress_bar["value"] = progress_value
            progress_bar.update_idletasks()

        except Exception as e:
            log_window.insert(tk.END, f"Error: {e}\n")
            log_window.see(tk.END)
            log_window.update_idletasks()

    def log_extract(self, message):
        self.extract_log.insert(tk.END, message + "\n")
        self.extract_log.see(tk.END)

    def log_pack(self, message):
        self.pack_log.insert(tk.END, message + "\n")
        self.pack_log.see(tk.END)

root = tk.Tk()
app = BDATApp(root)
root.mainloop()
