import os
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from threading import Thread
import queue

def unzip_file(zip_file_path, output_folder, callback):
    """
    Unzip a single file to the specified output folder.
    Calls the callback function upon completion or error.
    """
    try:
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(output_folder)
        callback(None)  # No error
    except Exception as e:
        callback(e)

def handle_unzip_with_timeout(zip_file_path, output_folder, timeout, text_widget):
    """
    Attempts to unzip a file with a specified timeout.
    Updates the text widget based on the operation's success or failure.
    """
    # Queue to communicate between threads
    result_queue = queue.Queue()

    # Wrapper callback to communicate back to the main thread
    def callback(result):
        result_queue.put(result)

    # Start the unzip operation in a separate thread
    unzip_thread = Thread(target=unzip_file, args=(zip_file_path, output_folder, callback))
    unzip_thread.start()

    # Wait for the unzip operation to complete or timeout
    try:
        result = result_queue.get(timeout=timeout)  # Wait for the result with timeout
        if result is None:
            text_widget.insert(tk.END, f"Successfully unzipped: {os.path.basename(zip_file_path)}\n")
        else:
            raise result
    except queue.Empty:
        # If the operation times out, log a message and proceed
        text_widget.insert(tk.END, f"Unzipping timed out for: {os.path.basename(zip_file_path)}. Skipping...\n")
    except Exception as e:
        text_widget.insert(tk.END, f"Error unzipping {os.path.basename(zip_file_path)}: {e}. Skipping...\n")

def unzip_and_delete(zip_folder, text_widget, timeout=10):
    """
    Finds all ZIP files in the folder, creates a corresponding "unzipped" subfolder for each,
    attempts to unzip them into their respective subfolder with a specified timeout,
    and then deletes the ZIP files, with progress updates in the text widget.
    """
    if not os.path.isdir(zip_folder):
        text_widget.insert(tk.END, "The specified folder does not exist.\n")
        return

    files = os.listdir(zip_folder)
    zip_files = [file for file in files if file.endswith('.zip')]

    if not zip_files:
        text_widget.insert(tk.END, "No ZIP files found in the specified folder.\n")
        return

    for zip_file in zip_files:
        zip_file_path = os.path.join(zip_folder, zip_file)
        output_folder = os.path.join(zip_folder, os.path.splitext(zip_file)[0])
        os.makedirs(output_folder, exist_ok=True)

        text_widget.insert(tk.END, f"Starting to unzip: {zip_file}\n")
        handle_unzip_with_timeout(zip_file_path, output_folder, timeout, text_widget)

        try:
            os.remove(zip_file_path)
            text_widget.insert(tk.END, f"Deleted: {zip_file}\n")
        except PermissionError:
            text_widget.insert(tk.END, f"Error deleting {zip_file}: Permission denied. Skipping...\n")

    text_widget.insert(tk.END, "Operation completed. Some files may have been skipped due to errors or timeouts.\n")

def select_folder():
    folder_selected = filedialog.askdirectory()
    folder_path_entry.delete(0, tk.END)
    folder_path_entry.insert(0, folder_selected)

def start_unzip_process():
    folder_path = folder_path_entry.get()
    if folder_path:
        unzip_and_delete(folder_path, output_text)
    else:
        messagebox.showerror("Error", "Please select a folder first.")

# Set up the UI
root = tk.Tk()
root.title("Unzip and Delete ZIP Files")

frame = tk.Frame(root)
frame.pack(pady=20)

folder_path_entry = tk.Entry(frame, width=50)
folder_path_entry.pack(side=tk.LEFT, padx=(0, 10))

browse_button = tk.Button(frame, text="Browse", command=select_folder)
browse_button.pack(side=tk.LEFT)

start_button = tk.Button(root, text="Start Unzip and Delete", command=start_unzip_process)
start_button.pack(pady=(10, 20))

output_text = scrolledtext.ScrolledText(root, width=70, height=10)
output_text.pack()
output_text.configure(state='normal')  # To allow text insertion

root.mainloop()
