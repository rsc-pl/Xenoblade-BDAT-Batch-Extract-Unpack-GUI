import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import subprocess
import os
import sys
import threading
import configparser
from pathlib import Path
import shutil  # Added for moving files

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

        # New Variable for XC3 Mode
        self.xc3_mode = tk.BooleanVar()

        # Config file setup
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

        self.pack_label = ttk.Label(self.pack_frame, text="Path to directory (Base 'gb' folder if XC3 mode):")
        self.pack_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.pack_entry = ttk.Entry(self.pack_frame, textvariable=self.pack_path, width=50)
        self.pack_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.pack_button = ttk.Button(self.pack_frame, text="Browse", command=self.browse_pack_input)
        self.pack_button.grid(row=0, column=2, padx=5, pady=5, sticky="w")

        self.pack_output_label = ttk.Label(self.pack_frame, text="Path to output directory:")
        self.pack_output_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.pack_output_entry = ttk.Entry(self.pack_frame, textvariable=self.pack_output_path, width=50)
        self.pack_output_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.pack_output_button = ttk.Button(self.pack_frame, text="Browse", command=self.browse_pack_output)
        self.pack_output_button.grid(row=1, column=2, padx=5, pady=5, sticky="w")

        # XC3 Mode Checkbox
        self.xc3_check = ttk.Checkbutton(self.pack_frame, text="Xenoblade 3 Mode (Process 'game'/'evt' & Organize)", variable=self.xc3_mode)
        self.xc3_check.grid(row=2, column=0, columnspan=3, padx=5, pady=5)

        self.pack_progress = ttk.Progressbar(self.pack_frame, orient="horizontal", length=200, mode="determinate")
        self.pack_progress.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

        self.pack_log = tk.Text(self.pack_frame, height=10, width=60)
        self.pack_log.grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

        self.pack_start_button = ttk.Button(self.pack_frame, text="Pack", command=self.pack_bdat)
        self.pack_start_button.grid(row=5, column=0, columnspan=3, padx=5, pady=5)

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

        # Configure grid weights
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

        # Handle window closing
        master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """Saves configuration and closes the application."""
        self.save_config()
        self.master.destroy()

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

    def get_toolset_path(self):
        """Determines the correct bdat-toolset executable path based on the OS."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if sys.platform == "win32":
            tool_name = "bdat-toolset.exe"
        else:
            tool_name = "bdat-toolset-linux"

        toolset_path = os.path.join(script_dir, tool_name)
        if not os.path.isfile(toolset_path):
            tk.messagebox.showerror("Error", f"Toolset executable not found at: {toolset_path}")
            return None
        return toolset_path

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
        toolset_path = self.get_toolset_path()
        if not toolset_path:
            self.log_extract("Could not find bdat-toolset executable. Aborting.")
            return

        for i, filename in enumerate(files):
            bdat_file = os.path.join(bdat_dir, filename)
            file_name_without_extension = os.path.splitext(filename)[0]
            output_path = os.path.join(output_dir, file_name_without_extension)
            os.makedirs(output_path, exist_ok=True)

            command = [toolset_path, "extract", bdat_file, "-o", output_path, "-f", "json", "--pretty"]
            self.run_command(command, self.extract_log, progress_bar, i+1)

    def pack_bdat(self):
        input_path = self.pack_path.get()
        if not input_path:
            self.log_pack("Error: No input directory selected.")
            return

        output_path = self.pack_output_path.get()
        if not output_path:
            self.log_pack("Error: No output directory selected.")
            return

        # Check if XC3 Mode is enabled
        is_xc3 = self.xc3_mode.get()

        if is_xc3:
            # XC3 Mode: Expects 'game' and 'evt' subfolders in the input path
            game_input = os.path.join(input_path, "game")
            evt_input = os.path.join(input_path, "evt")

            # Warn if folders are missing, but don't strictly crash if one is missing
            if not os.path.exists(game_input) and not os.path.exists(evt_input):
                 self.log_pack(f"Error: XC3 Mode is on, but neither 'game' nor 'evt' folders found in {input_path}")
                 return

            # Prepare output paths
            game_output = os.path.join(output_path, "game")
            evt_output = os.path.join(output_path, "evt")

            # Start XC3 Thread
            threading.Thread(target=self._pack_bdat_xc3, args=(input_path, output_path, self.pack_progress)).start()

        else:
            # Standard Mode
            subdirectories = [d for d in os.listdir(input_path) if os.path.isdir(os.path.join(input_path, d))]
            self.pack_progress["maximum"] = len(subdirectories)
            self.pack_progress["value"] = 0

            threading.Thread(target=self._pack_bdat, args=(input_path, output_path, subdirectories, self.pack_progress)).start()

    def _pack_bdat(self, json_dir, output_dir, subdirectories, progress_bar, start_index=0):
        toolset_path = self.get_toolset_path()
        if not toolset_path:
            self.log_pack("Could not find bdat-toolset executable. Aborting.")
            return

        os.makedirs(output_dir, exist_ok=True)

        for i, item in enumerate(subdirectories):
            item_path = os.path.join(json_dir, item)
            output_file_path = os.path.join(output_dir, f"{item}.bdat")

            if os.path.exists(output_file_path):
                try:
                    os.remove(output_file_path)
                    self.log_pack(f"Removed existing file: {output_file_path}")
                except OSError as e:
                    self.log_pack(f"Error removing {output_file_path}: {e}")
                    continue

            command = [toolset_path, "pack", item_path, "-o", output_dir, "-f", "json"]
            self.run_command(command, self.pack_log, progress_bar, start_index + i + 1)

    def _pack_bdat_xc3(self, base_input, base_output, progress_bar):
        self.pack_log.delete("1.0", tk.END)
        self.log_pack("--- Starting XC3 Batch Mode ---")

        folders_to_process = []

        # 1. Identify 'game' folders
        game_in = os.path.join(base_input, "game")
        game_out = os.path.join(base_output, "game")
        game_subs = []
        if os.path.exists(game_in):
             game_subs = [d for d in os.listdir(game_in) if os.path.isdir(os.path.join(game_in, d))]

        # 2. Identify 'evt' folders
        evt_in = os.path.join(base_input, "evt")
        evt_out = os.path.join(base_output, "evt")
        evt_subs = []
        if os.path.exists(evt_in):
            evt_subs = [d for d in os.listdir(evt_in) if os.path.isdir(os.path.join(evt_in, d))]

        total_files = len(game_subs) + len(evt_subs)
        progress_bar["maximum"] = total_files
        progress_bar["value"] = 0
        current_progress = 0

        # Process 'game'
        if game_subs:
            self.log_pack(f"Processing 'game' folder ({len(game_subs)} items)...")
            self._pack_bdat(game_in, game_out, game_subs, progress_bar, start_index=current_progress)
            current_progress += len(game_subs)

        # Process 'evt'
        if evt_subs:
            self.log_pack(f"Processing 'evt' folder ({len(evt_subs)} items)...")
            self._pack_bdat(evt_in, evt_out, evt_subs, progress_bar, start_index=current_progress)
            current_progress += len(evt_subs)

        self.log_pack("\n--- Packing Finished ---")

        # 3. Trigger File Moving Logic (Only for evt)
        if os.path.exists(evt_out):
            self.log_pack("\n--- Starting XC3 File Reorganization (evt folder) ---")
            self.reorganize_evt_folder(evt_out)
            self.log_pack("--- Reorganization Finished ---")

    def reorganize_evt_folder(self, directory):
        """
        Integrated logic from movefiles.py.
        Moves .bdat files in the specified directory to subfolders based on filename.
        """

        # Define exceptions (filename: target_folder)
        exceptions = {
            "msg_ev10010100.bdat": "ev30",
            "msg_ev10030100.bdat": "ev30",
            "msg_mv021801.bdat": "cq",
            "msg_mv062602.bdat": "cq",
            "msg_ev10010100.bdat": "ev01",
            "msg_mv01100110.bdat": "ev01",
            "msg_mv01290110.bdat": "ev01",
            "msg_mv01310140.bdat": "ev01",
            "msg_ev10020100.bdat": "ev03",
            "msg_ev10020200.bdat": "ev03",
            "msg_mv03285130.bdat": "ev03",
            "msg_mv04220110.bdat": "ev04",
            "msg_ev_featuredsong.bdat": "ev05",
            "msg_ev10020300.bdat": "ev05",
            "msg_ev10020400.bdat": "ev06",
            "msg_ev_endthemesong.bdat": "ev07",
        }

        # Define valid folder names
        valid_folders = ["ask", "cq", "ev01", "ev02", "ev03", "ev04", "ev05", "ev06", "ev07", "ev08", "ev09", "ev10", "ev11", "ev12", "ev13", "ev14", "ev15", "ev30", "ev40", "fev", "nq", "sq", "tlk", "tq"]

        files_moved = 0

        try:
            for filename in os.listdir(directory):
                if filename.endswith(".bdat"):
                    source_path = os.path.join(directory, filename)
                    target_folder = None

                    # Check for exceptions first
                    if filename in exceptions:
                        target_folder = exceptions[filename]
                    else:
                        # Extract folder name from filename
                        for folder in valid_folders:
                            if filename.startswith(f"msg_{folder}"):
                                target_folder = folder
                                break

                    if target_folder:
                        target_path = os.path.join(directory, target_folder)
                        if not os.path.exists(target_path):
                            os.makedirs(target_path)

                        destination_path = os.path.join(target_path, filename)
                        try:
                            # If destination exists, remove it first to allow overwrite (shutil.move fails if dest exists on some OS)
                            if os.path.exists(destination_path):
                                os.remove(destination_path)

                            shutil.move(source_path, destination_path)
                            self.log_pack(f"Moved '{filename}' to '{target_folder}'")
                            files_moved += 1
                        except Exception as e:
                            self.log_pack(f"Error moving '{filename}' to '{target_folder}': {e}")
                    # else:
                         # Optional: Log unmatched files
                         # self.log_pack(f"'{filename}' not matched, leaving in root.")

            self.log_pack(f"Total files reorganized: {files_moved}")

        except Exception as e:
            self.log_pack(f"Critical error during directory iteration: {e}")


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
        toolset_path = self.get_toolset_path()
        if not toolset_path:
            self.log_extract("Could not find bdat-toolset executable. Aborting.")
            return

        filename = os.path.basename(bdat_file)
        file_name_without_extension = os.path.splitext(filename)[0]
        output_path = os.path.join(output_dir, file_name_without_extension)
        os.makedirs(output_path, exist_ok=True)

        command = [toolset_path, "extract", bdat_file, "-o", output_path, "-f", "json", "--pretty"]
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
        toolset_path = self.get_toolset_path()
        if not toolset_path:
            self.log_pack("Could not find bdat-toolset executable. Aborting.")
            return

        if os.path.exists(output_file):
            try:
                os.remove(output_file)
                self.log_pack(f"Removed existing file to overwrite: {output_file}")
            except OSError as e:
                self.log_pack(f"Error removing {output_file}: {e}")
                return

        command = [toolset_path, "pack", json_dir, "-o", output_file, "-f", "json"]

        self.run_command(command, self.single_pack_log, progress_bar, 1)

    def run_command(self, command_list, log_window, progress_bar, progress_value):
        try:
            # Only clear log if it's the very start of a sequence (value is 0)
            if progress_bar["value"] == 0 and "XC3" not in log_window.get("1.0", "1.end"):
                 log_window.delete("1.0", tk.END)

            log_window.insert(tk.END, f"Running: {' '.join(command_list)}\n\n")
            log_window.see(tk.END)

            process = subprocess.Popen(command_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True)

            while True:
                output = process.stdout.readline()
                if output:
                    log_window.insert(tk.END, output)
                    log_window.see(tk.END)
                    log_window.update_idletasks()
                else:
                    return_code = process.poll()
                    if return_code is not None:
                        log_window.insert(tk.END, f"\nProcess finished with return code: {return_code}\n\n")
                        log_window.see(tk.END)
                        log_window.update_idletasks()
                        break

            progress_bar["value"] = progress_value
            progress_bar.update_idletasks()

        except FileNotFoundError:
            log_window.insert(tk.END, f"Error: Command not found. Make sure '{command_list[0]}' is in the correct directory.\n")
            log_window.see(tk.END)
        except Exception as e:
            log_window.insert(tk.END, f"An unexpected error occurred: {e}\n")
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
                # Load XC3 mode boolean
                self.xc3_mode.set(self.config['DEFAULT'].getboolean('xc3_mode', False))

    def save_config(self):
        self.config['DEFAULT'] = {
            'extract_path': self.extract_path.get(),
            'extract_output_path': self.extract_output_path.get(),
            'pack_path': self.pack_path.get(),
            'pack_output_path': self.pack_output_path.get(),
            'single_extract_path': self.single_extract_path.get(),
            'single_extract_output_path': self.single_extract_output_path.get(),
            'single_pack_path': self.single_pack_path.get(),
            'single_pack_output_path': self.single_pack_output_path.get(),
            'xc3_mode': str(self.xc3_mode.get())
        }
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

root = tk.Tk()
app = BDATApp(root)
root.mainloop()
