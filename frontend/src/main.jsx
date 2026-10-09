import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { api } from "./api";
import "./styles.css";

const STATUSES = ["BOOKED", "CHECKED_IN", "COMPLETED", "CANCELLED"];
const LABEL = { BOOKED: "Booked", CHECKED_IN: "Checked in", COMPLETED: "Completed", CANCELLED: "Cancelled" };
const NEXT = { BOOKED: "CHECKED_IN", CHECKED_IN: "COMPLETED" };
const NEXT_LABEL = { BOOKED: "Check in", CHECKED_IN: "Complete" };

function formatSlot(iso) {
  const d = new Date(iso);
  return {
    day: d.toLocaleDateString("en-IN", { weekday: "short", day: "2-digit", month: "short" }),
    time: d.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" }),
  };
}

function StatCard({ label, value, tone }) {
  return (
    <div className={`stat ${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function BookingForm({ doctors, onClose, onBooked }) {
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  async function submit(event) {
    event.preventDefault();
    const form = new FormData(event.target);
    setSaving(true);
    setError("");
    try {
      await api.book({
        patient_name: form.get("patient_name"),
        patient_phone: form.get("patient_phone"),
        doctor_id: Number(form.get("doctor_id")),
        scheduled_at: new Date(form.get("scheduled_at")).toISOString(),
        reason: form.get("reason"),
      });
      onBooked();
    } catch (e) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="backdrop" onClick={onClose}>
      <form className="dialog" onSubmit={submit} onClick={(e) => e.stopPropagation()}>
        <header>
          <h2>Book an appointment</h2>
          <button type="button" className="ghost" onClick={onClose} aria-label="Close">×</button>
        </header>
        <label>Patient name<input name="patient_name" required minLength={2} placeholder="Full name" /></label>
        <label>Phone<input name="patient_phone" required placeholder="+91 98765 43210" /></label>
        <label>
          Doctor
          <select name="doctor_id" required>
            {doctors.map((d) => (
              <option key={d.id} value={d.id}>{d.name} · {d.specialty}</option>
            ))}
          </select>
        </label>
        <label>Date & time<input name="scheduled_at" type="datetime-local" required /></label>
        <label>Reason<textarea name="reason" rows={3} placeholder="Symptoms or purpose of visit" /></label>
        {error && <p className="form-error">{error}</p>}
        <button className="primary" disabled={saving}>{saving ? "Booking…" : "Confirm booking"}</button>
      </form>
    </div>
  );
}

function App() {
  const [appointments, setAppointments] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [stats, setStats] = useState({ total: 0, booked: 0, checkedIn: 0, completed: 0, cancelled: 0, doctors: 0 });
  const [filter, setFilter] = useState("ALL");
  const [doctorFilter, setDoctorFilter] = useState(0);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState("");

  async function load() {
    try {
      const [a, d, s] = await Promise.all([api.appointments(), api.doctors(), api.stats()]);
      setAppointments(a);
      setDoctors(d);
      setStats(s);
      setError("");
    } catch (e) {
      setError(e.message);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function advance(appt, status) {
    try {
      await api.setStatus(appt.id, status);
      load();
    } catch (e) {
      setError(e.message);
    }
  }

  const visible = useMemo(
    () =>
      appointments.filter(
        (a) => (filter === "ALL" || a.status === filter) && (!doctorFilter || a.doctor_id === doctorFilter)
      ),
    [appointments, filter, doctorFilter]
  );

  const loadByDoctor = useMemo(() => {
    const counts = {};
    appointments.filter((a) => a.status !== "CANCELLED").forEach((a) => (counts[a.doctor_id] = (counts[a.doctor_id] || 0) + 1));
    return counts;
  }, [appointments]);

  return (
    <div className="page">
      <header className="topbar">
        <div className="brand">
          <span className="logo">✚</span>
          <div>
            <b>ClinicFlow</b>
            <small>Appointment desk</small>
          </div>
        </div>
        <div className="desk-user">
          <span className="avatar">RR</span>
          <div>
            <b>Rohan Ranjan</b>
            <small>Front desk · 24BCS10428</small>
          </div>
        </div>
      </header>

      <main>
        <section className="intro">
          <div>
            <h1>Appointments</h1>
            <p>Book, check in and close out patient visits across all doctors.</p>
          </div>
          <button className="primary" onClick={() => setShowForm(true)}>+ Book appointment</button>
        </section>

        {error && <div className="banner">⚠ {error}</div>}

        <section className="stats">
          <StatCard label="All appointments" value={stats.total} tone="neutral" />
          <StatCard label="Booked" value={stats.booked} tone="blue" />
          <StatCard label="Checked in" value={stats.checkedIn} tone="amber" />
          <StatCard label="Completed" value={stats.completed} tone="green" />
          <StatCard label="Cancelled" value={stats.cancelled} tone="red" />
        </section>

        <section className="layout">
          <div className="card">
            <div className="card-head">
              <h2>Schedule</h2>
              <div className="tabs">
                {["ALL", ...STATUSES].map((s) => (
                  <button key={s} className={filter === s ? "on" : ""} onClick={() => setFilter(s)}>
                    {s === "ALL" ? "All" : LABEL[s]}
                  </button>
                ))}
              </div>
            </div>
            <table>
              <thead>
                <tr><th>When</th><th>Patient</th><th>Doctor</th><th>Reason</th><th>Status</th><th></th></tr>
              </thead>
              <tbody>
                {visible.map((a) => {
                  const slot = formatSlot(a.scheduled_at);
                  return (
                    <tr key={a.id}>
                      <td><b>{slot.time}</b><small>{slot.day}</small></td>
                      <td><b>{a.patient_name}</b><small>{a.patient_phone}</small></td>
                      <td><b>{a.doctor_name}</b><small>{a.specialty}</small></td>
                      <td className="reason">{a.reason || "—"}</td>
                      <td><span className={`pill ${a.status.toLowerCase()}`}>{LABEL[a.status]}</span></td>
                      <td className="actions">
                        {NEXT[a.status] && <button onClick={() => advance(a, NEXT[a.status])}>{NEXT_LABEL[a.status]}</button>}
                        {a.status === "BOOKED" && <button className="danger" onClick={() => advance(a, "CANCELLED")}>Cancel</button>}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            {!visible.length && <p className="empty">No appointments match this view.</p>}
          </div>

          <aside className="card doctors">
            <div className="card-head"><h2>Doctors on duty</h2></div>
            <button className={`doctor ${doctorFilter === 0 ? "on" : ""}`} onClick={() => setDoctorFilter(0)}>
              <span className="initials">★</span>
              <div><b>All doctors</b><small>{stats.doctors} on duty</small></div>
            </button>
            {doctors.map((d) => (
              <button key={d.id} className={`doctor ${doctorFilter === d.id ? "on" : ""}`} onClick={() => setDoctorFilter(d.id)}>
                <span className="initials">{d.name.replace("Dr. ", "").split(" ").map((p) => p[0]).join("")}</span>
                <div><b>{d.name}</b><small>{d.specialty} · Room {d.room}</small></div>
                <em>{loadByDoctor[d.id] || 0}</em>
              </button>
            ))}
          </aside>
        </section>
      </main>

      {showForm && (
        <BookingForm
          doctors={doctors}
          onClose={() => setShowForm(false)}
          onBooked={() => {
            setShowForm(false);
            load();
          }}
        />
      )}
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);
