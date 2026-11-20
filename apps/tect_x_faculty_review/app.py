"""ResearchOS / TECT-X: invitation-only, human-in-the-loop curriculum review.

This is a locally runnable collaboration prototype, not a production-hardened
internet service or a mathematical proof validator. It NEVER certifies RH,
BSD, or a new Selmer theorem. All editorial approvals are for TEACHING USE ONLY.

Quick start:
    python -m pip install -r requirements.txt
    python app.py init --email you@example.org
    python app.py serve
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import secrets
import sqlite3
import sys
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Annotated, Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent
DEFAULT_DB = ROOT / "data" / "review.sqlite3"
DEFAULT_SEED = ROOT / "data" / "seed_claims.json"
SOURCE_DOCX = ROOT / "source" / "ResearchOS_TECT_X_Standalone_Zeta_TDA_Curriculum.docx"
PASSWORD_ITERATIONS = 450_000
SESSION_LIFETIME_SECONDS = 12 * 3600
MAX_FEEDBACK = 5000
SCIENTIFIC_DISCLAIMER = (
    "Peer review in this app is editorial review for curriculum use, NOT "
    "certification of any unsolved mathematical theorem."
)


def now() -> int:
    return int(time.time())


def fingerprint(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def hash_password(password: str) -> str:
    if len(password) < 12:
        raise ValueError("Password must contain at least 12 characters")
    salt = secrets.token_bytes(16)
    dig = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PASSWORD_ITERATIONS)
    return f"pbkdf2_sha256${PASSWORD_ITERATIONS}${salt.hex()}${dig.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        typ, count, salt_hex, actual = stored.split("$")
        if typ != "pbkdf2_sha256" or int(count) < 100_000:
            return False
        dig = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), int(count))
        return hmac.compare_digest(dig, bytes.fromhex(actual))
    except (ValueError, TypeError):
        return False


def email_normalize(email: str) -> str:
    email = email.strip().lower()
    if not re.fullmatch(r"[^\s@]{1,120}@[^\s@]{1,200}\.[^\s@]{2,40}", email):
        raise ValueError("Enter a valid email address")
    return email


def db_connect(path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(str(path), timeout=20, isolation_level=None)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    con.execute("PRAGMA busy_timeout=20000")
    return con


@contextmanager
def read_db(path: Path):
    con = db_connect(path)
    try:
        yield con
    finally:
        con.close()


@contextmanager
def write_db(path: Path):
    con = db_connect(path)
    try:
        con.execute("BEGIN IMMEDIATE")
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def log_event(con: sqlite3.Connection, actor: int | None, action: str, claim: str | None, details: dict) -> None:
    con.execute("INSERT INTO events(actor_id,action,claim_id,details_json,created_at) VALUES(?,?,?,?,?)",
                (actor, action, claim, json.dumps(details, ensure_ascii=False, sort_keys=True), now()))


def init_db(path: Path = DEFAULT_DB, seed_path: Path = DEFAULT_SEED) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with write_db(path) as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY, email TEXT NOT NULL UNIQUE,
            display_name TEXT NOT NULL, role TEXT NOT NULL CHECK(role IN ('admin','reviewer','editor')),
            password_hash TEXT NOT NULL, created_at INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS invitations (
            id INTEGER PRIMARY KEY, email TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('reviewer','editor')),
            token_hash TEXT NOT NULL UNIQUE, expires_at INTEGER NOT NULL,
            used_at INTEGER, issued_by INTEGER NOT NULL REFERENCES users(id),
            created_at INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS sessions (
            token_hash TEXT PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id),
            csrf_token TEXT NOT NULL, expires_at INTEGER NOT NULL,
            created_at INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS claims (
            id TEXT PRIMARY KEY, title TEXT NOT NULL, category TEXT NOT NULL,
            week TEXT NOT NULL, goal TEXT NOT NULL, body TEXT NOT NULL,
            source_section TEXT NOT NULL, proof_scope TEXT NOT NULL,
            evidence_url TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL CHECK(status IN
              ('open_for_review','in_review','revision_requested','ready_for_adjudication','teaching_approved')),
            round INTEGER NOT NULL DEFAULT 1,
            author_id INTEGER REFERENCES users(id),
            created_at INTEGER NOT NULL, updated_at INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS assignments (
            id INTEGER PRIMARY KEY, claim_id TEXT NOT NULL REFERENCES claims(id),
            reviewer_id INTEGER NOT NULL REFERENCES users(id),
            assigned_by INTEGER NOT NULL REFERENCES users(id),
            created_at INTEGER NOT NULL, UNIQUE(claim_id,reviewer_id)
        );
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY, claim_id TEXT NOT NULL REFERENCES claims(id),
            reviewer_id INTEGER NOT NULL REFERENCES users(id),
            round INTEGER NOT NULL, verdict TEXT NOT NULL CHECK(verdict IN
                ('approve_teaching','request_revision','reject_teaching')),
            evidence TEXT NOT NULL, limitations TEXT NOT NULL,
            submitted_at INTEGER NOT NULL, UNIQUE(claim_id,reviewer_id,round)
        );
        CREATE TABLE IF NOT EXISTS decisions (
            id INTEGER PRIMARY KEY, claim_id TEXT NOT NULL REFERENCES claims(id),
            adjudicator_id INTEGER NOT NULL REFERENCES users(id),
            round INTEGER NOT NULL,
            decision TEXT NOT NULL CHECK(decision IN ('approve_teaching','return_for_revision')),
            rationale TEXT NOT NULL, decided_at INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY, actor_id INTEGER REFERENCES users(id),
            action TEXT NOT NULL, claim_id TEXT, details_json TEXT NOT NULL,
            created_at INTEGER NOT NULL
        );
        """)
        exists = con.execute("SELECT COUNT(*) AS c FROM claims").fetchone()["c"]
        if not exists:
            data = json.loads(seed_path.read_text(encoding="utf-8"))
            for cl in data["claims"]:
                con.execute("""INSERT INTO claims
                (id,title,category,week,goal,body,source_section,proof_scope,evidence_url,status,round,created_at,updated_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,1,?,?)""",
                (cl["id"], cl["title"], cl["category"], cl["week"], cl["goal"],
                 cl["body"], cl["source_section"], cl["proof_scope"],
                 cl.get("evidence_url", ""), "open_for_review", now(), now()))
            log_event(con, None, "CURRICULUM_IMPORTED", None,
                      {"claim_count": len(data["claims"]), "source": data["source_filename"]})


