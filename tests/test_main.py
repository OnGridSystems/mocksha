import os

from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from aiohttp import web

from app import init_func
from utils import get_last_file, gen_log_file_name, logger, multidict_to_dict, get_response, directory_is_not_empty, \
    reset_some_response_headers, clean_directory
from settings import CONFIG_DIR


class AppTestCase(AioHTTPTestCase):

    async def get_application(self):
        """
        Override the get_app method to return your application.
        """

        return init_func("app")

    def test_app(self):

        assert type(self.app) == web.Application


    def test_get_last_file(self):
        with open(os.path.join(CONFIG_DIR, "0001.yml"), "w") as f:
            pass

        with open(os.path.join(CONFIG_DIR, "0002.yml"), "w") as f:
            pass

        log_files = (file for file in os.listdir(CONFIG_DIR) if os.path.isfile(os.path.join(CONFIG_DIR, file)))
        last_file = get_last_file(log_files)["file_name"]
        assert f.name == os.path.join(CONFIG_DIR, last_file)


    def test_gen_log_file_name(self):

        log_file_name = gen_log_file_name()

        log_file_name = log_file_name.split(".")

        assert int(log_file_name[0]) and log_file_name[1] =="yml"


    def test_logger(self):

        data = {
            "test_key1": "test_value1",
            "test_key2": "test_value2",
        }

        log_file = logger(data)

        with open(os.path.join(CONFIG_DIR, log_file), "r") as f:
            result = "".join(f.readlines())

        assert "test_key1" in result
        assert "test_key2" in result
        assert "test_value1" in result
        assert "test_value1" in result


    def test_multidict_to_dict(self):

        from multidict import MultiDict

        d = multidict_to_dict(MultiDict([('a', 1), ('b', 2), ('a', 3)]))
        assert isinstance(d, dict)


    def test_get_response_valid_yaml_file(self):

        data = {
            "test_key1": "test_value1",
            "test_key2": "test_value2",
        }

        log_file = logger(data)

        with self.assertRaises(Exception) as context:
            get_response("URL", "text")

        assert str(context.exception) == "Not valid yaml file"


    def test_get_response(self):

        data = {
            "request": {
                "url": "some_url",
                "content": {
                    "body": "some_text"
                },
            }
        }

        logger(data)

        response = get_response("some_url", "some_text")

        assert data["request"]["url"] == response["request"]["url"] \
               and data["request"]["content"]["body"] == response["request"]["content"]["body"]


    def test_directory_is_not_empty(self):

        file = os.path.join(CONFIG_DIR, "0001test.yml")

        with open(file, "w") as f:
            pass

        self.assertTrue(os.path.isfile(os.path.join(CONFIG_DIR, file)), directory_is_not_empty())


    def test_reset_some_response_headers(self):

        d ={
            "key1": "value1",
            "Content-Length": "value2",
        }
        reset_some_response_headers(d)

        self.assertTrue("Content-Length" not in d, "key1" in d)


    def test_clean_directory(self):

        file = os.path.join(CONFIG_DIR, "0001test.yml")

        with open(file, "w") as f:
            pass

        clean_directory()

        self.assertFalse(os.listdir(CONFIG_DIR))
