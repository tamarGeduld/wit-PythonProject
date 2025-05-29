import os
import shutil
import commit

from func_files import create_folder, copy_project, delete_contents_in_folder, copy_files_with_overwriting, \
    create_hidden_folder, delete_contents_except_wit
from func_files import create_new_file_in_folder
from func_files import add_to_json_file
from func_files import load_from_json_file


class Repository:

    def __init__(self):
        self.path = os.getcwd()
        self.history = load_from_json_file(rf"{self.path}\.wit\history.json")

    def wit_init(self):
        if not os.path.exists(rf"{self.path}\.wit"):
            create_hidden_folder(self.path,".wit")
            create_folder(rf"{self.path}\.wit", "history")
            create_folder(rf"{self.path}\.wit", "add_files")
            create_new_file_in_folder(rf"{self.path}\.wit",'history.json')
            print("Project initialized successfully!")
        else:
            print("The project is already initialized!")

    def wit_commit(self,message):
        new_commit = commit.Commit(message)
        create_folder(rf"{self.path}\.wit\history", str(new_commit.hash_code))
        copy_project(rf"{self.path}", rf"{self.path}\.wit\history\{str(new_commit.hash_code)}")
        copy_files_with_overwriting(rf"{self.path}\.wit\add_files",rf"{self.path}\.wit\history\{str(new_commit.hash_code)}")
        delete_contents_in_folder(rf"{self.path}\.wit\add_files")
        self.history[new_commit.hash_code] = {
            'message' : new_commit.message,
            'date_time' : new_commit.date_time.isoformat()
        }
        add_to_json_file(rf"{self.path}\.wit\history.json",self.history)
        print(f"Commit successful! Commit hash: {new_commit.hash_code}, Message: '{new_commit.message}', Date: {new_commit.date_time.isoformat()}")

    def wit_log(self):
        for hash_code,repos in self.history.items():
            print(f"hash code:{hash_code}\t,date: {repos['date_time']}\t,massage:{repos['message']}")

    def wit_checkout(self,id):
        delete_contents_except_wit(rf"{self.path}")
        copy_project(rf"{self.path}.\.wit\history\{id}", rf"{self.path}")
        print("successfully checked out")

    def wit_add_file(self, file_name):
        shutil.copy(rf"{os.getcwd()}\{file_name}", rf"{self.path}\.wit\add_files")
        print(f"File '{file_name}' has been added successfully.")

    def wit_status(self):
        if not os.listdir(rf"{self.path}\.wit\add_files"):
            print("There are no changes that have not been updated.")
        else:
            print("There are changes that have been updated: ", end=" ")
            for file in os.listdir(rf"{self.path}\.wit\add_files"):
                print(file, end=", ")
            print()