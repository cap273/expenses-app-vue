# household_routes.py
from flask import Blueprint, jsonify, request, current_app
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from flask_login import current_user
from werkzeug.exceptions import BadRequestKeyError

from flask_backend.utils.session import login_required_api
from flask_backend.database.models import db, Account, Scope, ScopeAccess

household_routes = Blueprint("household_routes", __name__)

@household_routes.route("/api/get_scopes", methods=["GET"])
@login_required_api
def get_scopes():
    """Get all scopes that the current user has access to"""
    try:
        # Join scope_access with scopes to get scope details
        scope_query = (
            db.session.query(Scope, ScopeAccess)
            .join(ScopeAccess, Scope.ScopeID == ScopeAccess.ScopeID)
            .filter(
                ScopeAccess.AccountID == current_user.id,
                ScopeAccess.InviteStatus == 'accepted'
            )
            .all()
        )

        scopes = [{
            'id': scope.ScopeID,
            'name': scope.ScopeName,
            'type': scope.ScopeType,
            'access_type': access.AccessType
        } for scope, access in scope_query]

        return jsonify({"success": True, "scopes": scopes})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@household_routes.route("/api/get_pending_invites", methods=["GET"])
@login_required_api
def get_pending_invites():
    """Get all pending household invites for the current user"""
    try:
        # Subquery to find the owner of each scope
        owner_subquery = (
            db.session.query(ScopeAccess.AccountID)
            .filter(
                ScopeAccess.ScopeID == Scope.ScopeID,
                ScopeAccess.AccessType == 'owner'
            )
            .correlate(Scope)  # Explicitly correlate the subquery with the outer query
            .scalar_subquery()
        )

        # Main query to find pending invites for the current user
        pending_invites_query = (
            db.session.query(Scope, ScopeAccess, Account)
            .join(ScopeAccess, Scope.ScopeID == ScopeAccess.ScopeID)
            .join(
                Account,
                Account.id == owner_subquery  # Join with the owner subquery
            )
            .filter(
                ScopeAccess.AccountID == current_user.id,
                ScopeAccess.InviteStatus == 'pending'
            )
            .all()
        )

        invites = [{
            'scope_id': scope.ScopeID,
            'scope_name': scope.ScopeName,
            'inviter_email': inviter.user_email
        } for scope, access, inviter in pending_invites_query]

        return jsonify({"success": True, "invites": invites})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@household_routes.route("/api/create_household", methods=["POST"])
@login_required_api
def create_household():
    """Create a new household scope"""
    try:
        data = request.json
        household_name = data.get("name")

        if not household_name:
            return jsonify({"success": False, "error": "Household name is required"})

        # Create new household scope
        new_scope = Scope(
            ScopeName=household_name,
            ScopeType='household',
            CreateDate=datetime.now().date(),
            LastUpdated=datetime.now().date()
        )
        db.session.add(new_scope)
        db.session.flush()

        # Create access record for the creating user
        scope_access = ScopeAccess(
            ScopeID=new_scope.ScopeID,
            AccountID=current_user.id,
            AccessType='owner',
            InviteStatus='accepted',
            CreateDate=datetime.now().date(),
            LastUpdated=datetime.now().date()
        )
        db.session.add(scope_access)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Household created successfully",
            "household": {
                "id": new_scope.ScopeID,
                "name": new_scope.ScopeName
            }
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)})

@household_routes.route("/api/invite_to_household", methods=["POST"])
@login_required_api
def invite_to_household():
    """Invite a user to a household by email"""
    try:
        data = request.json
        email = data.get("email")
        scope_id = data.get("scopeId")

        if not email or not scope_id:
            return jsonify({"success": False, "error": "Email and scope ID are required"})

        # Check if the inviting user has owner access
        inviter_access = ScopeAccess.query.filter_by(
            ScopeID=scope_id,
            AccountID=current_user.id,
            AccessType='owner'
        ).first()

        if not inviter_access:
            return jsonify({"success": False, "error": "You don't have permission to invite users"})

        # Find the invited user
        invited_user = Account.query.filter_by(user_email=email).first()
        if not invited_user:
            return jsonify({"success": False, "error": "User not found"})

        # Check if invite already exists
        existing_invite = ScopeAccess.query.filter_by(
            ScopeID=scope_id,
            AccountID=invited_user.id
        ).first()

        if existing_invite:
            return jsonify({"success": False, "error": "User already has access or pending invite"})

        # Create new access record
        new_access = ScopeAccess(
            ScopeID=scope_id,
            AccountID=invited_user.id,
            AccessType='member',
            InviteStatus='pending',
            CreateDate=datetime.now().date(),
            LastUpdated=datetime.now().date()
        )
        db.session.add(new_access)
        db.session.commit()

        return jsonify({"success": True, "message": f"Invitation sent to {email}"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)})

@household_routes.route("/api/respond_to_invite", methods=["POST"])
@login_required_api
def respond_to_invite():
    """Accept or reject a household invitation"""
    try:
        data = request.json
        scope_id = data.get("scopeId")
        response = data.get("response")  # 'accept' or 'reject'

        if not scope_id or not response:
            return jsonify({"success": False, "error": "Scope ID and response are required"})

        # Find the invitation
        invite = ScopeAccess.query.filter_by(
            ScopeID=scope_id,
            AccountID=current_user.id,
            InviteStatus='pending'
        ).first()

        if not invite:
            return jsonify({"success": False, "error": "Invitation not found"})

        # Update invitation status
        invite.InviteStatus = 'accepted' if response == 'accept' else 'rejected'
        invite.LastUpdated = datetime.now().date()
        db.session.commit()

        return jsonify({
            "success": True,
            "message": f"Invitation {invite.InviteStatus}"
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)})
    
@household_routes.route("/api/get_household_members", methods=["GET"])
@login_required_api
def get_household_members():
    """Get members for a specific household scope"""
    try:
        scope_id = request.args.get("scopeId")
        if not scope_id:
            return jsonify({"success": False, "error": "Scope ID is required"})
        
        members_query = (
            db.session.query(Account, ScopeAccess)
            .join(ScopeAccess, Account.id == ScopeAccess.AccountID)
            .filter(ScopeAccess.ScopeID == scope_id)
            .all()
        )
        
        members = [{
            "email": account.user_email,
            "access_type": access.AccessType
        } for account, access in members_query]
        
        return jsonify({"success": True, "members": members})
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})