def create_user(db_path: Path, email: str, display_name: str, password: str, role: str = "admin") -> int:
    if role not in ("admin", "reviewer", "editor"):
        raise ValueError("Unknown role")
    email = email_normalize(email)
    pw = hash_password(password)
    if not (2 <= len(display_name.strip()) <= 110):
        raise ValueError("Name must be 2–110 characters")
    with write_db(db_path) as con:
        cur = con.execute("INSERT INTO users(email,display_name,role,password_hash,created_at) VALUES(?,?,?,?,?)",
                          (email, display_name.strip(), role, pw, now()))
        user_id = cur.lastrowid
        log_event(con, user_id, "USER_CREATED", None, {"role": role})
        return user_id


class LoginBody(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=512)


class InviteBody(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    role: Literal["reviewer", "editor"] = "reviewer"
    days: int = Field(default=7, ge=1, le=30)


class JoinBody(BaseModel):
    token: str = Field(min_length=25, max_length=200)
    name: str = Field(min_length=2, max_length=110)
    password: str = Field(min_length=12, max_length=512)
    consent_to_review: bool = False


class ProposalBody(BaseModel):
    title: str = Field(min_length=12, max_length=160)
    category: Literal["lesson", "mathematical_identity", "research_gap", "experiment"]
    goal: str = Field(min_length=20, max_length=1000)
    body: str = Field(min_length=40, max_length=6000)
    evidence_url: str = Field(default="", max_length=1000)


class AssignmentBody(BaseModel):
    claim_id: str
    reviewer_id: int


class ReviewBody(BaseModel):
    claim_id: str
    verdict: Literal["approve_teaching", "request_revision", "reject_teaching"]
    evidence: str = Field(min_length=20, max_length=MAX_FEEDBACK)
    limitations: str = Field(min_length=12, max_length=MAX_FEEDBACK)


class RevisionBody(BaseModel):
    claim_id: str
    goal: str = Field(min_length=10, max_length=1000)
    body: str = Field(min_length=35, max_length=6000)
    evidence_url: str = Field(default="", max_length=1000)
    rationale: str = Field(min_length=15, max_length=2000)


class DecisionBody(BaseModel):
    claim_id: str
    decision: Literal["approve_teaching", "return_for_revision"]
    rationale: str = Field(min_length=20, max_length=MAX_FEEDBACK)


def create_app(db_path: Path = DEFAULT_DB, seed_path: Path = DEFAULT_SEED,
               source_docx: Path = SOURCE_DOCX) -> FastAPI:
    init_db(db_path, seed_path)
    app = FastAPI(title="ResearchOS TECT-X | Professor Review Portal", version="1.0.0",
                  docs_url=None, redoc_url=None, openapi_url=None)
    app.state.db_path = db_path
    app.state.source_docx = source_docx
    secure_cookie = os.environ.get("TECTX_HTTPS_ONLY") == "1"
    app.state.secure_cookie = secure_cookie
    app.state.failed_logins = {}
    # Resist malicious Host headers; deployments must explicitly allow their own domain.
    extra_hosts = [x.strip() for x in os.environ.get("TECTX_ALLOWED_HOSTS", "").split(",") if x.strip()]
    app.add_middleware(TrustedHostMiddleware,
                       allowed_hosts=["127.0.0.1", "localhost", "testserver", *extra_hosts],
                       www_redirect=False)

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; connect-src 'self'; form-action 'self'; "
            "object-src 'none'; frame-ancestors 'none'; base-uri 'self'"
        )
        return response

    app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")

    def find_actor(request: Request, required: bool = True) -> dict | None:
        session_token = request.cookies.get("tectx_session")
        if not session_token:
            if required:
                raise HTTPException(401, "Please sign in")
            return None
        with read_db(db_path) as con:
            row = con.execute("""SELECT u.id,u.email,u.display_name,u.role,s.csrf_token,s.expires_at
                FROM sessions s JOIN users u ON s.user_id=u.id
                WHERE s.token_hash=?""", (fingerprint(session_token),)).fetchone()
        if not row or row["expires_at"] <= now():
            if required:
                raise HTTPException(401, "Session expired — sign in again")
            return None
        return dict(row)

    def require_actor(request: Request, roles: tuple[str, ...] | None = None, mutating: bool = False) -> dict:
        actor = find_actor(request)
        if roles and actor["role"] not in roles:
            raise HTTPException(403, "You do not have permission for this action")
        if mutating and not hmac.compare_digest(request.headers.get("x-csrf-token", ""), actor["csrf_token"]):
            raise HTTPException(403, "Missing or incorrect CSRF token")
        return actor

    def create_session(con: sqlite3.Connection, user_id: int) -> tuple[str, str]:
        raw_session = secrets.token_urlsafe(36)
        csrf = secrets.token_urlsafe(32)
        con.execute("INSERT INTO sessions(token_hash,user_id,csrf_token,expires_at,created_at) VALUES(?,?,?,?,?)",
                    (fingerprint(raw_session), user_id, csrf, now() + SESSION_LIFETIME_SECONDS, now()))
        return raw_session, csrf

    def cookie(response: JSONResponse, raw_session: str) -> None:
        response.set_cookie("tectx_session", raw_session, max_age=SESSION_LIFETIME_SECONDS,
                            httponly=True, secure=secure_cookie, samesite="strict", path="/")

    def require_claim(con: sqlite3.Connection, claim_id: str) -> dict:
        row = con.execute("SELECT * FROM claims WHERE id=?", (claim_id,)).fetchone()
        if not row:
            raise HTTPException(404, "Unknown review item")
        return dict(row)

    @app.get("/")
    def index():
        return FileResponse(ROOT / "static" / "index.html")

    @app.get("/api/me")
    def me(request: Request):
        user = find_actor(request, required=False)
        if not user:
            return {"signed_in": False, "disclaimer": SCIENTIFIC_DISCLAIMER}
        return {"signed_in": True, "user": {
            "id": user["id"], "name": user["display_name"], "email": user["email"], "role": user["role"]},
            "csrf": user["csrf_token"], "disclaimer": SCIENTIFIC_DISCLAIMER}

    @app.post("/api/login")
    def login(body: LoginBody, request: Request):
        try:
            email = email_normalize(body.email)
        except ValueError:
            raise HTTPException(401, "Incorrect email or password")
        identifier = email + "|" + (request.client.host if request.client else "unknown")
        attempts = [t for t in app.state.failed_logins.get(identifier, []) if t > now() - 600]
        if len(attempts) >= 6:
            raise HTTPException(429, "Too many sign-in attempts; try again later")
        with write_db(db_path) as con:
            user = con.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
            if not user or not verify_password(body.password, user["password_hash"]):
                attempts.append(now())
                app.state.failed_logins[identifier] = attempts
                raise HTTPException(401, "Incorrect email or password")
            app.state.failed_logins.pop(identifier, None)
            raw, csrf = create_session(con, user["id"])
            log_event(con, user["id"], "SESSION_STARTED", None, {})
        response = JSONResponse({"ok": True, "csrf": csrf})
        cookie(response, raw)
        return response

    @app.post("/api/logout")
    def logout(request: Request):
        actor = require_actor(request, mutating=True)
        with write_db(db_path) as con:
            con.execute("DELETE FROM sessions WHERE token_hash=?", (fingerprint(request.cookies["tectx_session"]),))
            log_event(con, actor["id"], "SESSION_ENDED", None, {})
        response = JSONResponse({"ok": True})
        response.delete_cookie("tectx_session", path="/")
        return response

    @app.post("/api/invitations")
    def make_invite(body: InviteBody, request: Request):
        actor = require_actor(request, roles=("admin",), mutating=True)
        try:
            email = email_normalize(body.email)
        except ValueError as exc:
            raise HTTPException(422, str(exc))
        raw = secrets.token_urlsafe(36)
        with write_db(db_path) as con:
            if con.execute("SELECT 1 FROM users WHERE email=?", (email,)).fetchone():
                raise HTTPException(409, "User exists — assign them from the roster")
            con.execute("""INSERT INTO invitations(email,role,token_hash,expires_at,issued_by,created_at)
                VALUES(?,?,?,?,?,?)""", (email, body.role, fingerprint(raw), now()+body.days*86400, actor["id"], now()))
            log_event(con, actor["id"], "INVITATION_ISSUED", None,
                      {"role": body.role, "valid_days": body.days, "recipient_email_masked": email[:2]+"***"})
        public_url = os.environ.get("TECTX_PUBLIC_URL", "").rstrip("/")
        if public_url and not public_url.startswith("https://"):
            raise HTTPException(500, "TECTX_PUBLIC_URL must be HTTPS")
        return {"invitation_url": (public_url or str(request.base_url).rstrip("/")) + "/?invite=" + raw,
                "expires_in_days": body.days,
                "delivery": "Copy this private URL and send manually; the app DOES NOT email anyone.",
                "identity_note": "Invitations and display names do not verify professorial affiliation."}

    @app.get("/api/invitation/{token}")
    def invitation_info(token: str):
        with read_db(db_path) as con:
            row = con.execute("SELECT email,role,expires_at,used_at FROM invitations WHERE token_hash=?",
                              (fingerprint(token),)).fetchone()
        if not row or row["used_at"] is not None or row["expires_at"] <= now():
            raise HTTPException(404, "Invitation is invalid, used, or expired")
        return {"email": row["email"], "role": row["role"], "expires_at": row["expires_at"]}

    @app.post("/api/join")
    def join(body: JoinBody):
        if not body.consent_to_review:
            raise HTTPException(422, "Explicit participation and review-record consent is required")
        try:
            pw = hash_password(body.password)
        except ValueError as exc:
            raise HTTPException(422, str(exc))
        with write_db(db_path) as con:
            invitation = con.execute("SELECT * FROM invitations WHERE token_hash=?",
                                     (fingerprint(body.token),)).fetchone()
            if not invitation or invitation["used_at"] is not None or invitation["expires_at"] <= now():
                raise HTTPException(404, "Invitation is invalid, used, or expired")
            if con.execute("SELECT 1 FROM users WHERE email=?", (invitation["email"],)).fetchone():
                raise HTTPException(409, "User already exists")
            user = con.execute("INSERT INTO users(email,display_name,role,password_hash,created_at) VALUES(?,?,?,?,?)",
                               (invitation["email"], body.name.strip(), invitation["role"], pw, now()))
            con.execute("UPDATE invitations SET used_at=? WHERE id=?", (now(), invitation["id"]))
            log_event(con, user.lastrowid, "INVITATION_ACCEPTED", None, {"role": invitation["role"], "participation_consent": True})
            raw, csrf = create_session(con, user.lastrowid)
        response = JSONResponse({"ok": True, "csrf": csrf})
        cookie(response, raw)
        return response

    @app.get("/api/dashboard")
    def dashboard(request: Request):
        actor = require_actor(request)
        with read_db(db_path) as con:
            claims = [dict(r) for r in con.execute("SELECT * FROM claims ORDER BY id")]
            users = []
            if actor["role"] == "admin":
                users = [dict(r) for r in con.execute("SELECT id,display_name,email,role FROM users ORDER BY role,display_name")]
            assigned = {r["claim_id"] for r in con.execute("SELECT claim_id FROM assignments WHERE reviewer_id=?", (actor["id"],))}
            reviewed = {(r["claim_id"],r["round"]) for r in con.execute(
                "SELECT claim_id,round FROM reviews WHERE reviewer_id=?", (actor["id"],))}
            for c in claims:
                counts = con.execute("""SELECT
                    COUNT(*) AS total, SUM(CASE WHEN verdict='approve_teaching' THEN 1 ELSE 0 END) AS approvals
                    FROM reviews WHERE claim_id=? AND round=?""", (c["id"], c["round"])).fetchone()
                c["reviews_count"] = counts["total"]
                c["approvals"] = counts["approvals"] or 0
                c["mine"] = c["id"] in assigned
                c["my_review_submitted"] = (c["id"], c["round"]) in reviewed
                c["can_review"] = actor["role"] == "reviewer" and c["mine"] and not c["my_review_submitted"] and c["status"] in ("open_for_review", "in_review", "ready_for_adjudication") and c["author_id"] != actor["id"]
                # Independent reviews stay blinded until a reviewer submits.
                if actor["role"] == "reviewer" and not c["my_review_submitted"]:
                    c["reviews_count"] = None
                    c["approvals"] = None
            events = [dict(r) for r in con.execute("""SELECT e.id,e.action,e.claim_id,e.details_json,e.created_at,
                    COALESCE(u.display_name,'System') AS actor_name FROM events e LEFT JOIN users u ON e.actor_id=u.id
                    ORDER BY e.id DESC LIMIT 35""")]
        return {"claims": claims, "users": users, "recent_events": events,
                "source": "ResearchOS TECT-X Standalone Zeta TDA Curriculum (DOCX)",
                "source_path": "/api/curriculum.docx", "disclaimer": SCIENTIFIC_DISCLAIMER}

    @app.get("/api/claims/{claim_id}")
    def claim_detail(claim_id: str, request: Request):
        actor = require_actor(request)
        with read_db(db_path) as con:
            claim = require_claim(con, claim_id)
            mine = con.execute("SELECT 1 FROM assignments WHERE claim_id=? AND reviewer_id=?",
                               (claim_id, actor["id"])).fetchone() is not None
            own_review = con.execute("SELECT 1 FROM reviews WHERE claim_id=? AND reviewer_id=? AND round=?",
                (claim_id, actor["id"], claim["round"])).fetchone() is not None
            show = actor["role"] == "admin" or own_review
            reviews = []
            if show:
                reviews = [dict(r) for r in con.execute("""SELECT r.id,r.round,r.verdict,r.evidence,r.limitations,r.submitted_at,
                    u.display_name AS reviewer_name FROM reviews r JOIN users u ON u.id=r.reviewer_id
                    WHERE r.claim_id=? AND r.round=? ORDER BY r.id""", (claim_id, claim["round"]))]
            assignments = []
            if actor["role"] == "admin":
                assignments = [dict(r) for r in con.execute("""SELECT a.reviewer_id,u.display_name,u.email,a.created_at
                    FROM assignments a JOIN users u ON u.id=a.reviewer_id WHERE a.claim_id=?""", (claim_id,))]
            history = [dict(r) for r in con.execute("""SELECT round,decision,rationale,decided_at FROM decisions
                WHERE claim_id=? ORDER BY id DESC""", (claim_id,))]
        return {"claim": claim, "reviews": reviews, "reviewed_by_me": own_review,
                "assigned_to_me": mine, "assignments": assignments, "decisions": history,
                "reviews_blinded": not show,
                "source_note": "Plain-text excerpts may omit native Word equations. Consult the attached DOCX for formulas."}

    @app.post("/api/proposals")
    def propose(body: ProposalBody, request: Request):
        actor = require_actor(request, roles=("admin", "reviewer", "editor"), mutating=True)
        if body.evidence_url and not body.evidence_url.startswith("https://"):
            raise HTTPException(422, "Evidence links must begin with https://")
        claim_id = "proposal-" + secrets.token_hex(7)
        with write_db(db_path) as con:
            con.execute("""INSERT INTO claims
              (id,title,category,week,goal,body,source_section,proof_scope,evidence_url,
               status,round,author_id,created_at,updated_at)
              VALUES(?,?,?,?,?,?,?,?,?,'open_for_review',1,?,?,?)""",
              (claim_id, body.title.strip(), body.category, "Professor proposal",
               body.goal.strip(), body.body.strip(), "Reviewer-authored proposal",
               "OPEN_MATHEMATICAL_BRIDGE" if body.category == "research_gap" else "PROPOSAL_UNVERIFIED",
               body.evidence_url.strip(), actor["id"], now(), now()))
            log_event(con, actor["id"], "PROPOSAL_SUBMITTED", claim_id,
                      {"category": body.category, "stage": "open_for_review", "theorem_certified": False})
        return {"ok": True, "claim_id": claim_id, "stage": "open_for_review",
                "proof_certified": False}

    @app.post("/api/assign")
    def assign(body: AssignmentBody, request: Request):
        actor = require_actor(request, roles=("admin",), mutating=True)
        with write_db(db_path) as con:
            claim = require_claim(con, body.claim_id)
            user = con.execute("SELECT id,role FROM users WHERE id=?", (body.reviewer_id,)).fetchone()
            if not user or user["role"] != "reviewer":
                raise HTTPException(422, "Only registered reviewers can receive assignments")
            if claim["author_id"] == body.reviewer_id:
                raise HTTPException(403, "An author cannot review their own work")
            if claim["status"] == "teaching_approved":
                raise HTTPException(409, "Approved content requires a new revision round")
            try:
                con.execute("INSERT INTO assignments(claim_id,reviewer_id,assigned_by,created_at) VALUES(?,?,?,?)",
                            (body.claim_id, body.reviewer_id, actor["id"], now()))
            except sqlite3.IntegrityError:
                raise HTTPException(409, "Reviewer already assigned")
            if claim["status"] == "open_for_review":
                con.execute("UPDATE claims SET status='in_review',updated_at=? WHERE id=?", (now(), body.claim_id))
            log_event(con, actor["id"], "REVIEWER_ASSIGNED", body.claim_id, {"reviewer_user_id": body.reviewer_id})
        return {"ok": True, "note": "Assignment recorded; the app sends no emails"}

    @app.post("/api/review")
    def submit_review(body: ReviewBody, request: Request):
        actor = require_actor(request, roles=("reviewer",), mutating=True)
        with write_db(db_path) as con:
            claim = require_claim(con, body.claim_id)
            if claim["author_id"] == actor["id"]:
                raise HTTPException(403, "You cannot review your own work")
            if not con.execute("SELECT 1 FROM assignments WHERE claim_id=? AND reviewer_id=?",
                               (body.claim_id, actor["id"])).fetchone():
                raise HTTPException(403, "This item is not assigned to you")
            if claim["status"] not in ("open_for_review", "in_review", "ready_for_adjudication"):
                raise HTTPException(409, "Current review round is closed or awaiting revision")
            if con.execute("SELECT 1 FROM reviews WHERE claim_id=? AND reviewer_id=? AND round=?",
                           (body.claim_id, actor["id"], claim["round"])).fetchone():
                raise HTTPException(409, "You already reviewed this round")
            con.execute("INSERT INTO reviews(claim_id,reviewer_id,round,verdict,evidence,limitations,submitted_at) VALUES(?,?,?,?,?,?,?)",
                        (body.claim_id, actor["id"], claim["round"], body.verdict,
                         body.evidence.strip(), body.limitations.strip(), now()))
            verdicts = [r["verdict"] for r in con.execute("SELECT verdict FROM reviews WHERE claim_id=? AND round=?",
                                                           (body.claim_id, claim["round"]))]
            if "reject_teaching" in verdicts or "request_revision" in verdicts:
                stage = "revision_requested"
            elif verdicts.count("approve_teaching") >= 2:
                stage = "ready_for_adjudication"
            else:
                stage = "in_review"
            con.execute("UPDATE claims SET status=?,updated_at=? WHERE id=?", (stage, now(), body.claim_id))
            log_event(con, actor["id"], "INDEPENDENT_REVIEW_SUBMITTED", body.claim_id,
                      {"round": claim["round"], "verdict": body.verdict, "stage": stage})
        return {"ok": True, "stage": stage,
                "boundary": "Reviewer approval does not establish truth or certify any theorem"}

    @app.post("/api/revise")
    def revise(body: RevisionBody, request: Request):
        actor = require_actor(request, roles=("admin", "editor", "reviewer"), mutating=True)
        if body.evidence_url and not body.evidence_url.startswith("https://"):
            raise HTTPException(422, "Evidence links must begin with https://")
        with write_db(db_path) as con:
            claim = require_claim(con, body.claim_id)
            if actor["role"] != "admin" and claim["author_id"] != actor["id"]:
                raise HTTPException(403, "Only the author or an administrator can revise this item")
            if claim["status"] not in ("revision_requested", "teaching_approved", "open_for_review"):
                raise HTTPException(409, "Revision is available only for returned, approved or unreviewed items")
            newround = claim["round"] + 1
            con.execute("""UPDATE claims SET goal=?,body=?,evidence_url=?,round=?,status='in_review',updated_at=? WHERE id=?""",
                        (body.goal.strip(), body.body.strip(), body.evidence_url.strip(), newround, now(), body.claim_id))
            log_event(con, actor["id"], "CLAIM_REVISED", body.claim_id,
                      {"prior_round": claim["round"], "new_round": newround,
                       "rationale": body.rationale.strip()})
        return {"ok": True, "round": newround}

    @app.post("/api/adjudicate")
    def adjudicate(body: DecisionBody, request: Request):
        actor = require_actor(request, roles=("admin",), mutating=True)
        with write_db(db_path) as con:
            claim = require_claim(con, body.claim_id)
            if claim["author_id"] == actor["id"]:
                raise HTTPException(403, "Author cannot adjudicate their own claim")
            if con.execute("SELECT 1 FROM reviews WHERE claim_id=? AND reviewer_id=? AND round=?",
                           (body.claim_id, actor["id"], claim["round"])).fetchone():
                raise HTTPException(403, "Reviewers cannot adjudicate their own review")
            if body.decision == "approve_teaching":
                if claim["status"] != "ready_for_adjudication":
                    raise HTTPException(409, "Two independent positive reviews are required")
                reviewers = con.execute("""SELECT COUNT(DISTINCT reviewer_id) AS n
                    FROM reviews WHERE claim_id=? AND round=? AND verdict='approve_teaching'""",
                    (body.claim_id, claim["round"])).fetchone()["n"]
                if reviewers < 2:
                    raise HTTPException(409, "Two distinct reviewers required")
                stage = "teaching_approved"
            else:
                if claim["status"] not in ("ready_for_adjudication", "in_review", "revision_requested"):
                    raise HTTPException(409, "This item cannot be returned now")
                stage = "revision_requested"
            con.execute("""INSERT INTO decisions(claim_id,adjudicator_id,round,decision,rationale,decided_at)
                VALUES(?,?,?,?,?,?)""", (body.claim_id, actor["id"], claim["round"], body.decision,
                                          body.rationale.strip(), now()))
            con.execute("UPDATE claims SET status=?,updated_at=? WHERE id=?", (stage, now(), body.claim_id))
            log_event(con, actor["id"], "EDITORIAL_DECISION", body.claim_id,
                      {"decision": body.decision, "round": claim["round"],
                       "scope": "TEACHING_USE_ONLY", "mathematical_proof_certified": False})
        return {"ok": True, "stage": stage, "mathematical_proof_certified": False,
                "scope": "Approved only for teaching use; mathematical truth remains independently assessed"}

    @app.get("/api/audit-export")
    def audit_export(request: Request):
        actor = require_actor(request, roles=("admin",))
        with read_db(db_path) as con:
            claims = [dict(r) for r in con.execute("SELECT * FROM claims ORDER BY id")]
            reviews = [dict(r) for r in con.execute("""SELECT r.claim_id,r.round,r.verdict,r.evidence,r.limitations,
                r.submitted_at,r.reviewer_id FROM reviews r ORDER BY r.id""")]
            decisions = [dict(r) for r in con.execute("""SELECT claim_id,round,decision,rationale,decided_at,
                adjudicator_id FROM decisions ORDER BY id""")]
            events = [dict(r) for r in con.execute("SELECT action,claim_id,details_json,created_at FROM events ORDER BY id")]
            log_event(con, actor["id"], "ANONYMIZED_AUDIT_EXPORTED", None, {})
        export = {"generated_at": datetime.now(timezone.utc).isoformat(),
                  "scope": "EDUCATIONAL_REVIEW_ONLY_NOT_PROOF_CERTIFICATION", "claims": claims,
                  "reviews": reviews, "decisions": decisions, "events": events,
                  "privacy": "Pseudonym IDs do not guarantee anonymity if authors add names to free-text remarks.",
                  "mathematical_proof_certified": False}
        data = json.dumps(export, ensure_ascii=False, indent=2)
        return JSONResponse(export, headers={"Content-Disposition": "attachment; filename=tectx-review-audit.json",
                                             "Cache-Control": "no-store"})

    @app.get("/api/curriculum.docx")
    def source_file(request: Request):
        require_actor(request)
        if not source_docx.is_file():
            raise HTTPException(404, "Original curriculum DOCX not bundled")
        return FileResponse(source_docx, filename=source_docx.name,
                            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            headers={"Cache-Control": "private, no-store"})

    return app


