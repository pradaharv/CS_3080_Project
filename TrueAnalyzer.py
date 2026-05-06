import os
import shutil
import zipfile
from datetime import datetime


class SystemAnalyzer:

    SENSITIVE_KEYWORDS = [
        "password", "passwd", "secret", "token", "key",
        "credential", "login", "api", "private"
    ]

    SENSITIVE_EXTENSIONS = [
        ".env", ".key", ".pem", ".crt", ".pfx",
        ".sql", ".db", ".sqlite", ".bak", ".config",".pem"
    ]

    def __init__(self):
        self.home = os.path.expanduser("~")
        self.report_name = "sensitive_file_report.txt"

    def get_size(self, path):
        total_size = 0

        if os.path.isfile(path):
            return os.path.getsize(path)

        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)

                if os.path.exists(file_path) and not os.path.islink(file_path):
                    total_size += os.path.getsize(file_path)

        return total_size

    def is_sensitive_file(self, filename):
        filename = filename.lower()

        for keyword in self.SENSITIVE_KEYWORDS:
            if keyword in filename:
                return True

        for extension in self.SENSITIVE_EXTENSIONS:
            if filename.endswith(extension):
                return True

        return False

    def get_user_folders(self):

        folders = [
            os.path.join(self.home, "Desktop"),
            os.path.join(self.home, "Documents"),
            os.path.join(self.home, "Downloads"),
            os.path.join(self.home, "Pictures"),
            os.path.join(self.home, "Music"),
            os.path.join(self.home, "Videos")
        ]

        return [folder for folder in folders if os.path.exists(folder)]

    def create_report(self):

        with open(self.report_name, "w") as report:
            report.write("User File Security Scan Report\n")
            report.write(f"Scan Date: {datetime.now()}\n")
            report.write("=" * 50 + "\n\n")

            for folder in self.get_user_folders():
                folder_size = self.get_size(folder)

                report.write(f"[DIRECTORY] {folder}\n")
                report.write(f"Size: {folder_size} bytes\n\n")

                for root, dirs, files in os.walk(folder):
                    for file in files:
                        file_path = os.path.join(root, file)

                        if os.path.exists(file_path) and not os.path.islink(file_path):
                            file_size = os.path.getsize(file_path)

                            if self.is_sensitive_file(file):

                                report.write("[POSSIBLE SENSITIVE FILE]\n")
                                report.write(f"Path: {file_path}\n")
                                report.write(f"Size: {file_size} bytes\n\n")

        return self.report_name

    def create_zip(self, report_file):
        zip_name = "information.zip"

        with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(report_file)

        print(f"Report saved inside {zip_name}")

    def create_zip_with_files(self):

        destination_folder = "copied_files"
        os.makedirs(destination_folder, exist_ok=True)

        zip_name = "information.zip"

        with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zipf:

            for root, dirs, files in os.walk(self.home):

                for file in files:
                    file_path = os.path.join(root, file)

                    if self.is_sensitive_file(file):

                        try:
                            # Keep folder structure
                            relative_path = os.path.relpath(file_path, self.home)

                            # Copy file
                            dest_path = os.path.join(destination_folder, relative_path)

                            os.makedirs(os.path.dirname(dest_path), exist_ok=True)

                            shutil.copy2(file_path, dest_path)

                            print(f"Copied: {file_path}")

                            # Add to zip
                            zipf.write(
                                dest_path,
                                arcname=os.path.join("copied_files", relative_path)
                            )

                            print(f"Added to zip: {relative_path}")

                        except Exception as e:
                            print(f"Error processing {file_path}: {e}")

        print(f"\nZip created: {zip_name}")


if __name__ == "__main__":

    analyzer = SystemAnalyzer()

    report_file = analyzer.create_report()

    analyzer.create_zip(report_file)

    analyzer.create_zip_with_files()