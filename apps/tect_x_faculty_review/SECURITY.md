# Security, privacy, and hosting boundaries

## Deployment status

This is a **local/offline-first prototype**, not a professionally security-audited SaaS service. The default application binds to **127.0.0.1**. Running it does not grant remote access to professors or other collaborators. No invitations, emails or profile claims are issued without an administrator action.

## Built-in controls

- PBKDF2-HMAC-SHA256 password hashes with random salts (450,000 iterations); passwords never included in exports.
- Unpredictable 36-byte URL-safe session tokens hashed at rest; HttpOnly, SameSite=Strict cookies with 12-hour sessions; secure-cookie mode for HTTPS deployments.
- One-time 36-byte invitation tokens hashed at rest and expired after a configurable 1–30 days; invitation URLs are sensitive secrets.
- CSRF token required for authenticated state-changing HTTP requests; role and assignment permission checks enforced on the server.
- Distinct independent reviewer approvals and human administrator adjudication; no self-review or self-adjudication.
- Review visibility blinded until the independent reviewer has submitted their own assessment.
- Pydantic length checks; user-supplied strings rendered as escaped text in the frontend.
- File download requires login; exports are administrator-only.
- Simple per-email/per-IP in-memory login throttling, suitable **only for a single local process**, not a distributed security perimeter.

## Limitations and mandatory controls before external faculty access

This app does **not** have federated university SSO, MFA, identity verification, legal privacy notices, production key management, revocation dashboards, backup/restore automation, high-availability storage, formal external penetration testing, email invitation delivery, or distributed rate limiting. Application audit events are not tamper-evident against a database administrator.

Before allowing access from outside localhost, at minimum:

1. Obtain explicit consent from the collaborator and confirm the person's identity through an independent channel. Never imply Professor Tao or any faculty member is involved without their affirmative agreement.
2. Deploy behind a maintained HTTPS reverse proxy with a trusted hostname and valid certificate; use `TECTX_HTTPS_ONLY=1`. Do not expose plain HTTP review sessions to the public internet. Configure secure firewall and access controls (VPN/institutional gateway recommended).
3. Use unique administrator passwords and private invitation links, institutional identity management/MFA if possible, and dedicated managed secrets. Do **not** commit SQLite databases, credentials, invitation tokens, personal correspondence or reviewer notes.
4. Add explicit academic-conflict-of-interest and independence disclosures before treating reviews as a journal-level peer review.
5. Establish encrypted backups, deletion/access/export policy, retention limits, and reviewer permission withdrawal. Tell participants where their data is hosted.
6. Conduct a qualified application security review before Internet exposure. For a production system, replace the demonstration identity stack with a maintained OIDC/SSO integration and move audit records into tamper-evident storage.
7. Verify source-grounded mathematical claims against the **original Word equations**, since plaintext excerpts can omit native OMML equations.

### Network bind safeguard

The local CLI refuses `--host 0.0.0.0` unless `TECTX_HTTPS_ONLY=1` is set; this only toggles the secure cookie bit. **It does not provide TLS itself**. The reverse proxy and domain configuration must be independently implemented and tested.

## Evidence and editorial boundaries

- Editorial status `teaching_approved` is **not** `theorem_proved` or journal-certified peer review.
- The Riemann hypothesis, Birch–Swinnerton-Dyer, and infinite 2-Selmer theorem remain outside the platform's certification authority.
- Exported review notes are not guaranteed anonymous. A reviewer may include their own name, institutions, details of unpublished mathematics, or identifiers in free-text fields.
- The user-supplied source DOCX is bundled for invited reviewer access; do not grant access to anyone without permission.
