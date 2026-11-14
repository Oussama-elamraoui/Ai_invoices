const API_URL = (
  import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1"
).replace(/\/$/, "");

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API_URL}${path}`, options);
  } catch {
    throw new Error("Could not reach the API. Is the backend running?");
  }

  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      message = body.detail || message;
    } catch {
      // Keep the HTTP status message when the server did not return JSON.
    }
    throw new Error(message);
  }

  return response.status === 204 ? null : response.json();
}

function jsonRequest(method, body) {
  return {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  };
}

export const api = {
  jobs: () => request("/jobs/?limit=50"),
  job: (id) => request(`/jobs/${id}`),
  drafts: (jobId) => request(`/invoice-drafts/job/${jobId}`),
  draft: (id) => request(`/invoice-drafts/${id}`),
  saveDraft: (id, body) => request(`/invoice-drafts/${id}`, jsonRequest("PATCH", body)),
  confirmDraft: (id, body) =>
    request(`/invoice-drafts/${id}/confirm`, jsonRequest("POST", body)),
  invoices: () => request("/invoices/?limit=50"),
  suppliers: (query = "") =>
    request(`/entities/suppliers?limit=100&query=${encodeURIComponent(query)}`),
  clients: (query = "") =>
    request(`/entities/clients?limit=100&query=${encodeURIComponent(query)}`),
  createSupplier: (body) =>
    request("/entities/suppliers", jsonRequest("POST", body)),
  createClient: (body) =>
    request("/entities/clients", jsonRequest("POST", body)),
  upload: (file) => {
    const body = new FormData();
    body.append("file", file);
    return request("/uploads/", { method: "POST", body });
  },
};
