"use client";
import * as React from "react";

export default function UploadPage() {
  const [jobId, setJobId] = React.useState<string | null>(null);
  const [status, setStatus] = React.useState<any>(null);
  const [error, setError] = React.useState<string | null>(null);
  const [checking, setChecking] = React.useState(false);

  const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);
    setJobId(null);
    setStatus(null);
    const form = e.currentTarget;
    const input = form.querySelector<HTMLInputElement>("input[type=file]");
    if (!input || !input.files || input.files.length === 0) {
      setError("Please choose a CSV file");
      return;
    }
    const fd = new FormData();
    fd.append("file", input.files[0]);
    const res = await fetch(`${apiBase}/v1/transactions/csv`, { method: "POST", body: fd });
    if (!res.ok) {
      setError(`Upload failed (${res.status})`);
      return;
    }
    const data = await res.json();
    setJobId(data.job_id ?? null);
  }

  async function checkStatus() {
    if (!jobId) return;
    setChecking(true);
    try {
      const res = await fetch(`${apiBase}/v1/jobs/${jobId}`);
      const data = await res.json();
      setStatus(data);
    } catch (e: any) {
      setError(String(e));
    } finally {
      setChecking(false);
    }
  }

  return (
    <main style={{ padding: 24, maxWidth: 640 }}>
      <h1>Upload CSV</h1>
      <p style={{ color: "#666" }}>Week 2 – CSV ingestion (stub): enqueues a background job and shows status.</p>
      <form onSubmit={onSubmit} style={{ marginTop: 16 }}>
        <input type="file" name="file" accept=".csv,text/csv" />
        <button type="submit" style={{ marginLeft: 12 }}>Upload</button>
      </form>

      {error && <p style={{ color: "crimson" }}>Error: {error}</p>}

      {jobId && (
        <section style={{ marginTop: 16 }}>
          <div>Job ID: <code>{jobId}</code></div>
          <button onClick={checkStatus} disabled={checking} style={{ marginTop: 8 }}>
            {checking ? "Checking..." : "Check status"}
          </button>
          {status && (
            <pre style={{ background: "#f6f8fa", padding: 12, marginTop: 12 }}>
{JSON.stringify(status, null, 2)}
            </pre>
          )}
        </section>
      )}
    </main>
  );
}