def cli(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="TECT-X invitation-only academic review prototype")
    subs = parser.add_subparsers(dest="command", required=True)
    p_init = subs.add_parser("init", help="Create local DB and first admin (password prompted securely)")
    p_init.add_argument("--email", required=True)
    p_init.add_argument("--name", default="Curriculum administrator")
    p_serve = subs.add_parser("serve", help="Run local review web app")
    p_serve.add_argument("--host", default="127.0.0.1")
    p_serve.add_argument("--port", type=int, default=8765)
    p_serve.add_argument("--db", type=Path, default=DEFAULT_DB)
    args = parser.parse_args(argv)
    if args.command == "init":
        import getpass
        init_db(DEFAULT_DB)
        try:
            password = getpass.getpass("New admin password (12+ characters): ")
            password2 = getpass.getpass("Repeat password: ")
            if password != password2:
                raise ValueError("Passwords do not match")
            create_user(DEFAULT_DB, args.email, args.name, password, role="admin")
        except (ValueError, sqlite3.IntegrityError) as exc:
            parser.error(str(exc))
        print("Local administrator created. Run: python app.py serve")
    else:
        if args.host not in ("127.0.0.1", "localhost", "::1"):
            if os.environ.get("TECTX_HTTPS_ONLY") != "1":
                parser.error("Non-local binds require TECTX_HTTPS_ONLY=1 and a correctly configured TLS proxy")
            if not os.environ.get("TECTX_PUBLIC_URL", "").startswith("https://"):
                parser.error("Non-local binds require TECTX_PUBLIC_URL=https://your.trusted.domain")
            if not os.environ.get("TECTX_ALLOWED_HOSTS"):
                parser.error("Non-local binds require TECTX_ALLOWED_HOSTS=your.trusted.domain")
        import uvicorn
        uvicorn.run(create_app(args.db), host=args.host, port=args.port, log_level="info", proxy_headers=False)


if __name__ == "__main__":
    cli()
