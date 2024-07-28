import json
import logging
import os
import threading
import time
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

from chatgpt_module import process_resume
from dn_helper import create_tables_and_store_data, export_to_excel

directory = None
txt_logs = None


class TextHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.insert(tk.END, msg + '\n')
        self.text_widget.see(tk.END)


def choose_directory():
    global directory
    directory = filedialog.askdirectory(initialdir="/home/roman/Downloads/Resumes",
                                        title="Select directory with Resumes", mustexist=True)
    return


def start_processing_thread(logger):
    thread = threading.Thread(target=start_processing, args=(logger,))
    thread.start()


def check_json_validity(json_string, logger):
    try:
        json.loads(json_string)
        return True
    except json.JSONDecodeError as err:
        logger.info(f"Error in parsing JSON: {err}")
        return False


def start_processing(logger):
    if directory is None:
        messagebox.showerror("Error", "Please choose directory first")
        return
    logger.info(f"Start processing files in directory: {directory}")
    # Здесь вы можете начать обработку файлов из выбранной директории
    for file in os.listdir(directory):
        if file.endswith(".pdf"):
            if file.__sizeof__() > 10000:
                logger.error(f"File {file} is too big. Skipping")
                continue
            file_path = os.path.join(directory, file)
            logger.info(f"Start processing file: {file_path} size: {os.path.getsize(file_path)} bytes")
            start_time = time.time()
            result = process_resume(file_path, logger)
            if result == "":
                logger.error(f"Error processing file: {file_path}")
                continue
            end_time = time.time()
            logger.info(f"End processing file: {file_path}. Time: {end_time - start_time:.3f} seconds")
            logger.info(result)
            result = json.dumps(result, indent=4)
            is_valid = check_json_validity(str(result), logger)
            if not is_valid:
                logger.error(f"Invalid JSON in file: {file_path}")
            else:
                logger.info(f"Valid JSON in file: {file_path}")
                create_tables_and_store_data(result, "data.db")
    logger.info(f"End processing files in directory: {directory}")
    # теперь нам необходимо все данные, которые мы положили в базу выложить в виде одного excel файла
    export_to_excel("data.db", "data.xlsx")
    logger.info("Exported data to excel")
    logger.info("All files processed")
    return


def config_frames(logger):
    root = tk.Tk()
    root.title("Resumes Processor. Version 1.0 (beta)")
    frame1 = tk.Frame(root)

    frame1.pack()
    frame2 = tk.Frame(root)
    frame2.pack()
    btn_choose_directory = tk.Button(frame1, text="Step 1: Choose Directory", command=choose_directory)
    btn_choose_directory.pack(side=tk.LEFT)
    btn_start = tk.Button(frame1, text="Step 2: Start processing", command=lambda: start_processing_thread(logger))
    btn_start.pack(side=tk.LEFT)
    txt_logs = tk.Text(frame2, height=40, width=150, wrap=tk.WORD, bg="light gray")
    txt_logs.pack()
    return root, txt_logs


def config_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    return logger


def add_handler_to_logger(logger, text_widget):
    th = TextHandler(text_widget)
    th.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    th.setFormatter(formatter)
    logger.addHandler(th)
    return logger


# Пример использования
if __name__ == "__main__":
    logger = config_logger()
    root, txt_logs = config_frames(logger)
    logger = add_handler_to_logger(logger, txt_logs)
    root.mainloop()
