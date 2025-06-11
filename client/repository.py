import os
import shutil
import zipfile
import requests
import commit

from func_files import create_folder, copy_project, delete_contents_in_folder, copy_files_with_overwriting, \
    create_hidden_folder, delete_contents_except_wit
from func_files import create_new_file_in_folder
from func_files import add_to_json_file
from func_files import load_from_json_file
from displayImage import display_image_from_url


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

    def wit_push(self):
        print("Running wit push...")
        history_path = os.path.join(self.path, ".wit", "history")
        zip_path = os.path.join(self.path, "push_package.zip")

        # search the last commit
        latest_commit_path = ""
        if os.path.exists(history_path):
            subdirs = [
                os.path.join(history_path, d) for d in os.listdir(history_path)
                if os.path.isdir(os.path.join(history_path, d))
            ]
            if subdirs:
                latest_commit_path = max(subdirs, key=os.path.getctime)
            else:
                print("No commits found in .wit/history")
                return
        else:
            print(".wit/history directory does not exist")
            return

        # יצירת ZIP
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(latest_commit_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, latest_commit_path)
                    zipf.write(file_path, arcname)

        try:
            with open(zip_path, 'rb') as f:
                files = {'zip_file': ('push_package.zip', f, 'application/zip')}

                response = requests.post("http://127.0.0.1:8000/alert", files=files)
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results")
                    print("Analysis results:\n")
                    for file, checks in results.items():
                        print(f"File: {file}")
                        function_lengths = checks.get("function_lengths", [])
                        print(f"  Function lengths: {', '.join(map(str, function_lengths))}")
                        print("  Issues:")
                        for issue in checks.get("long_functions", []):
                            print(f"    - {issue}")

                        if checks.get("file_too_long"):
                            print(f"    - File is too long (more than 200 lines)")

                        for issue in checks.get("unused_variables", []):
                            print(f"    - Line {issue['line']}: {issue['message']}")

                        for issue in checks.get("missing_docstrings", []):
                            print(f"    - Line {issue['line']}: {issue['message']}")

                        for issue in checks.get("non_english_variable_names", []):
                            print(f"    - Line {issue['line']}: {issue['message']}")

                        print()
                else:
                    print("Server returned an error in alert:", response.status_code)
                    print(response.text)
                    return

            with open(zip_path, 'rb') as f:
                files = {'zip_file': ('push_package.zip', f, 'application/zip')}

                response = requests.post(f"http://127.0.0.1:8000/analyzer",files=files)

                if response.status_code == 200:
                    data = response.json()

                    histogram_url = data.get("histogram_url")
                    pie_chart_url = data.get("pie_chart_url")
                    bar_chart_url = data.get("bar_chart_url")
                    line_chart_url = data.get("line_chart_url")

                    if histogram_url:
                        display_image_from_url(f"http://127.0.0.1:8000{histogram_url}", "Function Length Histogram")

                    if pie_chart_url:
                        display_image_from_url(f"http://127.0.0.1:8000{pie_chart_url}", "Problem Type Pie Chart")

                    if bar_chart_url:
                        display_image_from_url(f"http://127.0.0.1:8000{bar_chart_url}", "Problems Per File Bar Chart")

                    if line_chart_url:
                        display_image_from_url(f"http://127.0.0.1:8000{line_chart_url}", "Problems Per File Line Chart")
                else:
                    print("Server returned an error in analyzer:", response.status_code)
                    print(response.text)

        except requests.RequestException as e:
            print(f"Error during push request: {e}")

        if os.path.exists(zip_path):
            os.remove(zip_path)
