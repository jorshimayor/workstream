import {
  Activity,
  BadgeCheck,
  Check,
  ChevronRight,
  ClipboardList,
  FileCheck2,
  KeyRound,
  Lock,
  Play,
  RefreshCcw,
  ShieldCheck,
  UserCog,
  Users
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";

import {
  Actor,
  ApiEvent,
  DemoConfig,
  DemoRecords,
  guidePayload,
  issueToken,
  projectPayload,
  submissionPayload,
  taskPayload
} from "./api";

const defaultConfig: DemoConfig = {
  issuer: "https://auth.flow.local/demo",
  audience: "workstream-demo",
  secret: "workstream-demo-local-secret"
};

type DemoStep = {
  key: string;
  label: string;
  detail: string;
  icon: typeof ClipboardList;
  run: () => Promise<void>;
};

function eventId() {
  return crypto.randomUUID();
}

function shortId(value?: string) {
  return value ? value.slice(0, 8) : "pending";
}

function statusTone(status?: string) {
  if (!status) return "muted";
  if (["active", "ready", "submitted"].includes(status)) return "good";
  if (["screening", "claimed", "in_progress"].includes(status)) return "info";
  return "muted";
}

export function App() {
  const [config, setConfig] = useState<DemoConfig>(defaultConfig);
  const [runId, setRunId] = useState(() => crypto.randomUUID().slice(0, 8));
  const [actors, setActors] = useState<Record<string, Actor>>({});
  const [records, setRecords] = useState<DemoRecords>({});
  const [events, setEvents] = useState<ApiEvent[]>([]);
  const [activeStep, setActiveStep] = useState<string | null>(null);
  const [selectedRecord, setSelectedRecord] = useState<keyof DemoRecords>("project");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function createActors() {
      const managerSubject = `demo-project-manager-${runId}`;
      const workerSubject = `demo-worker-${runId}`;
      const reviewerSubject = `demo-reviewer-${runId}`;
      const [managerToken, workerToken, reviewerToken] = await Promise.all([
        issueToken(config, managerSubject, ["project_manager"]),
        issueToken(config, workerSubject, ["worker"]),
        issueToken(config, reviewerSubject, ["reviewer"])
      ]);
      if (cancelled) return;
      setActors({
        manager: {
          label: "Project Manager",
          subject: managerSubject,
          roles: ["project_manager"],
          token: managerToken
        },
        worker: {
          label: "Worker",
          subject: workerSubject,
          roles: ["worker"],
          token: workerToken
        },
        reviewer: {
          label: "Reviewer",
          subject: reviewerSubject,
          roles: ["reviewer"],
          token: reviewerToken
        }
      });
    }
    createActors().catch((caught: unknown) => setError(String(caught)));
    return () => {
      cancelled = true;
    };
  }, [config, runId]);

  async function call<T>(
    label: string,
    method: string,
    path: string,
    actor?: Actor,
    body?: unknown,
    expectedStatus?: number
  ): Promise<T> {
    const response = await fetch(path, {
      method,
      headers: {
        ...(actor ? { Authorization: `Bearer ${actor.token}` } : {}),
        ...(body ? { "Content-Type": "application/json" } : {})
      },
      body: body ? JSON.stringify(body) : undefined
    });
    const contentType = response.headers.get("content-type") ?? "";
    const data = contentType.includes("application/json")
      ? await response.json()
      : await response.text();
    const ok = expectedStatus ? response.status === expectedStatus : response.ok;
    setEvents((current) => [
      {
        id: eventId(),
        at: new Date().toLocaleTimeString(),
        label,
        method,
        path,
        status: response.status,
        actor: actor?.label,
        ok
      },
      ...current
    ]);
    if (!ok) {
      throw new Error(`${label} returned ${response.status}: ${JSON.stringify(data)}`);
    }
    return data as T;
  }

  async function runStep(key: string, action: () => Promise<void>) {
    setError(null);
    setActiveStep(key);
    try {
      await action();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught));
    } finally {
      setActiveStep(null);
    }
  }

  const steps: DemoStep[] = useMemo(
    () => [
      {
        key: "health",
        label: "Verify API And Flow Tokens",
        detail: "Checks health, invalid token rejection, and manager actor context.",
        icon: ShieldCheck,
        run: async () => {
          await call("Health", "GET", "/api/v1/health");
          await call("Invalid token rejected", "GET", "/api/v1/auth/me", {
            label: "Invalid Token",
            subject: "bad-token",
            roles: ["worker"],
            token: "bad.token.value"
          }, undefined, 401);
          await call("Manager token accepted", "GET", "/api/v1/auth/me", actors.manager);
        }
      },
      {
        key: "project",
        label: "Create Project",
        detail: "Creates the project shell with base payment context.",
        icon: ClipboardList,
        run: async () => {
          const project = await call<any>(
            "Create project",
            "POST",
            "/api/v1/projects",
            actors.manager,
            projectPayload(runId),
            201
          );
          setRecords((current) => ({ ...current, project }));
          setSelectedRecord("project");
        }
      },
      {
        key: "guide",
        label: "Create And Activate Guide",
        detail: "Adds guide, checker, review, revision, and payment policy.",
        icon: FileCheck2,
        run: async () => {
          if (!records.project) throw new Error("Create a project first.");
          const guide = await call<any>(
            "Create guide",
            "POST",
            `/api/v1/projects/${records.project.id}/guides`,
            actors.manager,
            guidePayload(runId),
            201
          );
          const patched = await call<any>(
            "Patch guide",
            "PATCH",
            `/api/v1/projects/${records.project.id}/guides/${guide.id}`,
            actors.manager,
            { change_summary: "Patched from the Week 1 API demo before activation." }
          );
          const activeGuide = await call<any>(
            "Activate guide",
            "POST",
            `/api/v1/projects/${records.project.id}/guides/${guide.id}/activate`,
            actors.manager
          );
          setRecords((current) => ({ ...current, guide: patched, activeGuide }));
          setSelectedRecord("activeGuide");
        }
      },
      {
        key: "task",
        label: "Create And Release Task",
        detail: "Creates, screens, and releases a task into the ready queue.",
        icon: Activity,
        run: async () => {
          if (!records.project) throw new Error("Create a project first.");
          const task = await call<any>(
            "Create task",
            "POST",
            `/api/v1/projects/${records.project.id}/tasks`,
            actors.manager,
            taskPayload(runId),
            201
          );
          await call("Screen task", "POST", `/api/v1/tasks/${task.id}/screen`, actors.manager, {
            reason: "Week 1 API demo screening passed"
          });
          const released = await call<any>(
            "Release task",
            "POST",
            `/api/v1/tasks/${task.id}/release`,
            actors.manager,
            { reason: "Week 1 API demo release" }
          );
          setRecords((current) => ({ ...current, task: released }));
          setSelectedRecord("task");
        }
      },
      {
        key: "claim",
        label: "Worker Claims And Starts",
        detail: "Activates demo worker profile, claims the task, then starts work.",
        icon: Users,
        run: async () => {
          if (!records.task) throw new Error("Create and release a task first.");
          const workerProfile = await call<any>(
            "Activate worker profile",
            "POST",
            "/api/v1/demo/worker-profile",
            actors.worker,
            { skill_tags: ["stem", "proofs"] },
            201
          );
          const claimed = await call<any>(
            "Claim task",
            "POST",
            `/api/v1/tasks/${records.task.id}/claim`,
            actors.worker,
            { reason: "Week 1 API demo worker claim" }
          );
          const started = await call<any>(
            "Start task",
            "POST",
            `/api/v1/tasks/${records.task.id}/start`,
            actors.worker,
            { reason: "Week 1 API demo worker start" }
          );
          setRecords((current) => ({
            ...current,
            workerProfile,
            assignment: claimed.assignment,
            task: started
          }));
          setSelectedRecord("assignment");
        }
      },
      {
        key: "submit",
        label: "Submit Packet",
        detail: "Worker submits artifact hash manifest, evidence, and attestation.",
        icon: BadgeCheck,
        run: async () => {
          if (!records.task) throw new Error("Start a task first.");
          const submission = await call<any>(
            "Submit packet",
            "POST",
            `/api/v1/tasks/${records.task.id}/submissions`,
            actors.worker,
            submissionPayload(runId),
            201
          );
          setRecords((current) => ({ ...current, submission, task: { ...current.task, status: "submitted" } }));
          setSelectedRecord("submission");
        }
      },
      {
        key: "lock",
        label: "Lock Submission And Audit",
        detail: "Worker lock is denied; manager lock succeeds; audit events load.",
        icon: Lock,
        run: async () => {
          if (!records.task || !records.submission) throw new Error("Submit a packet first.");
          await call(
            "Worker lock denied",
            "POST",
            `/api/v1/submissions/${records.submission.id}/lock`,
            actors.worker,
            undefined,
            403
          );
          const lockedSubmission = await call<any>(
            "Manager lock accepted",
            "POST",
            `/api/v1/submissions/${records.submission.id}/lock`,
            actors.manager
          );
          const auditEvents = await call<any[]>(
            "Load audit events",
            "GET",
            `/api/v1/tasks/${records.task.id}/audit-events`,
            actors.manager
          );
          await call(
            "Reviewer blocked in Week 1",
            "GET",
            `/api/v1/tasks/${records.task.id}`,
            actors.reviewer,
            undefined,
            403
          );
          setRecords((current) => ({ ...current, lockedSubmission, auditEvents }));
          setSelectedRecord("auditEvents");
        }
      }
    ],
    [actors.manager, actors.reviewer, actors.worker, records, runId]
  );

  async function runAll() {
    await runStep("run-all", async () => {
      await call("Health", "GET", "/api/v1/health");
      await call("Invalid token rejected", "GET", "/api/v1/auth/me", {
        label: "Invalid Token",
        subject: "bad-token",
        roles: ["worker"],
        token: "bad.token.value"
      }, undefined, 401);
      await call("Manager token accepted", "GET", "/api/v1/auth/me", actors.manager);

      const project = await call<any>(
        "Create project",
        "POST",
        "/api/v1/projects",
        actors.manager,
        projectPayload(runId),
        201
      );
      setRecords((current) => ({ ...current, project }));

      const guide = await call<any>(
        "Create guide",
        "POST",
        `/api/v1/projects/${project.id}/guides`,
        actors.manager,
        guidePayload(runId),
        201
      );
      const patchedGuide = await call<any>(
        "Patch guide",
        "PATCH",
        `/api/v1/projects/${project.id}/guides/${guide.id}`,
        actors.manager,
        { change_summary: "Patched from the Week 1 API demo before activation." }
      );
      const activeGuide = await call<any>(
        "Activate guide",
        "POST",
        `/api/v1/projects/${project.id}/guides/${guide.id}/activate`,
        actors.manager
      );
      setRecords((current) => ({ ...current, guide: patchedGuide, activeGuide }));

      const task = await call<any>(
        "Create task",
        "POST",
        `/api/v1/projects/${project.id}/tasks`,
        actors.manager,
        taskPayload(runId),
        201
      );
      await call("Screen task", "POST", `/api/v1/tasks/${task.id}/screen`, actors.manager, {
        reason: "Week 1 API demo screening passed"
      });
      const releasedTask = await call<any>(
        "Release task",
        "POST",
        `/api/v1/tasks/${task.id}/release`,
        actors.manager,
        { reason: "Week 1 API demo release" }
      );
      setRecords((current) => ({ ...current, task: releasedTask }));

      const workerProfile = await call<any>(
        "Activate worker profile",
        "POST",
        "/api/v1/demo/worker-profile",
        actors.worker,
        { skill_tags: ["stem", "proofs"] },
        201
      );
      const claimed = await call<any>(
        "Claim task",
        "POST",
        `/api/v1/tasks/${task.id}/claim`,
        actors.worker,
        { reason: "Week 1 API demo worker claim" }
      );
      const startedTask = await call<any>(
        "Start task",
        "POST",
        `/api/v1/tasks/${task.id}/start`,
        actors.worker,
        { reason: "Week 1 API demo worker start" }
      );
      setRecords((current) => ({
        ...current,
        workerProfile,
        assignment: claimed.assignment,
        task: startedTask
      }));

      const submission = await call<any>(
        "Submit packet",
        "POST",
        `/api/v1/tasks/${task.id}/submissions`,
        actors.worker,
        submissionPayload(runId),
        201
      );
      setRecords((current) => ({
        ...current,
        submission,
        task: { ...startedTask, status: "submitted" }
      }));

      await call(
        "Worker lock denied",
        "POST",
        `/api/v1/submissions/${submission.id}/lock`,
        actors.worker,
        undefined,
        403
      );
      const lockedSubmission = await call<any>(
        "Manager lock accepted",
        "POST",
        `/api/v1/submissions/${submission.id}/lock`,
        actors.manager
      );
      const auditEvents = await call<any[]>(
        "Load audit events",
        "GET",
        `/api/v1/tasks/${task.id}/audit-events`,
        actors.manager
      );
      await call(
        "Reviewer blocked in Week 1",
        "GET",
        `/api/v1/tasks/${task.id}`,
        actors.reviewer,
        undefined,
        403
      );
      setRecords((current) => ({
        ...current,
        lockedSubmission,
        auditEvents
      }));
      setSelectedRecord("auditEvents");
    });
  }

  function resetDemo() {
    setRunId(crypto.randomUUID().slice(0, 8));
    setRecords({});
    setEvents([]);
    setError(null);
    setSelectedRecord("project");
  }

  const recordTabs: Array<[keyof DemoRecords, string]> = [
    ["project", "Project"],
    ["activeGuide", "Guide"],
    ["task", "Task"],
    ["assignment", "Assignment"],
    ["submission", "Submission"],
    ["lockedSubmission", "Locked"],
    ["auditEvents", "Audit"]
  ];

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand-block">
          <div className="brand-mark">W</div>
          <div>
            <h1>Workstream</h1>
            <p>Week 1 real API demo</p>
          </div>
        </div>

        <section className="panel compact">
          <div className="panel-title">
            <KeyRound size={16} />
            <span>Flow Auth Demo</span>
          </div>
          <label>
            Issuer
            <input
              value={config.issuer}
              onChange={(event) => setConfig({ ...config, issuer: event.target.value })}
            />
          </label>
          <label>
            Audience
            <input
              value={config.audience}
              onChange={(event) => setConfig({ ...config, audience: event.target.value })}
            />
          </label>
          <label>
            Local secret
            <input
              type="password"
              value={config.secret}
              onChange={(event) => setConfig({ ...config, secret: event.target.value })}
            />
          </label>
        </section>

        <section className="panel compact">
          <div className="panel-title">
            <UserCog size={16} />
            <span>Actors</span>
          </div>
          {Object.values(actors).map((actor) => (
            <div className="actor-row" key={actor.subject}>
              <span>{actor.label}</span>
              <code>{actor.roles.join(", ")}</code>
            </div>
          ))}
        </section>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <h2>Project Guide To Locked Submission</h2>
            <p>Run the Week 1 lifecycle through the backend APIs with real bearer tokens.</p>
          </div>
          <div className="actions">
            <button className="secondary" onClick={resetDemo} title="Reset demo run">
              <RefreshCcw size={16} />
              Reset
            </button>
            <button className="primary" onClick={() => void runAll()} disabled={activeStep !== null}>
              <Play size={16} />
              Run All
            </button>
          </div>
        </header>

        {error && <div className="error-banner">{error}</div>}

        <section className="metric-grid">
          <Metric label="Project" value={shortId(records.project?.id)} status={records.project?.status} />
          <Metric label="Guide" value={records.activeGuide?.guide?.version ?? "pending"} status={records.activeGuide?.guide?.status} />
          <Metric label="Task" value={records.task?.status ?? "pending"} status={records.task?.status} />
          <Metric label="Submission" value={records.lockedSubmission?.locked_at ? "locked" : records.submission?.status ?? "pending"} status={records.lockedSubmission?.locked_at ? "active" : records.submission?.status} />
        </section>

        <section className="content-grid">
          <div className="panel flow-panel">
            <div className="section-heading">
              <h3>Lifecycle</h3>
              <span>Run ID {runId}</span>
            </div>
            <div className="step-list">
              {steps.map((step) => {
                const Icon = step.icon;
                const isRunning = activeStep === step.key;
                return (
                  <div className="step-row" key={step.key}>
                    <div className={`step-icon ${isRunning ? "running" : ""}`}>
                      {isRunning ? <Activity size={17} /> : <Icon size={17} />}
                    </div>
                    <div className="step-copy">
                      <strong>{step.label}</strong>
                      <span>{step.detail}</span>
                    </div>
                    <button
                      className="icon-button"
                      onClick={() => void runStep(step.key, step.run)}
                      disabled={activeStep !== null}
                      title={`Run ${step.label}`}
                    >
                      <ChevronRight size={18} />
                    </button>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="panel record-panel">
            <div className="section-heading">
              <h3>Current Records</h3>
              <span>{selectedRecord}</span>
            </div>
            <div className="tab-row">
              {recordTabs.map(([key, label]) => (
                <button
                  key={key}
                  className={selectedRecord === key ? "active" : ""}
                  onClick={() => setSelectedRecord(key)}
                >
                  {label}
                </button>
              ))}
            </div>
            <pre>{JSON.stringify(records[selectedRecord] ?? {}, null, 2)}</pre>
          </div>

          <div className="panel event-panel">
            <div className="section-heading">
              <h3>API Events</h3>
              <span>{events.length} calls</span>
            </div>
            <div className="event-list">
              {events.length === 0 && <div className="empty-state">No API calls yet.</div>}
              {events.map((event) => (
                <div className="event-row" key={event.id}>
                  <div className={`event-status ${event.ok ? "ok" : "bad"}`}>
                    {event.ok ? <Check size={14} /> : event.status}
                  </div>
                  <div>
                    <strong>{event.label}</strong>
                    <span className="event-request">
                      <b>{event.method}</b>
                      <span>{event.path}</span>
                    </span>
                  </div>
                  <code>{event.actor ?? "public"}</code>
                </div>
              ))}
            </div>
          </div>
        </section>
      </section>
    </main>
  );
}

function Metric({
  label,
  value,
  status
}: {
  label: string;
  value: string;
  status?: string;
}) {
  return (
    <div className="metric-card">
      <span>{label}</span>
      <strong>{value}</strong>
      <em className={statusTone(status)}>{status ?? "not created"}</em>
    </div>
  );
}
