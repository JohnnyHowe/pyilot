from upload_parameters import UploadParameters


def upload_to_testflight():
    parameters = UploadParameters().load()


if __name__ == "__main__":
    upload_to_testflight()