import os, re, yaml


mocksha_app_dir = os.path.abspath(os.path.dirname(__file__))
YAML_files_store = os.path.join(mocksha_app_dir, "YAML_files_store")


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

    log_files = (file for file in os.listdir(YAML_files_store)
                 if os.path.isfile(os.path.join(YAML_files_store, file)))

    log_file = get_last_file(log_files)
    next_file = "0001.yml" if not log_file["file_name"] else "{:04d}.yml".format(log_file["number"] + 1)

    return next_file


def logger(data):

    log_file = gen_log_file()

    with open(os.path.join(YAML_files_store, log_file), "w") as f:
        yaml.dump(data, f, default_flow_style=False)
        return True


def multidict_to_dict(multidict):

    d = {}
    for key, value in multidict.items():
        key_ = str(key)
        if not d.get(key_):
            d.update({key_: value})
        else:
            d.update({key_: d[key_]+"; {}".format(value)})

    return d


def get_response(url):

    log_files = (file for file in os.listdir(YAML_files_store) if os.path.isfile(os.path.join(YAML_files_store, file)))

    for file in log_files:
        with open(os.path.join(YAML_files_store, file), "r") as f:
            data = yaml.safe_load(f)

            if data["request"]["url"] == url:
                print(data)
                return data
