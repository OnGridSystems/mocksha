import os
import unittest

from aiohttp import web

from mocksha.app import init_func
from mocksha.utils import get_last_file, gen_log_file_name, multidict_to_dict, directory_is_not_empty, \
    reset_some_response_headers, clean_config_directory
from mocksha.settings import CONFIG_DIR


class UnitTestCase(unittest.TestCase):

    def setUp(self):
        self.app = init_func(test=True)

    def tearDown(self):
        clean_config_directory()

    def test_app(self):
        assert type(self.app) == web.Application

    def test_get_last_file(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp_dir:

            file_1 = os.path.join(tmp_dir, "0001.yml")
            file_2 = os.path.join(tmp_dir, "0002.yml")

            with open(file_1, "w") as f:
                pass
            with open(file_2, "w") as f:
                pass

            log_files = (file for file in os.listdir(tmp_dir) if os.path.isfile(os.path.join(tmp_dir, file)))
            last_file = get_last_file(log_files)["file_name"]

            assert f.name == os.path.join(tmp_dir, last_file)

    def test_gen_log_file_name(self):
        log_file_name = gen_log_file_name()

        log_file_name = log_file_name.split(".")

        assert int(log_file_name[0]) and log_file_name[1] =="yml"

    # def test_logger(self):
    #     data = {
    #         "test_key1": "test_value1",
    #         "test_key2": "test_value2",
    #     }
    #
    #     log_file = logger(data)
    #
    #     with open(os.path.join(CONFIG_DIR, log_file), "r") as f:
    #         result = "".join(f.readlines())
    #
    #     assert "test_key1" in result
    #     assert "test_key2" in result
    #     assert "test_value1" in result
    #     assert "test_value1" in result

    def test_multidict_to_dict(self):
        from multidict import MultiDict

        d = multidict_to_dict(MultiDict([('a', 1), ('b', 2), ('a', 3)]))
        assert isinstance(d, dict)

    # def test_get_response_valid_yaml_file(self):
    #     data = {
    #         "test_key1": "test_value1",
    #         "test_key2": "test_value2",
    #     }
    #
    #     log_file = logger(data)
    #
    #     with self.assertRaises(KeyError):
    #         get_response("URL", "text")

    # def test_get_response(self):
    #     data = {
    #         "request": {
    #             "url": "some_url",
    #             "content": {
    #                 "body": "some_text"
    #             },
    #         }
    #     }
    #
    #     logger(data)
    #
    #     response = get_response("some_url", "some_text")
    #
    #     assert data["request"]["url"] == response["request"]["url"] \
    #            and data["request"]["content"]["body"] == response["request"]["content"]["body"]

    def test_directory_is_not_empty(self):
        file = os.path.join(CONFIG_DIR, "0001test.yml")

        with open(file, "w") as f:
            pass

        self.assertTrue(os.path.isfile(os.path.join(CONFIG_DIR, file)), directory_is_not_empty())

    def test_reset_some_response_headers(self):
        d ={
            "key1": "value1",
            "Content-Length": "value",
            "Transfer-Encoding": "value",
            "Content-Encoding": "value",
        }
        reset_some_response_headers(d)

        self.assertTrue("Content-Length" not in d, "key1" in d)
        self.assertFalse("Transfer-Encoding" in d)
        self.assertFalse("Content-Encoding" in d)

    def test_clean_directory(self):
        file = os.path.join(CONFIG_DIR, "0001test.yml")

        with open(file, "w") as f:
            pass

        clean_config_directory()

        self.assertFalse(os.listdir(CONFIG_DIR))
