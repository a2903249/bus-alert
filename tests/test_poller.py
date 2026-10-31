from app.services.poller import should_notify


def test_within_threshold():
    assert should_notify({"StopStatus": 0, "EstimateTime": 290}, 5) is True


def test_exactly_threshold():
    assert should_notify({"StopStatus": 0, "EstimateTime": 300}, 5) is True


def test_too_far():
    assert should_notify({"StopStatus": 0, "EstimateTime": 301}, 5) is False


def test_no_estimate():
    assert should_notify({"StopStatus": 0}, 5) is False


def test_bad_status():
    assert should_notify({"StopStatus": 1, "EstimateTime": 100}, 5) is False