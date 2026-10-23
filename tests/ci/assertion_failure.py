"""Explicit CI failure probe; excluded from ordinary fixture-test discovery."""


def test_intentional_failure():
    assert False, "Controlled assertion failure: this CI run must fail."
