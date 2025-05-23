from http import HTTPStatus
from fastapi.testclient import TestClient
import pytest

from api.controllers import model_controller


@pytest.fixture
def api_client():
    from fastapi import FastAPI

    app = FastAPI()

    app.include_router(model_controller.router)
    return TestClient(app)


def test_list_models(api_client):
    model_controller.mr.list_registered_models = lambda: ["modelo1", "modelo2"]
    response = api_client.get("/api/v1/model/list")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == ["modelo1", "modelo2"]


def test_predict(api_client):
    class FakeResult:
        def tolist(self):
            return [42, 43]

    model_controller.mr.predict = lambda model_name, version, data: FakeResult()
    payload = {"model_name": "modelo1", "model_version": 1, "data": [[1, 2, 3]]}
    response = api_client.post("/api/v1/model/predict", json=payload)
    assert response.status_code == HTTPStatus.OK
    assert response.json() == [42, 43]
