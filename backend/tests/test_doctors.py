def test_list_doctors(client):
    doctors = client.get("/api/doctors").json()
    assert [d["specialty"] for d in doctors] == ["Cardiology", "General Medicine"]


def test_create_doctor(client):
    response = client.post("/api/doctors", json={"name": "Dr. New Joiner", "specialty": "Dermatology", "room": "9"})
    assert response.status_code == 201
    assert response.json()["id"] == 3


def test_create_doctor_validation(client):
    response = client.post("/api/doctors", json={"name": "X", "specialty": "Dermatology"})
    assert response.status_code == 422
