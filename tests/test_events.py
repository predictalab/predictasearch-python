from predictasearch import DoneEvent, FailedEvent, ProgressEvent, ResultEvent
from predictasearch.events import SourceErrorEvent, parse_event
from predictasearch.sse import ServerSentEvent


def _parse(event, data, id="3"):
    return parse_event(ServerSentEvent(event=event, data=data, id=id))


def test_each_event_is_typed():
    assert _parse("result", '{"network": "github", "data": [{"a": 1}]}') == (
        ResultEvent(id=3, network="github", data=[{"a": 1}])
    )
    assert _parse("source_error", '{"network": "forum", "reason": "timeout"}') == (
        SourceErrorEvent(id=3, network="forum", reason="timeout")
    )
    assert _parse(
        "progress", '{"done": 1, "total": 3, "found": 1, "failed": 0}'
    ) == ProgressEvent(id=3, done=1, total=3, found=1, failed=0)
    assert _parse(
        "done",
        '{"found": 1, "failed": 1, "credit_debited": true, "credit_balance": 4}',
    ) == DoneEvent(id=3, found=1, failed=1, credit_debited=True, credit_balance=4)
    assert _parse(
        "failed",
        '{"reason": "shutdown", "credit_refunded": true, "credit_balance": 5}',
    ) == FailedEvent(id=3, reason="shutdown", credit_refunded=True, credit_balance=5)


def test_an_unknown_event_is_skipped():
    assert _parse("new_kind", "{}") is None


def test_a_field_added_later_is_dropped():
    event = _parse("source_error", '{"network": "x", "reason": "y", "code": 7}')

    assert event == SourceErrorEvent(id=3, network="x", reason="y")
