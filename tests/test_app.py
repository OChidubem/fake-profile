import pytest
import json
from app import app, generate_profile


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ── generate_profile unit tests ───────────────────────────────────────────────

class TestGenerateProfile:
    REQUIRED_KEYS = {
        "name", "email", "phone", "address", "city", "country",
        "date_of_birth", "job", "company", "username", "website",
        "bio", "gender", "avatar",
    }

    def test_returns_all_required_fields(self):
        profile = generate_profile()
        assert self.REQUIRED_KEYS.issubset(profile.keys())

    def test_name_is_non_empty_string(self):
        profile = generate_profile()
        assert isinstance(profile["name"], str)
        assert len(profile["name"]) > 0

    def test_email_contains_at_sign(self):
        profile = generate_profile()
        assert "@" in profile["email"]

    def test_gender_is_valid(self):
        profile = generate_profile()
        assert profile["gender"] in ("Male", "Female")

    def test_avatar_is_url(self):
        profile = generate_profile()
        assert profile["avatar"].startswith("https://")

    def test_multiple_profiles_are_unique(self):
        emails = {generate_profile()["email"] for _ in range(20)}
        # Very unlikely all 20 generated emails are the same
        assert len(emails) > 1


# ── Flask route tests ──────────────────────────────────────────────────────────

class TestIndexRoute:
    def test_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_returns_html(self, client):
        response = client.get("/")
        assert b"Fake Profile Generator" in response.data


class TestApiGenerateRoute:
    def test_default_returns_one_profile(self, client):
        response = client.get("/api/generate")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 1

    def test_count_param_returns_correct_number(self, client):
        for count in (1, 3, 5, 10):
            response = client.get(f"/api/generate?count={count}")
            data = json.loads(response.data)
            assert len(data) == count

    def test_count_clamped_to_max_10(self, client):
        response = client.get("/api/generate?count=99")
        data = json.loads(response.data)
        assert len(data) == 10

    def test_count_clamped_to_min_1(self, client):
        response = client.get("/api/generate?count=0")
        data = json.loads(response.data)
        assert len(data) == 1

    def test_profile_has_required_fields(self, client):
        response = client.get("/api/generate")
        profile = json.loads(response.data)[0]
        for key in ("name", "email", "phone", "gender", "job", "company"):
            assert key in profile

    def test_content_type_is_json(self, client):
        response = client.get("/api/generate")
        assert "application/json" in response.content_type
