# TECT-X Faculty Review Hub

**A standalone human-in-the-loop application for the ResearchOS / TECT-X curriculum.**

This is an **invitation-only academic collaboration prototype**, seeded directly from the supplied `ResearchOS_TECT_X_Standalone_Zeta_TDA_Curriculum.docx` (the original Word document is included under `source/`). It is designed so that independent experts, including professors **if they choose to participate**, can critique lessons, propose corrections and examine the evidence behind mathematical claims. It does **not** claim any professor has joined, endorsed, reviewed or been contacted by this project.


## What's inside

- **Review workspace:** all twelve teaching sessions and two research-integrity audit records extracted from the curriculum DOCX, with traceable source headings and a download of the unmodified original Word file.
- **Secure invitation flow:** admin-generated one-time invitation links, hashed tokens and expiration. No automated emails or identity assertions.
- **Human-in-the-loop review:** admins assign reviewers; each expert submits an independent verdict, evidence and limitations. Feedback is blinded until the reviewer has filed their own assessment.
- **Editorial gate:** two **different** positive reviewers are required before an administrator can approve a lesson **for teaching use only**. Authors cannot review their own proposals, and authors cannot adjudicate them.
- **Revision workflow:** approved or returned items can be revised into a new numbered round. Earlier review rounds remain in the SQLite audit trail.
- **Research proposals:** invited reviewers can submit new curricular, computational or mathematical items for review without claiming that unresolved mathematics has been proved.
- **Audit export:** administrator can export a JSON record of claims, verdicts, decisions and events, without exporting password hashes, session tokens or invitation tokens. Free-text comments still need privacy review before external sharing.
- **Originality boundary:** the Riemann hypothesis, BSD and Selmer-infinitude theorem are **never** marked solved by this platform.

## Install and run locally

You need Python **3.11 or later** and the two packages listed in `requirements.txt`.

```bash
cd tectx_professor_review_app
python -m pip install -r requirements.txt
python app.py init --email YOUR_EMAIL --name "Curriculum administrator"
# Enter a unique password of 12 or more characters when prompted.
python app.py serve
```

Visit **http://127.0.0.1:8765** and sign in. The database is created automatically at `data/review.sqlite3`; this is private local application state and is not included in the distributed ZIP.

### How expert participation works

1. The administrator signs in, opens **Reviewer roster → Generate private invitation**, and creates a link bound to the intended expert's email.
2. The administrator shares the link **privately and manually** after inviting the person through ordinary professional communication. The software does not contact Professor Tao or anyone else automatically. A displayed name does not verify academic credentials.
3. The expert accepts the single-use link, creates a password and signs in.
4. The administrator opens a teaching/research item and assigns at least two independently participating reviewers.
5. Reviewers submit evidence-backed **Approve for teaching / Request revisions / Reject teaching** reports. A reviewer cannot see others' report text before submitting their own.
6. Two different positive assessments move the item to **Awaiting decision**. Only a human administrator can **approve for teaching use**. If any reviewer requests revision, the author/admin can submit a new round that preserves prior reviews.
7. Administrators can export a JSON audit record, with a warning that free-text might contain identifying information.

### Safe invitation template

> Subject: Optional independent review of ResearchOS TECT-X curriculum
>
> I am inviting you, if interested and available, to review the attached six-week AI, zeta-function and topological-data-analysis curriculum through a private human-review workspace. It supports independent written feedback, correction requests and explicit evidence limitations. Participation is optional; no affiliation or endorsement is implied. The portal does not claim a proof of RH or BSD. If you choose to participate, I can send you a single-use reviewer invitation.

Do **not** state that Professor Terence Tao or any other professor is collaborating unless they explicitly agree.

## Verification

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q tests/test_workflow.py
```

The tests exercise authentication, CSRF, single-use invitations, independent-review gating, forbidden self-review, editing/revisions, editorial decisions, privacy boundaries and audit export.

## Project structure

```text
tectx_professor_review_app/
  app.py                    # FastAPI + SQLite business logic and security checks
  static/index.html         # Responsive UI shell
  static/app.js             # Reviewer workspace interface, forms and actions
  static/style.css          # Responsive styling
  data/seed_claims.json     # Source-grounded curriculum teaching/audit items
  source/*.docx             # Original user-provided curriculum (incl. Word equations)
  tests/test_workflow.py    # End-to-end human-review regression tests
  requirements.txt          # FastAPI + Uvicorn
  SECURITY.md               # Deployment and privacy limitations
  README.md
```

## Data and mathematical integrity

**Source:** review cards are extracted from the named `ResearchOS TECT-X Standalone Zeta TDA Curriculum.docx`. Word's native equation objects do not always survive plain-text extraction, so excerpts are **not authoritative** for formulas; reviewers must consult the bundled DOCX. The source file is unchanged.

The curriculum's six-week scope, twelve sessions, sequence, statistical-inference caveats and video attribution are preserved. A reviewer approval certifies **only that the human reviewer considers the item suitable for teaching**, not that any mathematical theorem has received peer review or been proved. Two teaching approvals do not confer scientific novelty.

**Motivating video:** Superintelligence, [*AI & Math: Solving Riemann Hypothesis by Brute Force? #shorts*](https://www.youtube.com/watch?v=M7eQUHH-oWI), March 21, 2026. Referenced from the screenshot-visible description; no full transcript was reviewed, redistributed or implied.

## Availability and limitations

This app runs **locally by default**. GitHub PR source code and a downloadable ZIP are not a hosted service. For professors in other institutions to use it remotely, **the owner must deploy it to a trusted HTTPS server, validate identity, obtain consent, configure backups and review security and data-retention policies**. See [SECURITY.md](SECURITY.md). It is not appropriate to publish a raw HTTP server or confidential reviews on the open internet.

The SQLite event log is append-only **at the application level**, not cryptographically immutable or equivalent to a formally certified academic peer-review record. Reviewer identity is invitation-linked, not institutionally verified. The app does not email, schedule, or contact external parties.

**Status:** Usable locally as a collaboration MVP; **not production-hosted and not proof-certified**.