from app.core.config import settings
from app.services.ai_advisor_service import AiAdvisorService


def test_driver_cannot_access_ai_advisor(client, driver_user):
    res = client.post(
        "/api/v1/ai/advisor",
        headers=driver_user["headers"],
        json={"question": "Karbon emisyonumuz neden yuksek?"},
    )
    assert res.status_code == 403


def test_admin_gets_503_when_api_key_missing(client, admin_user, monkeypatch):
    monkeypatch.setattr(settings, "GEMINI_API_KEY", None)

    res = client.post(
        "/api/v1/ai/advisor",
        headers=admin_user["headers"],
        json={"question": "Karbon emisyonumuz neden yuksek?"},
    )
    assert res.status_code == 503
    assert res.json()["detail"] == "Gemini API key is not configured."


def test_admin_can_ask_ai_advisor_with_mocked_gemini(client, admin_user, monkeypatch):
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "fake-test-key")

    async def fake_call_gemini(self, prompt):
        return "Bu bir test cevabidir."

    monkeypatch.setattr(AiAdvisorService, "_call_gemini", fake_call_gemini)

    res = client.post(
        "/api/v1/ai/advisor",
        headers=admin_user["headers"],
        json={"question": "Karbon emisyonumuz neden yuksek?"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["answer"] == "Bu bir test cevabidir."
    assert body["model"] == settings.GEMINI_MODEL
    assert body["context_used"] == {
        "dashboard": True,
        "alerts": True,
        "recommendations": True,
        "report": True,
    }
