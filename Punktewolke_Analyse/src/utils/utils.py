# utils.py
import os


def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def save_text(text, output_path):
    with open(output_path, "a") as file:
        file.write(text)
