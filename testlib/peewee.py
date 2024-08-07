import contextlib
from unittest.mock import Mock, patch


@contextlib.contextmanager
def patch_select(target: str, **kwargs):
    with patch(target=f"{target}.select") as select_mock:
        select_mock.return_value = select_mock
        for attr in ("join", "left_outer_join", "switch", "order_by", "where"):
            getattr(select_mock, attr).return_value = select_mock
        result_mock = Mock(**kwargs)
        for attr in ("get", "get_by_id", "__iter__"):
            setattr(select_mock, attr, result_mock)
        yield result_mock
