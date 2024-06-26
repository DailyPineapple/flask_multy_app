import tkinter as tk
from tkinter import ttk, messagebox
from pytube import YouTube, exceptions
import os
from sys import platform
from pathlib import Path

def get_download_path():
    """Returns the default downloads path for linux or windows"""
    if platform == "win32":
        return os.path.join(Path.home(), "Downloads")
    else:
        return os.path.join(Path.home(), "Downloads")

def on_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage_of_completion = bytes_downloaded / total_size * 100
    progress_bar['value'] = percentage_of_completion
    app.update_idletasks()

def download_video():
    url = url_entry.get()
    if not url.strip():
        messagebox.showerror("Error", "Please enter a YouTube URL")
        return
    try:
        yt = YouTube(url, on_progress_callback=on_progress)
        if var.get() == "MP4":
            video = yt.streams.get_highest_resolution()
            video.download(get_download_path())
            messagebox.showinfo("Success", "Video downloaded successfully!")
        elif var.get() == "MP3":
            video = yt.streams.filter(only_audio=True).first()
            output_file = video.download(get_download_path())
            base, ext = os.path.splitext(output_file)
            new_file = base + '.mp3'
            os.rename(output_file, new_file)
            messagebox.showinfo("Success", "Audio downloaded successfully!")
    except exceptions.PytubeError as e:
        messagebox.showerror("Error", f"Failed to download: {str(e)}")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
    finally:
        progress_bar['value'] = 0  # Reset the progress bar for the next operation.

app = tk.Tk()
app.title("YouTube Downloader")

tk.Label(app, text="Enter YouTube URL:").pack(pady=10)

url_entry = tk.Entry(app, width=50)
url_entry.pack(pady=5)

var = tk.StringVar(app)
var.set("MP4")  # default choice

tk.Radiobutton(app, text="MP4", variable=var, value="MP4").pack()
tk.Radiobutton(app, text="MP3", variable=var, value="MP3").pack()

progress_bar = ttk.Progressbar(app, orient='horizontal', mode='determinate', length=280)
progress_bar.pack(pady=10)

download_button = tk.Button(app, text="Download", command=download_video)
download_button.pack(pady=20)

app.mainloop()

