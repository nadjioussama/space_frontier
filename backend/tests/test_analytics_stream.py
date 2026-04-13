"""Tests for analytics.stream — Redis Streams buffer."""
import json
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_redis():
    with patch("apps.analytics.stream._redis") as r:
        yield r


class TestPush:
    def test_push_calls_xadd(self, mock_redis):
        from apps.analytics.stream import push, STREAM, MAXLEN

        record = {"event_type": "session.started", "player_id": "abc"}
        push(record)
        mock_redis.xadd.assert_called_once_with(
            STREAM, {"e": json.dumps(record)}, maxlen=MAXLEN, approximate=True,
        )

    def test_push_swallows_redis_errors(self, mock_redis):
        from apps.analytics.stream import push

        mock_redis.xadd.side_effect = ConnectionError("gone")
        push({"event_type": "x"})  # should not raise


class TestEnsureGroup:
    def test_creates_group(self, mock_redis):
        from apps.analytics.stream import ensure_group, STREAM, GROUP

        ensure_group()
        mock_redis.xgroup_create.assert_called_once_with(STREAM, GROUP, id="0", mkstream=True)

    def test_ignores_busygroup(self, mock_redis):
        from apps.analytics.stream import ensure_group

        mock_redis.xgroup_create.side_effect = Exception("BUSYGROUP")
        ensure_group()  # should not raise


class TestReadBatch:
    def test_parses_entries(self, mock_redis):
        from apps.analytics.stream import read_batch

        payload = {"event_type": "session.ended", "duration_seconds": 120}
        mock_redis.xreadgroup.return_value = [
            (b"stream", [(b"1-0", {b"e": json.dumps(payload).encode()})])
        ]
        result = read_batch(count=10, block_ms=100)
        assert len(result) == 1
        assert result[0][0] == b"1-0"
        assert result[0][1] == payload

    def test_malformed_entries_are_acked_and_skipped(self, mock_redis):
        from apps.analytics.stream import read_batch, STREAM, GROUP

        mock_redis.xreadgroup.return_value = [
            (b"stream", [(b"bad-1", {b"wrong_key": b"nope"})])
        ]
        result = read_batch()
        assert result == []
        mock_redis.xack.assert_called_once_with(STREAM, GROUP, b"bad-1")

    def test_empty_response(self, mock_redis):
        from apps.analytics.stream import read_batch

        mock_redis.xreadgroup.return_value = None
        assert read_batch() == []


class TestAck:
    def test_ack_with_ids(self, mock_redis):
        from apps.analytics.stream import ack, STREAM, GROUP

        ack([b"1-0", b"2-0"])
        mock_redis.xack.assert_called_once_with(STREAM, GROUP, b"1-0", b"2-0")

    def test_ack_empty_list_is_noop(self, mock_redis):
        from apps.analytics.stream import ack

        ack([])
        mock_redis.xack.assert_not_called()
