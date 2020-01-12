import zipfile
import os
import shutil
import typing
from typing import List
from typing import NewType

import utilities as util

class_COLOR = NewType("COLOR", util.COLOR)


def get_dir_paths(dir_name: str) -> List[str]:
    """
    Goes through the specified folder and retrieves all the file paths within.

    Args:\n
            dir_name: str = The path to the directory.

    Returns:\n
            file_paths: List[str] = A list of all the paths in the directory.
    """

    file_paths = []
    for root, directories, files in os.walk(dir_name):
        for filename in files:
            file_path = os.path.join(root, filename)
            file_paths.append(file_path)
            
    return file_paths


class ZipDir:
    """
    Represents the build directory archiving process. 
    """

    def __init__(self, dir_path: str, required_files: List[str], required_dirs: List[str]) -> None:
        self.dir_path = dir_path
        self.required_files = required_files
        self.required_dirs = required_dirs

        
    def build_message(self, message: str, status: str, color: class_COLOR) -> None:
        """
        Prints out a build message from the given arguments in the following format:\n
                f"{message} [{color}{status}{util.COLOR.END}]"
        """

        print(f"{message} [{color}{status}{util.COLOR.END}]")

    
    def ok_message(self, message: str) -> None:
        """
        Pre-built "OK" message in green.
        """

        self.build_message(message, "OK", util.COLOR.LIGHT_GREEN)

    
    def fail_message(self, message: str) -> None:
        """
        Pre-built "FAIL" message in red.
        """

        self.build_message(message, "FAIL", util.COLOR.RED)

    
    def build(self) -> None:
        """
        Builds the zip file:\n
            * First the specified dir is removed to have a clean start.\n
            * Secondly the directory is remade.\n
            * Thirdly any "required_dirs" are copied to the build dir.\n
            * Fourthly any "required_files" are copied to the build dir.\n
            * Finally all the files and folders from the build dir get written to the archive.\n
        """

        try:
            shutil.rmtree(self.dir_path)
            os.mkdir(self.dir_path)
            self.ok_message(f"Cleaning build directory: '{self.dir_path}'")
        except Exception as e:
            self.fail_message(f"Cleaning build directory: '{self.dir_path}'")
            print(e)

        for directory in self.required_dirs:
            try:
                shutil.copytree(f"{directory}", f"{self.dir_path}/{directory}")
                self.ok_message(f"Copying directory: '{directory}'")
            except Exception as e:
                self.fail_message(f"Copying directory: '{directory}'")
                print(e)

        for f in self.required_files:
            try:
                shutil.copy(f, self.dir_path)
                self.ok_message(f"Copying file: '{f}'")
            except Exception as e:
                self.fail_message(f"Copying file: '{f}'")
                print(e)

        try:
            archive = zipfile.ZipFile(f"{self.dir_path}.zip", "w", zipfile.ZIP_DEFLATED, True, 9)
            self.ok_message(f"Creating archive: '{self.dir_path}.zip'")
            for f in get_dir_paths(self.dir_path):
                try:
                    archive.write(f)
                    self.ok_message(f"Writing file to archive: '{f}'")
                except Exception as e:
                    self.fail_message(f"Writing file to archive: '{f}'")
                    print(e)
            archive.close()
        except Exception as e:
            self.fail_message(f"Creating archive: '{self.dir_path}.zip'")
            print(e)
