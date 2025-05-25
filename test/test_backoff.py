
import pytest
from src.backoff import backoff


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr("src.backoff.sleep", lambda *_: None)
    yield


class TestBackoff:
    def test_invalid_delay_raises(self):
        with pytest.raises(ValueError):
            @backoff(delay=-1)
            def foo():
                ...

    def test_invalid_retries_raises(self):
        with pytest.raises(ValueError):
            @backoff(retries=0)
            def bar():
                ...
                
    def test_returns_value_if_no_exception(self):
        @backoff(delay=0, retries=3)
        def always_succeeds():
            return "OK"

        assert always_succeeds() == "OK"

    def test_raises_after_exhausting_all_retries(self):
        call_count = 0
        retries = 4

        @backoff(delay=0.01, retries=retries)
        def count_and_fail():
            nonlocal call_count
            call_count += 1
            raise Exception("Intentional failure.")

        with pytest.raises(Exception, match="Intentional failure."):
            count_and_fail()

        assert call_count == retries

    def test_value_error_bubbles_immediately(self):
        call_count = 0

        @backoff(delay=0.01, retries=5)
        def fail_with_value_error():
            nonlocal call_count
            call_count += 1
            raise ValueError("bad input")

        with pytest.raises(ValueError):
            fail_with_value_error()

        assert call_count == 1

    def test_delay_doubles_between_retries(self, monkeypatch):
        delays = []
        monkeypatch.setattr("src.backoff.sleep", lambda s: delays.append(s))

        @backoff(delay=1, retries=4)
        def always_fails():
            raise RuntimeError("nope")

        with pytest.raises(RuntimeError):
            always_fails()

        assert delays == [1, 2, 4]

    def test_succeeds_after_n_failures(self, monkeypatch):
        delays = []
        monkeypatch.setattr("src.backoff.sleep", lambda s: delays.append(s))

        call_count = 0
        succeed_on = 3

        @backoff(delay=1, retries=5)
        def flaky():
            nonlocal call_count
            call_count += 1
            if call_count < succeed_on:
                raise RuntimeError("temporary fail")
            return "OK"

        result = flaky()
        assert result == "OK"
        assert call_count == succeed_on
        assert delays == [1, 2]
