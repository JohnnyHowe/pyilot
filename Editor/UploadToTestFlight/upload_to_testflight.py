import os
from typing import Callable
from testflight_uploader.upload_configuration import UploadConfiguration
from testflight_uploader.testflight_uploader import TestflightUploader
from testflight_uploader.app_store_connect_key_creator import create_api_key_file
# TODO find better solution to this
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pretty_print import *


def main():
    api_key_path = create_api_key_file()

    # Run the uploader safely
    def get_configuration_and_upload():
        configuration = UploadConfiguration(api_key_path)
        uploader = TestflightUploader(configuration)
        uploader.upload()
    error = _run_safe(get_configuration_and_upload)

    api_key_path.unlink()

    # Raise an error if there was one
    if error:
        raise error


def _run_safe(func: Callable):
    try:
        func()
        return None
    except Exception as exception:
        return exception


if __name__ == "__main__":
    main()