"""
profiles.py — User profile endpoints demonstrating Insecure Direct Object References (IDOR).

This module shows:
  - VULNERABLE: /users/<user_id> — Broken access control (no authorization check)
  - SECURE: /users/me — Proper access control (session-based authorization)
"""
from __future__ import annotations

from flask import Blueprint, jsonify, request, session

from .audit import log_action
from .db import tx
from .rbac import requires_auth
from .validators import sanitize_text

bp = Blueprint("profiles", __name__, url_prefix="/users")


# ---------------------------------------------------------------------------
# VULNERABLE: IDOR - Insecure Direct Object References
# ---------------------------------------------------------------------------

@bp.get("/<int:user_id>")
@requires_auth
def get_user_profile_insecure(user_id: int):
    """
    VULNERABLE: Broken Access Control (IDOR).
    
    Returns ANY user profile without verifying ownership.
    Any authenticated user can access any other user's data by changing user_id.
    
    This is the ATTACK endpoint for the User Profile IDOR demo.
    """
    # VULNERABLE: IDOR
    # No check if session['user_id'] == user_id
    # Simply returns whatever user_id is requested
    
    with tx() as db:
        user = db.execute(
            "SELECT id, username, email, phone, address, notes FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        log_action(
            "USER_PROFILE_ACCESSED",
            resource=f"user:{user_id}",
            details={"accessed_by_user_id": session.get("user_id")},
            success=True
        )
        
        return jsonify({
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "phone": user["phone"],
            "address": user["address"],
            "notes": user["notes"],
        })


# ---------------------------------------------------------------------------
# SECURE: Proper Access Control
# ---------------------------------------------------------------------------

@bp.get("/me")
@requires_auth
def get_user_profile_secure():
    """
    SECURE: Proper access control enforcement.
    
    Returns ONLY the currently authenticated user's profile.
    Uses session['user_id'] to enforce authorization.
    
    This is the DEFEND endpoint for the User Profile IDOR demo.
    """
    # SECURE: Proper access control
    # Extract user_id from session, not from request params
    user_id = session.get("user_id")
    
    with tx() as db:
        user = db.execute(
            "SELECT id, username, email, phone, address, notes FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "phone": user["phone"],
            "address": user["address"],
            "notes": user["notes"],
        })


@bp.put("/me")
@requires_auth
def update_user_profile():
    """
    Update current user's profile.
    
    Allows updating: email, phone, address, notes.
    Cannot modify username, id, or role.
    """
    user_id = session.get("user_id")
    data = request.get_json() or {}
    
    # Validate inputs
    email = data.get("email", "").strip()
    phone = data.get("phone", "").strip()
    address = data.get("address", "").strip()
    notes = data.get("notes", "").strip()
    
    # Sanitize text inputs
    if email:
        email = sanitize_text(email)
    if address:
        address = sanitize_text(address)
    if notes:
        notes = sanitize_text(notes)
    
    # Validate email format if provided
    if email and "@" not in email:
        return jsonify({"error": "Invalid email format"}), 400
    
    # Update database
    with tx() as db:
        db.execute(
            "UPDATE users SET email = ?, phone = ?, address = ?, notes = ? WHERE id = ?",
            (email, phone, address, notes, user_id)
        )
        db.commit()
        
        log_action(
            "USER_PROFILE_UPDATED",
            resource=f"user:{user_id}",
            details={"fields_updated": ["email", "phone", "address", "notes"]},
            success=True
        )
    
    return jsonify({
        "ok": True,
        "message": "Profile updated",
        "id": user_id,
        "email": email,
        "phone": phone,
        "address": address,
        "notes": notes,
    })
