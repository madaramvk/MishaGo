from unittest.mock import patch, MagicMock


def test_get_chat_history_empty(client):
    resp = client.get("/api/chat/history?context_type=general")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_get_chat_history_with_messages(client, db_session):
    from backend.models import ChatMessage
    db_session.add(ChatMessage(role="user", content="hello", context_type="general"))
    db_session.add(ChatMessage(role="gucci", content="hi there!", context_type="general"))
    db_session.commit()
    resp = client.get("/api/chat/history?context_type=general&limit=20")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 2
    assert data[0]["role"] == "user"


def test_get_goal_chat_history(client, db_session):
    from backend.models import ChatMessage, Goal, Direction
    d = Direction.query.first()
    g = Goal(title="Test", direction_id=d.id)
    db_session.add(g)
    db_session.flush()
    db_session.add(ChatMessage(role="user", content="help", context_type="goal", goal_id=g.id))
    db_session.commit()
    resp = client.get(f"/api/chat/history?context_type=goal&goal_id={g.id}")
    data = resp.get_json()
    assert len(data) == 1


def test_stream_chat_returns_sse_content_type(client, db_session):
    from backend.models import Setting
    db_session.add(Setting(key="api_key", value="test-key"))
    db_session.commit()

    mock_stream_cm = MagicMock()
    mock_stream_cm.__enter__ = MagicMock(return_value=mock_stream_cm)
    mock_stream_cm.__exit__ = MagicMock(return_value=False)
    mock_stream_cm.text_stream = iter(["Hello ", "friend!"])

    with patch("backend.routes.chat.anthropic") as mock_anthropic:
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client
        mock_client.messages.stream.return_value = mock_stream_cm
        resp = client.get("/api/chat/stream?message=hi")
        assert resp.content_type.startswith("text/event-stream")


def test_stream_chat_saves_user_message(client, db_session):
    from backend.models import Setting, ChatMessage
    db_session.add(Setting(key="api_key", value="test-key"))
    db_session.commit()

    mock_stream_cm = MagicMock()
    mock_stream_cm.__enter__ = MagicMock(return_value=mock_stream_cm)
    mock_stream_cm.__exit__ = MagicMock(return_value=False)
    mock_stream_cm.text_stream = iter(["ok"])

    with patch("backend.routes.chat.anthropic") as mock_anthropic:
        mock_client = MagicMock()
        mock_anthropic.Anthropic.return_value = mock_client
        mock_client.messages.stream.return_value = mock_stream_cm
        client.get("/api/chat/stream?message=test+message")
        msg = ChatMessage.query.filter_by(role="user").first()
        assert msg is not None
        assert msg.content == "test message"


def test_stream_chat_no_api_key(client):
    resp = client.get("/api/chat/stream?message=hi")
    assert resp.status_code == 400
