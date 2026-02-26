const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const API_KEY = import.meta.env.VITE_API_KEY || "";

export async function createJob(file) {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${API_BASE}/jobs`, {
    method: "POST",
    headers: API_KEY ? { "X-API-Key": API_KEY } : {},
    body: form
  });

  if (!res.ok) {
    const txt = await res.text();
    throw new Error(`Create job failed: ${res.status} ${txt}`);
  }
  return res.json(); // { job_id }
}

export async function getJob(jobId) {
  const res = await fetch(`${API_BASE}/jobs/${jobId}`, {
    headers: API_KEY ? { "X-API-Key": API_KEY } : {}
  });

  if (!res.ok) {
    const txt = await res.text();
    throw new Error(`Get job failed: ${res.status} ${txt}`);
  }
  return res.json(); // { status, error? }
}

export function downloadUrl(jobId) {
  return `${API_BASE}/jobs/${jobId}/download`;
}
