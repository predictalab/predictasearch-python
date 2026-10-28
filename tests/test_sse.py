from predictasearch.sse import ServerSentEvent, SSEDecoder


def _decode(text):
    decoder = SSEDecoder()
    return list(decoder.iter_events(text.split("\n"))), decoder


def test_events_with_id_name_and_data():
    events, _ = _decode('id: 0\nevent: progress\ndata: {"done": 1}\n\n')

    assert events == [ServerSentEvent(event="progress", data='{"done": 1}', id="0")]


def test_comments_and_retry_are_not_events():
    events, decoder = _decode(
        "retry: 3000\n\n: ping\n\nid: 1\nevent: done\ndata: {}\n\n"
    )

    assert [e.event for e in events] == ["done"]
    assert decoder.retry == 3000


def test_data_lines_are_joined():
    events, _ = _decode("data: a\ndata: b\n\n")

    assert events == [ServerSentEvent(event="message", data="a\nb")]


def test_an_unfinished_event_is_not_given():
    events, _ = _decode("id: 2\nevent: result\ndata: {}")

    assert events == []


def test_a_value_without_space_after_the_colon():
    events, _ = _decode("event:done\ndata:{}\n\n")

    assert events == [ServerSentEvent(event="done", data="{}")]
