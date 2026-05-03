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

@bp.get("/attack/<path:user_input>")
@requires_auth
def get_user_profile_insecure(user_input: str):
    """
    VULNERABLE: Broken Access Control (IDOR) + SQL Injection.
    
    Accepts user input directly in SQL query using string interpolation.
    No authorization check — anyone can access any data.
    SQL Injection payloads work: ' OR '1'='1 returns ALL users.
    
    This is the ATTACK endpoint for the User Profile IDOR demo.
    """
    # VULNERABLE: IDOR + String interpolation in SQL
    # No parameterization, no authorization check
    
    with tx() as db:
        try:
            # Vulnerable: String interpolation allows SQL injection
            sql = f"SELECT id, username, email, phone, address, notes FROM users WHERE id = '{user_input}' OR '1'='1'"
            users = db.execute(sql).fetchall()
            
            if not users:
                return jsonify({"error": "No users found"}), 404
            
            log_action(
                "USER_PROFILE_ACCESSED_INSECURE",
                resource="user:*",
                details={"input": user_input, "accessed_by_user_id": session.get("user_id")},
                success=True
            )
            
            # Return all matching users (vulnerable to IDOR + SQLi)
            result = []
            for user in users:
                result.append({
                    "id": user["id"],
                    "username": user["username"],
                    "email": user["email"],
                    "phone": user["phone"],
                    "address": user["address"],
                    "notes": user["notes"],
                })
            
            return jsonify({
                "vulnerable": True,
                "users_returned": len(result),
                "users": result,
                "sql": sql,
            })
        except Exception as e:
            return jsonify({
                "error": str(e),
                "vulnerable": True
            }), 400


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
    No user input in query — cannot be exploited.
    
    This is the DEFEND endpoint for the User Profile IDOR demo.
    """
    # SECURE: Proper access control
    # Extract user_id from session, not from request params
    user_id = session.get("user_id")
    
    if not user_id:
        return jsonify({"error": "Not authenticated"}), 401
    
    with tx() as db:
        user = db.execute(
            "SELECT id, username, email, phone, address, notes FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        log_action(
            "USER_PROFILE_VIEWED_SECURE",
            resource=f"user:{user_id}",
            details={"user_id": user_id},
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
