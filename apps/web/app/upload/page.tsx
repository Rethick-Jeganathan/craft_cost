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
    <div className="mx-auto max-w-2xl space-y-4">
      <h1 className="text-xl font-semibold text-white/90">Upload CSV</h1>
      <p className="text-sm text-[var(--muted)]">Week 2 – CSV ingestion (stub): enqueues a background job and shows status.</p>

      <form onSubmit={onSubmit} className="rounded-lg border border-[var(--border)]/60 bg-[var(--surface)]/60 p-4 space-y-3">
        <input
          className="block w-full text-sm text-[var(--muted)] file:mr-4 file:rounded-md file:border-0 file:bg-brand-600/10 file:px-3 file:py-2 file:text-sm file:font-medium file:text-white hover:file:bg-brand-600/20"
          type="file"
          name="file"
          accept=".csv,text/csv"
        />
        <button
          type="submit"
          className="inline-flex items-center rounded-md bg-brand-600 px-3 py-2 text-sm font-medium text-white hover:bg-brand-700"
        >
          Upload
        </button>
      </form>

      {error && <p className="text-sm text-red-400">Error: {error}</p>}

      {jobId && (
        <section className="rounded-lg border border-[var(--border)]/60 bg-[var(--surface)]/60 p-4 space-y-2">
          <div className="text-sm">Job ID: <code className="text-[var(--muted)]">{jobId}</code></div>
          <button
            onClick={checkStatus}
            disabled={checking}
            className="inline-flex items-center rounded-md border border-[var(--border)]/60 bg-transparent px-3 py-2 text-sm text-white hover:border-brand-600/50 disabled:opacity-50"
          >
            {checking ? "Checking..." : "Check status"}
          </button>
          {status && (
            <pre className="mt-2 overflow-auto rounded-md border border-[var(--border)]/60 bg-black/30 p-3 text-xs">
{JSON.stringify(status, null, 2)}
            </pre>
          )}
        </section>
      )}
    </div>
  );
}
