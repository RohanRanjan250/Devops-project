async function request(path, options = {}) {
  const response = await fetch(`/api${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    const detail = Array.isArray(body.detail) ? body.detail.map((d) => d.msg).join(", ") : body.detail;
    throw new Error(detail || `Request failed (${response.status})`);
  }
  return response.status === 204 ? null : response.json();
}

export const api = {
  doctors: () => request("/doctors"),
  appointments: () => request("/appointments"),
  stats: () => request("/appointments/stats"),
  book: (data) => request("/appointments", { method: "POST", body: JSON.stringify(data) }),
  setStatus: (id, status) => request(`/appointments/${id}`, { method: "PUT", body: JSON.stringify({ status }) }),
  remove: (id) => request(`/appointments/${id}`, { method: "DELETE" }),
};
