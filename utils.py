import os, re, yaml
from settings import CONFIG_DIR


def get_last_file(files):

    last_file = {"number":0,
                 "file_name": None,
                 }

    for file in files:
        number = re.match(r"\d+", file)
        if number and int(number.group(0)) > last_file["number"]:
            last_file["number"] = int(number.group(0))
            last_file["file_name"] = file

    return last_file


def gen_log_file():

    log_files = (file for file in os.listdir(CONFIG_DIR)
                 if os.path.isfile(os.path.join(CONFIG_DIR, file)))

    log_file = get_last_file(log_files)
    next_file = "0001.yml" if not log_file["file_name"] else "{:04d}.yml".format(log_file["number"] + 1)

    return next_file


def logger(data):

    log_file = gen_log_file()

    with open(os.path.join(CONFIG_DIR, log_file), "w") as f:
        yaml.dump(data, f, default_flow_style=False)
        return log_file


def multidict_to_dict(multidict):

    return {str(key): value for key, value in multidict.items()}


def get_response(url):

    log_files = (file for file in os.listdir(CONFIG_DIR) if os.path.isfile(os.path.join(CONFIG_DIR, file)))

    for file in log_files:
        with open(os.path.join(CONFIG_DIR, file), "r") as f:
            data = yaml.safe_load(f)
            try:
                if data["request"]["url"] == url:
                    data.update({"file_name": file})
                    return data
            except KeyError:
                raise Exception("Not valid yaml file")


def directory_is_not_empty():
    if not os.listdir(CONFIG_DIR):
        return True


def reset_some_response_headers(headers):

    if "Content-Length" in headers:
        del headers["Content-Length"]

    if "Transfer-Encoding" in headers:
        del headers["Transfer-Encoding"]

    if "Content-Encoding" in headers:
        del headers["Content-Encoding"]
