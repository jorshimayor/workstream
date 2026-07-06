export type Role = "project_manager" | "worker" | "reviewer";

export type DemoConfig = {
  issuer: string;
  audience: string;
  secret: string;
};

export type Actor = {
  label: string;
  subject: string;
  roles: Role[];
  token: string;
};

export type ApiEvent = {
  id: string;
  at: string;
  label: string;
  method: string;
  path: string;
  status: number;
  actor?: string;
  ok: boolean;
};

export type DemoRecords = {
  project?: any;
  guide?: any;
  activeGuide?: any;
  task?: any;
  assignment?: any;
  workerProfile?: any;
  submission?: any;
  lockedSubmission?: any;
  auditEvents?: any[];
};

const encoder = new TextEncoder();

function base64Url(input: string | ArrayBuffer): string {
  const bytes = typeof input === "string" ? encoder.encode(input) : new Uint8Array(input);
  let binary = "";
  bytes.forEach((byte) => {
    binary += String.fromCharCode(byte);
  });
  return btoa(binary).replaceAll("+", "-").replaceAll("/", "_").replaceAll("=", "");
}

export async function issueToken(
  config: DemoConfig,
  subject: string,
  roles: Role[]
): Promise<string> {
  const now = Math.floor(Date.now() / 1000);
  const header = base64Url(JSON.stringify({ alg: "HS256", typ: "JWT" }));
  const payload = base64Url(
    JSON.stringify({
      iss: config.issuer,
      aud: config.audience,
      sub: subject,
      email: `${subject}@flow.local`,
      name: subject
        .split("-")
        .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
        .join(" "),
      roles,
      iat: now,
      nbf: now - 5,
      exp: now + 60 * 60
    })
  );
  const key = await crypto.subtle.importKey(
    "raw",
    encoder.encode(config.secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );
  const signature = await crypto.subtle.sign("HMAC", key, encoder.encode(`${header}.${payload}`));
  return `${header}.${payload}.${base64Url(signature)}`;
}

export function authHeaders(token?: string): HeadersInit {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function apiRequest<T>(
  method: string,
  path: string,
  token?: string,
  body?: unknown
): Promise<{ data: T; status: number }> {
  const response = await fetch(path, {
    method,
    headers: {
      ...authHeaders(token),
      ...(body ? { "Content-Type": "application/json" } : {})
    },
    body: body ? JSON.stringify(body) : undefined
  });
  const contentType = response.headers.get("content-type") ?? "";
  const data = contentType.includes("application/json")
    ? await response.json()
    : await response.text();
  if (!response.ok) {
    throw Object.assign(new Error(`${method} ${path} failed with ${response.status}`), {
      status: response.status,
      data
    });
  }
  return { data: data as T, status: response.status };
}

export function projectPayload(runId: string) {
  return {
    name: `Week 1 Demo ${runId}`,
    slug: `week1-demo-${runId}`,
    description: "Team demo project running the Week 1 Workstream lifecycle."
  };
}

export function guidePayload(runId: string) {
  return {
    version: "v1",
    content_markdown: `# Demo Project Guide ${runId}

Complete the task and submit verifiable evidence. A valid submission includes a
summary, an artifact manifest, an artifact package reference, and evidence that
can be checked against the locked project policy.

Reviewers check guide compliance, artifact hashes, evidence quality, and whether
the output satisfies the task acceptance criteria.`,
    change_summary: "Initial demo guide",
    post_submit_checker_policy: {
      required_checkers: ["check_policy_context_present", "check_required_files"],
      warning_checkers: [],
      blocking_severities: ["high"]
    },
    review_policy: {
      requires_second_review: false,
      allowed_decisions: ["accept", "needs_revision", "reject"],
      minimum_finding_fields: ["issue", "required_fix"],
      sla_hours: 24
    },
    revision_policy: {
      max_revision_rounds: 7,
      revision_deadline_hours: 48,
      auto_reject_after_limit: true,
      allowed_resubmission_states: ["needs_revision"],
      reviewer_reassignment_rule: "same reviewer preferred"
    },
    payment_policy: {
      base_amount: "25.00",
      currency: "USD",
      payout_type: "fixed",
      revision_payment_rule: "none",
      rejection_payment_rule: "none",
      accepted_payment_rule: "pay base amount"
    }
  };
}

export function taskPayload(runId: string) {
  return {
    title: `Demo task ${runId}`,
    description: "Evaluate the supplied proof and return evidence-backed output.",
    task_type: "evaluation",
    difficulty: "medium",
    skill_tags: ["stem", "proofs"],
    estimated_time_minutes: 45,
    source_type: "manual",
    source_ref: `demo-${runId}`,
    source_payload_hash: `sha256:source-${runId}`,
    acceptance_criteria: "The submission packet is complete and evidence-backed.",
    rejection_criteria: "Evidence is missing or unverifiable."
  };
}

export function submissionPayload(runId: string) {
  return {
    summary: "Completed the demo task with artifact hash and evidence.",
    package_uri: `local://packages/token=build-${runId}.tar.zst`,
    package_hash: `sha256:package-${runId}`,
    artifact_hash_manifest: [
      {
        artifact: "answer.md",
        hash: `sha256:answer-${runId}`,
        size_bytes: 128,
        notes: "primary answer artifact"
      }
    ],
    worker_attestation: "I confirm this packet follows the locked project guide.",
    evidence_items: [
      {
        type: "log",
        label: "checker dry run",
        uri: `s3://workstream-demo/reports/user@team-${runId}.log`,
        hash: `sha256:evidence-${runId}`,
        size_bytes: 256,
        metadata: { command: "workstream-demo" }
      }
    ]
  };
}
