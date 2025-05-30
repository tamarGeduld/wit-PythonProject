import ctypes
import json
import os
import shutil


#יצירת תקייה
def create_folder(path, folder_name):
    # בדוק אם הנתיב קיים
    if os.path.exists(path):
         # עכשיו צור את התיקיה בנתיב עם השם החדש
         folder_path = os.path.join(path, folder_name)
         if not os.path.exists(folder_path):  # אם התיקיה לא קיימת
              os.makedirs(folder_path)  # יצירת התיקיה
         else:
              print(f"Folder '{folder_name}' already exists at this path.")

#יצירת תיקייה נסתרת
def create_hidden_folder(path, folder_name):
    if os.path.exists(path):
        folder_path = os.path.join(path, folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            # יוצר תקייה נסתרת
            ctypes.windll.kernel32.SetFileAttributesW('.wit', 0x02)
        else:
            print(f"Folder '{folder_name}' already exists at this path.")


#יצירת קובץ JSON
def create_new_file_in_folder(path, file_name):
    with open(os.path.join(path, file_name), 'w') as fp:
        pass

#כתיבה לקובץ
def load_from_json_file(path):
    if os.path.exists(path):
        with open(path, "r",encoding="utf-8") as file:
            if os.path.getsize(path)>0:
              return json.load(file)
    return {}
#הוספה לקובץ
def add_to_json_file(path,data):
    with open(path,"w",encoding="utf-8") as file:
        json.dump(data, file,indent=4)

# מתעלמים מתיקיית .wit
def ignore_wit_directory(src, files):
    return ['.wit'] if '.wit' in files else []

# מעתיקים את כל התיקייה חוץ מ-.wit
def copy_project(src, dst):
    if os.path.exists(dst):
         shutil.copytree(src, dst, ignore=ignore_wit_directory,dirs_exist_ok=True)

#מחיקת תוכן של תקייה
def delete_contents_in_folder(path):
    for item in os.listdir(path):
        os.remove(rf"{path}\{item}")

#העתקת קבצים תוך כדי דיריסת קבצים קיימים

def copy_files_with_overwriting(src, dst):
    for item in os.listdir(src):
        src_path = os.path.join(src, item)
        dst_path = os.path.join(dst, item)

        if os.path.isdir(src_path):
            # אופציה א': לדלג על תיקיות
            continue

            # או אופציה ב': להעתיק תיקיות שלמות
            # shutil.copytree(src_path, dst_path, dirs_exist_ok=True)

        else:
            shutil.copy(src_path, dst_path)

#מחיקת תוכן תיקיה מלבד תיקיה .WIT
#def delete_contents_except_wit(path):
    #if os.path.exists(path):
        #for item in os.listdir(path):
            #item_path = os.path.join(path, item)
            #if item != ".wit":
                   # if os.path.isdir(item_path):
                       # shutil.rmtree(item_path)
                    #else:
                      #  os.remove(item_path)
    #else:
       # print(f"Error: The directory does not exist.")
def delete_contents_in_folder(path):
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            # אם זו תיקיה, מוחקים אותה כולה
            shutil.rmtree(item_path)
        else:
            # אם זה קובץ, מוחקים אותו
            os.remove(item_path)


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
