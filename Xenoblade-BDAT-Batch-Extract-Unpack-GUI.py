import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import subprocess
import os
import threading
import configparser
from pathlib import Path

class BDATApp:
    def __init__(self, master):
        self.master = master
        master.title("BDAT Conversion Toolset")
        
        # Create all StringVars first
        self.extract_path = tk.StringVar()
        self.extract_output_path = tk.StringVar()
        self.pack_path = tk.StringVar()
        self.pack_output_path = tk.StringVar()
        self.single_extract_path = tk.StringVar()
        self.single_extract_output_path = tk.StringVar()
        self.single_pack_path = tk.StringVar()
        self.single_pack_output_path = tk.StringVar()

        # Config file setup - uses same name as script but with .ini extension
        script_name = Path(__file__).stem
        self.config_file = Path(__file__).parent / f"{script_name}.ini"
        self.config = configparser.ConfigParser()
        self.load_config()

        # Notebook for tabbed interface
        self.notebook = ttk.Notebook(master)
        self.notebook.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # --- Batch Processing Frame ---
        self.batch_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.batch_frame, text="Batch Processing")

        # Extract Section
        self.extract_frame = ttk.LabelFrame(self.batch_frame, text="Extract BDAT to JSON")
        self.extract_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.extract_label = ttk.Label(self.extract_frame, text="Path to directory containing BDAT files:")
        self.extract_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.extract_entry = ttk.Entry(self.extract_frame, textvariable=self.extract_path, width=50)
        self.extract_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.extract_button = ttk.Button(self.extract_frame, text="Browse", command=self.browse_extract_input)
        self.extract_button.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        self.extract_output_label = ttk.Label(self.extract_frame, text="Path to output directory:")
        self.extract_output_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

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
        self.pack_frame = ttk.LabelFrame(self.batch_frame, text="Pack JSON to BDAT")
        self.pack_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.pack_label = ttk.Label(self.pack_frame, text="Path to directory containing JSON files:")
        self.pack_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.pack_entry = ttk.Entry(self.pack_frame, textvariable=self.pack_path, width=50)
        self.pack_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.pack_button = ttk.Button(self.pack_frame, text="Browse", command=self.browse_pack_input)
        self.pack_button.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        self.pack_output_label = ttk.Label(self.pack_frame, text="Path to output BDAT file:")
        self.pack_output_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

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

        # --- Single File Processing Frame ---
        self.single_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.single_frame, text="Single File Processing")

        # Single Extract Section
        self.single_extract_frame = ttk.LabelFrame(self.single_frame, text="Extract Single BDAT to JSON")
        self.single_extract_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.single_extract_label = ttk.Label(self.single_extract_frame, text="Path to BDAT file:")
        self.single_extract_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.single_extract_entry = ttk.Entry(self.single_extract_frame, textvariable=self.single_extract_path, width=50)
        self.single_extract_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.single_extract_button = ttk.Button(self.single_extract_frame, text="Browse", command=self.browse_single_extract_input)
        self.single_extract_button.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        self.single_extract_output_label = ttk.Label(self.single_extract_frame, text="Path to output directory:")
        self.single_extract_output_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.single_extract_output_entry = ttk.Entry(self.single_extract_frame, textvariable=self.single_extract_output_path, width=50)
        self.single_extract_output_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.single_extract_output_button = ttk.Button(self.single_extract_frame, text="Browse", command=self.browse_single_extract_output)
        self.single_extract_output_button.grid(row=1, column=2, padx=5, pady=5, sticky="w")

        self.single_extract_progress = ttk.Progressbar(self.single_extract_frame, orient="horizontal", length=200, mode="determinate")
        self.single_extract_progress.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

        self.single_extract_log = tk.Text(self.single_extract_frame, height=10, width=60)
        self.single_extract_log.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

        self.single_extract_start_button = ttk.Button(self.single_extract_frame, text="Extract", command=self.extract_single_bdat)
        self.single_extract_start_button.grid(row=4, column=0, columnspan=3, padx=5, pady=5)

        # Single Pack Section
        self.single_pack_frame = ttk.LabelFrame(self.single_frame, text="Pack Single JSON to BDAT")
        self.single_pack_frame.grid(row=5, column=0, padx=10, pady=10, sticky="ew")

        self.single_pack_label = ttk.Label(self.single_pack_frame, text="Path to JSON directory:")
        self.single_pack_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.single_pack_entry = ttk.Entry(self.single_pack_frame, textvariable=self.single_pack_path, width=50)
        self.single_pack_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.single_pack_button = ttk.Button(self.single_pack_frame, text="Browse", command=self.browse_single_pack_input)
        self.single_pack_button.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        self.single_pack_output_label = ttk.Label(self.single_pack_frame, text="Path to output BDAT file:")
        self.single_pack_output_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.single_pack_entry = ttk.Entry(self.single_pack_frame, textvariable=self.single_pack_output_path, width=50)
        self.single_pack_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.single_pack_button = ttk.Button(self.single_pack_frame, text="Browse", command=self.browse_single_pack_output)
        self.single_pack_button.grid(row=1, column=2, padx=5, pady=5, sticky="w")

        self.single_pack_progress = ttk.Progressbar(self.single_pack_frame, orient="horizontal", length=200, mode="determinate")
        self.single_pack_progress.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

        self.single_pack_log = tk.Text(self.single_pack_frame, height=10, width=60)
        self.single_pack_log.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

        self.single_pack_start_button = ttk.Button(self.single_pack_frame, text="Pack", command=self.pack_single_bdat)
        self.single_pack_start_button.grid(row=4, column=0, columnspan=3, padx=5, pady=5)

        # Configure grid weights to make the UI resizable
        for i in range(3):
            self.extract_frame.columnconfigure(i, weight=1)
            self.pack_frame.columnconfigure(i, weight=1)
            self.single_extract_frame.columnconfigure(i, weight=1)
            self.single_pack_frame.columnconfigure(i, weight=1)
        self.extract_frame.rowconfigure(1, weight=1)
        self.pack_frame.rowconfigure(1, weight=1)
        self.single_extract_frame.rowconfigure(1, weight=1)
        self.single_pack_frame.rowconfigure(1, weight=1)
        self.batch_frame.columnconfigure(0, weight=1)
        self.batch_frame.rowconfigure(0, weight=1)
        self.batch_frame.rowconfigure(1, weight=1)
        self.single_frame.columnconfigure(0, weight=1)
        self.single_frame.rowconfigure(0, weight=1)
        self.single_frame.rowconfigure(1, weight=1)
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)

    def browse_extract_input(self):
        initialdir = self.extract_path.get() or self.config.get('DEFAULT', 'extract_path', fallback='')
        dirname = filedialog.askdirectory(initialdir=initialdir)
        if dirname:
            self.extract_path.set(dirname)
            self.save_config()

    def browse_extract_output(self):
        initialdir = self.extract_output_path.get() or self.config.get('DEFAULT', 'extract_output_path', fallback='')
        dirname = filedialog.askdirectory(initialdir=initialdir)
        if dirname:
            self.extract_output_path.set(dirname)
            self.save_config()

    def browse_pack_input(self):
        initialdir = self.pack_path.get() or self.config.get('DEFAULT', 'pack_path', fallback='')
        dirname = filedialog.askdirectory(initialdir=initialdir)
        if dirname:
            self.pack_path.set(dirname)
            self.save_config()

    def browse_pack_output(self):
        initialdir = self.pack_output_path.get() or self.config.get('DEFAULT', 'pack_output_path', fallback='')
        dirname = filedialog.askdirectory(initialdir=initialdir)
        if dirname:
            self.pack_output_path.set(dirname)
            self.save_config()

    def browse_single_extract_input(self):
        initialdir = self.single_extract_path.get() or self.config.get('DEFAULT', 'single_extract_path', fallback='')
        filename = filedialog.askopenfilename(
            filetypes=[("BDAT files", "*.bdat")],
            initialdir=os.path.dirname(initialdir) if initialdir else None
        )
        if filename:
            self.single_extract_path.set(filename)
            self.save_config()

    def browse_single_extract_output(self):
        initialdir = self.single_extract_output_path.get() or self.config.get('DEFAULT', 'single_extract_output_path', fallback='')
        dirname = filedialog.askdirectory(initialdir=initialdir)
        if dirname:
            self.single_extract_output_path.set(dirname)
            self.save_config()

    def browse_single_pack_input(self):
        initialdir = self.single_pack_path.get() or self.config.get('DEFAULT', 'single_pack_path', fallback='')
        dirname = filedialog.askdirectory(initialdir=initialdir)
        if dirname:
            self.single_pack_path.set(dirname)
            self.save_config()

    def browse_single_pack_output(self):
        initialdir = self.single_pack_output_path.get() or self.config.get('DEFAULT', 'single_pack_output_path', fallback='')
        filename = filedialog.asksaveasfilename(
            defaultextension=".bdat",
            filetypes=[("BDAT files", "*.bdat")],
            initialdir=os.path.dirname(initialdir) if initialdir else None
        )
        if filename:
            self.single_pack_output_path.set(filename)
            self.save_config()

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

    def extract_single_bdat(self):
        bdat_file = self.single_extract_path.get()
        if not bdat_file:
            self.log_extract("Error: No BDAT file selected.")
            return

        output_dir = self.single_extract_output_path.get()
        if not output_dir:
            self.log_extract("Error: No output directory selected.")
            return

        self.single_extract_progress["maximum"] = 1
        self.single_extract_progress["value"] = 0
        threading.Thread(target=self._extract_single_bdat, args=(bdat_file, output_dir, self.single_extract_progress)).start()

    def _extract_single_bdat(self, bdat_file, output_dir, progress_bar):
        filename = os.path.basename(bdat_file)
        file_name_without_extension = os.path.splitext(filename)[0]
        output_path = os.path.join(output_dir, file_name_without_extension) # Use the filename without extension as the output directory name
        os.makedirs(output_path, exist_ok=True)

        toolset_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bdat-toolset.exe")
        command = f"\"{toolset_path}\" extract \"{bdat_file}\" -o \"{output_path}\" -f json --pretty"
        self.run_command(command, self.single_extract_log, progress_bar, 1)

    def pack_single_bdat(self):
        json_dir = self.single_pack_path.get()
        if not json_dir:
            self.log_pack("Error: No JSON directory selected.")
            return

        output_file = self.single_pack_output_path.get()
        if not output_file:
            self.log_pack("Error: No output file selected.")
            return

        self.single_pack_progress["maximum"] = 1
        self.single_pack_progress["value"] = 0

        threading.Thread(target=self._pack_single_bdat, args=(json_dir, output_file, self.single_pack_progress)).start()

    def _pack_single_bdat(self, json_dir, output_file, progress_bar):
        toolset_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bdat-toolset.exe")
        command = f"\"{toolset_path}\" pack \"{json_dir}\" -o \"{output_file}\" -f json"
        self.run_command(command, self.single_pack_log, progress_bar, 1)

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

    def load_config(self):
        if self.config_file.exists():
            self.config.read(self.config_file)
            if 'DEFAULT' in self.config:
                self.extract_path.set(self.config['DEFAULT'].get('extract_path', ''))
                self.extract_output_path.set(self.config['DEFAULT'].get('extract_output_path', ''))
                self.pack_path.set(self.config['DEFAULT'].get('pack_path', ''))
                self.pack_output_path.set(self.config['DEFAULT'].get('pack_output_path', ''))
                self.single_extract_path.set(self.config['DEFAULT'].get('single_extract_path', ''))
                self.single_extract_output_path.set(self.config['DEFAULT'].get('single_extract_output_path', ''))
                self.single_pack_path.set(self.config['DEFAULT'].get('single_pack_path', ''))
                self.single_pack_output_path.set(self.config['DEFAULT'].get('single_pack_output_path', ''))

    def save_config(self):
        self.config['DEFAULT'] = {
            'extract_path': self.extract_path.get(),
            'extract_output_path': self.extract_output_path.get(),
            'pack_path': self.pack_path.get(),
            'pack_output_path': self.pack_output_path.get(),
            'single_extract_path': self.single_extract_path.get(),
            'single_extract_output_path': self.single_extract_output_path.get(),
            'single_pack_path': self.single_pack_path.get(),
            'single_pack_output_path': self.single_pack_output_path.get()
        }
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

root = tk.Tk()
app = BDATApp(root)
root.mainloop()
