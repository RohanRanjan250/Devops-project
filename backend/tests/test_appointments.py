def test_book_appointment(client, booking):
    response = client.post("/api/appointments", json=booking)
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "BOOKED"
    assert body["doctor_name"] == "Dr. Test Physician"


def test_double_booking_same_slot_is_rejected(client, booking):
    assert client.post("/api/appointments", json=booking).status_code == 201
    clash = dict(booking, patient_name="Someone Else", patient_phone="9999999999")
    response = client.post("/api/appointments", json=clash)
    assert response.status_code == 409


def test_same_slot_different_doctor_is_allowed(client, booking):
    assert client.post("/api/appointments", json=booking).status_code == 201
    assert client.post("/api/appointments", json=dict(booking, doctor_id=2)).status_code == 201


def test_book_with_unknown_doctor_returns_404(client, booking):
    assert client.post("/api/appointments", json=dict(booking, doctor_id=99)).status_code == 404


def test_invalid_phone_is_rejected(client, booking):
    assert client.post("/api/appointments", json=dict(booking, patient_phone="abc")).status_code == 422


def test_update_status_and_filter(client, booking):
    appt = client.post("/api/appointments", json=booking).json()
    updated = client.put(f"/api/appointments/{appt['id']}", json={"status": "CHECKED_IN"})
    assert updated.json()["status"] == "CHECKED_IN"
    checked_in = client.get("/api/appointments", params={"status_filter": "checked_in"}).json()
    assert [a["id"] for a in checked_in] == [appt["id"]]


def test_invalid_status_is_rejected(client, booking):
    appt = client.post("/api/appointments", json=booking).json()
    assert client.put(f"/api/appointments/{appt['id']}", json={"status": "LOST"}).status_code == 422


def test_delete_appointment(client, booking):
    appt = client.post("/api/appointments", json=booking).json()
    assert client.delete(f"/api/appointments/{appt['id']}").status_code == 204
    assert client.get(f"/api/appointments/{appt['id']}").status_code == 404


def test_stats(client, booking):
    first = client.post("/api/appointments", json=booking).json()
    client.post("/api/appointments", json=dict(booking, doctor_id=2))
    client.put(f"/api/appointments/{first['id']}", json={"status": "COMPLETED"})
    stats = client.get("/api/appointments/stats").json()
    assert stats == {"total": 2, "booked": 1, "checkedIn": 0, "completed": 1, "cancelled": 0, "doctors": 2}
