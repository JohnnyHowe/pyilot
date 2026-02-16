from upload_parameters import UploadParameters
from upload_to_test_flight import upload_to_testflight


def upload_to_testflight_cmd_entry():
    parameters = UploadParameters()
    parameters.load()
    upload_to_testflight(*parameters.get_values())


if __name__ == "__main__":
    upload_to_testflight_cmd_entry()
