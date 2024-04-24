import warnings

import pytest

from common.api.flask_ext.authentication.common import get_domain


@pytest.mark.unit
def test_get_domain_from_origin(base_flask_app) -> None:
    # This suppresses a warning from flask that looks like this:
    # "Current server name 'test.site:9000' doesn't match configured server name 'dev.localhost'"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with base_flask_app.test_request_context(headers={"Origin": "http://test.site:9000/foo/"}):
            assert get_domain() == "test.site"


@pytest.mark.unit
def test_get_domain_from_host(base_flask_app) -> None:
    # This suppresses a warning from flask that looks like this:
    # "Current server name 'test.site:9000' doesn't match configured server name 'dev.localhost'"
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with base_flask_app.test_request_context(headers={"Host": "test.site:9000"}):
            assert get_domain() == "test.site"


@pytest.mark.unit
def test_get_domain_valueerror_malformed_host(base_flask_app) -> None:
    """The Host header should not contain a URL scheme."""
    # Temporarily suppresses the following warning:
    # UserWarning: Current server name 'http://dev.localhost/foo/' doesn't match configured server name 'dev.localhost'
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with base_flask_app.test_request_context(headers={"Host": "http://dev.localhost/foo/"}):
            with pytest.raises(ValueError):
                get_domain()
