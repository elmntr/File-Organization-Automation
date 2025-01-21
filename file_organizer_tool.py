# file_organizer_tool.py

import os
import shutil
import json
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox, Listbox, Scrollbar, RIGHT, Y, Toplevel, Text, Button

class FileOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Organizer")

        self.center_window()
        # Set the theme
        self.style = ttk.Style("darkly")

        # Configuration files
        self.config_file = "mappings.json"
        self.settings_file = "settings.json"
        self.file_type_map = self.load_mappings()
        self.undo_log = []

        # Check first-time usage
        self.check_first_time_usage()

        # Layout: Top Frame for folder selection
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.pack(fill=X)

        self.select_folder_button = ttk.Button(top_frame, text="Select Folder", command=self.select_folder, bootstyle="info")
        self.select_folder_button.pack(side=LEFT, padx=10)

        self.start_button = ttk.Button(top_frame, text="Start Organization", command=self.start_organization, state=DISABLED, bootstyle="success")
        self.start_button.pack(side=LEFT, padx=10)

        self.undo_button = ttk.Button(top_frame, text="Undo Last Organization", command=self.undo_organization, state=DISABLED, bootstyle="warning")
        self.undo_button.pack(side=LEFT, padx=10)

        # Layout: Middle Frame for log
        log_frame = ttk.Labelframe(self.root, text="Activity Log", padding=10, bootstyle="primary")
        log_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        self.log_text = ttk.Text(log_frame, height=10, state="disabled")
        self.log_text.pack(fill=BOTH, expand=True)

        # Layout: Bottom Frame for mappings
        mapping_frame = ttk.Labelframe(self.root, text="File Type Mappings", padding=10, bootstyle="secondary")
        mapping_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Add scrollbar to the Listbox
        listbox_frame = ttk.Frame(mapping_frame)
        listbox_frame.pack(fill=X, padx=10, pady=5)

        self.mapping_listbox = Listbox(listbox_frame, height=8)
        self.mapping_listbox.pack(side=LEFT, fill=X, expand=True)

        self.scrollbar = Scrollbar(listbox_frame, orient=VERTICAL, command=self.mapping_listbox.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        self.mapping_listbox.config(yscrollcommand=self.scrollbar.set)
        self.update_mapping_listbox()

        # Add/Edit/Delete mappings
        mapping_controls = ttk.Frame(mapping_frame)
        mapping_controls.pack(fill=X, padx=10, pady=5)

        self.extension_entry = ttk.Entry(mapping_controls, width=15)
        self.extension_entry.pack(side=LEFT, padx=5)
        self.extension_entry.insert(0, "Extension")

        self.folder_entry = ttk.Entry(mapping_controls, width=20)
        self.folder_entry.pack(side=LEFT, padx=5)
        self.folder_entry.insert(0, "Folder Name")

        self.add_mapping_button = ttk.Button(mapping_controls, text="Add/Edit Mapping", command=self.add_edit_mapping, bootstyle="primary")
        self.add_mapping_button.pack(side=LEFT, padx=5)

        self.delete_mapping_button = ttk.Button(mapping_controls, text="Delete Mapping", command=self.delete_mapping, bootstyle="danger")
        self.delete_mapping_button.pack(side=LEFT, padx=5)

        self.selected_folder = None
    
    def center_window(self):
        """Center the window on the screen."""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 800  # You can change this
        window_height = 550  # You can change this

        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)

        self.root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")
        
    
    def check_first_time_usage(self):
        """Check if the user is opening the app for the first time and show the manual."""
        if not os.path.exists(self.settings_file):
            self.show_manual()
            self.save_settings({"first_time": False})
        else:
            with open(self.settings_file, "r") as file:
                settings = json.load(file)
                if settings.get("first_time", True):
                    self.show_manual()
                    settings["first_time"] = False
                    self.save_settings(settings)

    def show_manual(self):
        """Display a manual in a modal window."""
        manual_window = Toplevel(self.root)
        manual_window.title("How to Use")
        manual_window.geometry("800x550")
        manual_window.resizable(False, False)
        manual_window.transient(self.root)  # Make it a modal window
        manual_window.grab_set()

        instructions = """
        Welcome to the File Organizer Tool!
        
        Here's how to use the tool:
        1. Select a folder to organize using the "Select Folder" button.
        2. Configure file type mappings (e.g., .pdf -> PDFs) in the "File Type Mappings" section.
        3. Click "Start Organization" to organize files into subfolders.
        4. Use "Undo Last Organization" to restore files to their original locations.

        Additional Features:
        - Add/Edit/Delete mappings in the "File Type Mappings" section.
        - Activity logs are displayed in real time.
        - Your configurations are saved automatically.

        Fuck u HAHAHHAA
        -JUSTIN
        """

        text_widget = Text(manual_window, wrap="word", font=("Arial", 10), padx=10, pady=10)
        text_widget.insert("1.0", instructions)
        text_widget.config(state="disabled")
        text_widget.pack(fill=BOTH, expand=True)

        close_button = Button(manual_window, text="Close", command=manual_window.destroy, bg="#4CAF50", fg="white", padx=10, pady=5)
        close_button.pack(pady=10)

    def save_settings(self, settings):
        """Save settings to the settings file."""
        with open(self.settings_file, "w") as file:
            json.dump(settings, file, indent=4)

    def log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def load_mappings(self):
        """Load file type mappings from a JSON configuration file."""
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as file:
                return json.load(file)
        else:
            # Default mappings
            return {
                ".pdf": "PDFs",
                ".jpg": "Images",
                ".jpeg": "Images",
                ".png": "Images",
                ".txt": "Text Files",
                ".docx": "Word Documents",
                ".xlsx": "Excel Files",
                ".mp4": "Videos",
            }

    def save_mappings(self):
        """Save the current mappings to the JSON configuration file."""
        with open(self.config_file, "w") as file:
            json.dump(self.file_type_map, file, indent=4)

    def update_mapping_listbox(self):
        """Update the listbox display with the current mappings."""
        self.mapping_listbox.delete(0, "end")
        for ext, folder in self.file_type_map.items():
            self.mapping_listbox.insert("end", f"{ext}: {folder}")

    # (Rest of the existing methods remain unchanged)
    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.selected_folder = folder
            self.log(f"Selected folder: {self.selected_folder}")
            self.start_button.config(state=NORMAL)

    def start_organization(self):
        if not self.selected_folder:
            messagebox.showerror("Error", "No folder selected!")
            return

        self.log("Starting file organization...")
        try:
            self.undo_log.clear()  # Clear previous undo log
            self.organize_files()
            self.log("File organization completed.")
            self.undo_button.config(state=NORMAL)
        except Exception as e:
            self.log(f"Error: {str(e)}")

    def organize_files(self):
        for file_name in os.listdir(self.selected_folder):
            file_path = os.path.join(self.selected_folder, file_name)

            if os.path.isfile(file_path):
                file_ext = os.path.splitext(file_name)[1].lower()
                subfolder_name = self.file_type_map.get(file_ext, "Others")
                subfolder_path = os.path.join(self.selected_folder, subfolder_name)

                if not os.path.exists(subfolder_path):
                    os.makedirs(subfolder_path)

                new_path = os.path.join(subfolder_path, file_name)
                try:
                    shutil.move(file_path, new_path)
                    self.undo_log.append((new_path, file_path))  # Log the move
                    self.log(f"Moved: {file_name} -> {subfolder_name}")
                except Exception as e:
                    self.log(f"Error moving {file_name}: {str(e)}")

    def undo_organization(self):
        if not self.undo_log:
            self.log("No actions to undo.")
            return

        self.log("Undoing last organization...")
        try:
            while self.undo_log:
                new_path, original_path = self.undo_log.pop()
                shutil.move(new_path, original_path)
                self.log(f"Restored: {os.path.basename(original_path)} to {original_path}")
            self.log("Undo completed.")
            self.undo_button.config(state=DISABLED)  # Disable undo after completion
        except Exception as e:
            self.log(f"Error during undo: {str(e)}")

    def add_edit_mapping(self):
        extension = self.extension_entry.get().strip().lower()
        folder_name = self.folder_entry.get().strip()

        if not extension.startswith("."):
            messagebox.showerror("Error", "File extension must start with a '.' (e.g., '.txt').")
            return

        if not folder_name:
            messagebox.showerror("Error", "Folder name cannot be empty.")
            return

        self.file_type_map[extension] = folder_name
        self.save_mappings()  # Save changes to configuration file
        self.update_mapping_listbox()
        self.log(f"Added/Edited mapping: {extension} -> {folder_name}")

    def delete_mapping(self):
        selected = self.mapping_listbox.curselection()
        if not selected:
            messagebox.showerror("Error", "No mapping selected!")
            return

        selected_text = self.mapping_listbox.get(selected[0])
        extension = selected_text.split(":")[0].strip()
        if extension in self.file_type_map:
            del self.file_type_map[extension]
            self.save_mappings()  # Save changes to configuration file
            self.update_mapping_listbox()
            self.log(f"Deleted mapping: {extension}")

    def on_closing(self):
        self.root.destroy()

# Run Application
if __name__ == "__main__":
    root = ttk.Window()
    app = FileOrganizerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
