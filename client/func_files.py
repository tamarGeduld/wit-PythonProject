import ctypes
import json
import os
import shutil


def create_folder(path, folder_name):
    if os.path.exists(path):
         folder_path = os.path.join(path, folder_name)
         if not os.path.exists(folder_path):
              os.makedirs(folder_path)
         else:
              print(f"Folder '{folder_name}' already exists at this path.")

def create_hidden_folder(path, folder_name):
    if os.path.exists(path):
        folder_path = os.path.join(path, folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            ctypes.windll.kernel32.SetFileAttributesW('.wit', 0x02)
        else:
            print(f"Folder '{folder_name}' already exists at this path.")


def create_new_file_in_folder(path, file_name):
    with open(os.path.join(path, file_name), 'w') as fp:
        pass

def load_from_json_file(path):
    if os.path.exists(path):
        with open(path, "r",encoding="utf-8") as file:
            if os.path.getsize(path)>0:
              return json.load(file)
    return {}

def add_to_json_file(path,data):
    with open(path,"w",encoding="utf-8") as file:
        json.dump(data, file,indent=4)

def ignore_wit_directory(src, files):
    return ['.wit'] if '.wit' in files else []

#  copy all aprat from .wit folder
def copy_project(src, dst):
    if os.path.exists(dst):
         shutil.copytree(src, dst, ignore=ignore_wit_directory,dirs_exist_ok=True)

def delete_contents_in_folder(path):
    for item in os.listdir(path):
        os.remove(rf"{path}\{item}")

def copy_files_with_overwriting(src,dist):
    for item in os.listdir(src):
        if os.path.exists(item):
            shutil.copy(rf"{src}\{item}",dist)

def delete_contents_except_wit(path):
    if os.path.exists(path):
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if item != ".wit":
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    else:
                        os.remove(item_path)
    else:
        print(f"Error: The directory does not exist.")
