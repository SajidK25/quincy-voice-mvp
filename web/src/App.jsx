import React, { useEffect, useMemo, useRef, useState } from "react";
import { createJob, getJob, downloadUrl } from "./api";

function StatusPill({ status }) {
  const label = status || "unknown";
  return <span className={`pill pill-${label}`}>{label}</span>;
}

export default function App() {
  const [file, setFile] = useState(null);
  const [jobId, setJobId] = useState("");
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const pollTimer = useRef(null);

  const canUpload = useMemo(() => !!file && !busy, [file, busy]);
  const ready = status === "ready";

  useEffect(() => {
    return () => {
      if (pollTimer.current) clearInterval(pollTimer.current);
    };
  }, []);

  async function startPolling(id) {
    if (pollTimer.current) clearInterval(pollTimer.current);

    pollTimer.current = setInterval(async () => {
      try {
        const data = await getJob(id);
        setStatus(data.status || "");
        if (data.error) setError(data.error);

        if (data.status === "ready" || data.status === "failed") {
          clearInterval(pollTimer.current);
          pollTimer.current = null;
          setBusy(false);
        }
      } catch (e) {
        setError(e.message);
      }
    }, 2500);
  }

  async function handleConvert() {
    setError("");
    setStatus("");
    setBusy(true);

    try {
      const { job_id } = await createJob(file);
      setJobId(job_id);
      setStatus("queued");
      await startPolling(job_id);
    } catch (e) {
      setBusy(false);
      setError(e.message);
    }
  }

  function reset() {
    setFile(null);
    setJobId("");
    setStatus("");
    setError("");
    setBusy(false);
    if (pollTimer.current) clearInterval(pollTimer.current);
    pollTimer.current = null;
  }

  return (
    <div className="page">
      <div className="card">
        <h1>Quincy Voice Converter</h1>
        <p className="sub">
          Upload a Suno song → RunPod splits + converts → download Quincy version.
        </p>

        <div className="section">
          <label className="label">Suno song file</label>
          <div className="row">
            <input
              type="file"
              accept="audio/*"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              disabled={busy}
            />
            <button className="secondary" onClick={reset} disabled={busy && !ready}>
              Reset
            </button>
          </div>

          {file && (
            <div className="meta">
              <div><strong>Name:</strong> {file.name}</div>
              <div><strong>Size:</strong> {(file.size / (1024 * 1024)).toFixed(2)} MB</div>
            </div>
          )}
        </div>

        <div className="section">
          <button className="primary" onClick={handleConvert} disabled={!canUpload}>
            {busy ? "Converting…" : "Convert to Quincy Voice"}
          </button>
        </div>

        {jobId && (
          <div className="section">
            <div className="row space">
              <div>
                <div className="label">Job</div>
                <div className="mono">{jobId}</div>
              </div>
              <div>
                <div className="label">Status</div>
                <StatusPill status={status} />
              </div>
            </div>

            {status && status !== "ready" && status !== "failed" && (
              <div className="hint">
                Pipeline: normalize → RunPod process → merge → ready.
              </div>
            )}

            {ready && (
              <div className="download">
                <a className="primary linkbtn" href={downloadUrl(jobId)}>
                  Download converted track (WAV)
                </a>
              </div>
            )}
          </div>
        )}

        {error && (
          <div className="error">
            <strong>Error:</strong> {error}
          </div>
        )}

        <div className="footer">
          <small>
            Tip: If Suno vocals are heavily processed, conversion can sound more synthetic.
          </small>
        </div>
      </div>
    </div>
  );
}
