from utils.urls import DynamicURL


class TestDynamicUrl:

    def test_create_dynamic_url_with_query_params(self):
        url = DynamicURL("https", "example.com", "/path", param1="value1", param2="value2")
        assert url.scheme == "https"
        assert url.netloc == "example.com"
        assert url.path == "/path"
        assert url.query_params == {"param1": "value1", "param2": "value2"}

    def test_dynamic_url_str_representation(self):
        url = DynamicURL("https", "example.com", "/path", param1="value1", param2="value2")
        assert str(url) == "https://example.com/path?param1=value1&param2=value2"

    def test_create_dynamic_url_no_query_params(self):
        url = DynamicURL("https", "example.com", "/path")
        assert url.scheme == "https"
        assert url.netloc == "example.com"
        assert url.path == "/path"
        assert url.query_params == {}

    def test_create_dynamic_url_empty_path(self):
        url = DynamicURL("https", "example.com", "")
        assert url.scheme == "https"
        assert url.netloc == "example.com"
        assert url.path == ""
        assert url.query_params == {}

    def test_create_dynamic_url_special_chars_in_query_params(self):
        url = DynamicURL("https", "example.com", "/path", param="value with spaces & special=chars")
        assert url.scheme == "https"
        assert url.netloc == "example.com"
        assert url.path == "/path"
        assert url.query_params == {"param": "value with spaces & special=chars"}
        assert str(url) == "https://example.com/path?param=value+with+spaces+%26+special%3Dchars"
