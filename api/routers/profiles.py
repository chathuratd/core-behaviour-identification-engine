"""
api/routers/profiles.py
=======================
Profile inspection and management endpoints for the frontend dashboard.

GET  /profiles/                    — List all users with a generated profile
GET  /profiles/{user_id}           — Full Core Behaviour Profile JSON
GET  /profiles/{user_id}/interests — Confirmed interests list (for dashboard card)
GET  /profiles/{user_id}/facts     — Critical constraints only (for alert panels)
DELETE /profiles/{user_id}         — Delete a user's profile
"""
from __future__ import annotations
import json
import os
from typing import List

from fastapi import APIRouter, HTTPException, Query

from api.models import (
    ProfileListResponse,
    ProfileResponse,
    ProfileSummary,
    InterestsResponse,
    FactsResponse,
    InterestEntry,
)
from data_adapter import DataAdapter

router = APIRouter(prefix="/profiles", tags=["Profiles"])

_data_adapter = DataAdapter()


# ---------------------------------------------------------------------------
# Helper: load raw interests from Supabase row
# ---------------------------------------------------------------------------

def _parse_interests(raw) -> List[dict]:
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except Exception:
            return []
    return raw or []


def _get_profile_row(user_id: str) -> dict:
    """Raise 404 if the user has no profile, else return the Supabase row."""
    if not _data_adapter.supabase:
        raise HTTPException(status_code=503, detail="Database connection unavailable.")
    try:
        resp = (
            _data_adapter.supabase
            .table("core_behavior_profiles")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database query failed: {e}")

    if not resp.data:
        raise HTTPException(
            status_code=404,
            detail=f"No profile found for user '{user_id}'.",
        )
    return resp.data[0]


# ---------------------------------------------------------------------------
# GET /profiles/
# ---------------------------------------------------------------------------

@router.get(
    "/",
    response_model=ProfileListResponse,
    summary="List All User Profiles",
    description="Returns a paginated summary of all users who have a generated Core Behaviour Profile.",
)
async def list_profiles(
    limit: int = Query(50, ge=1, le=200, description="Max records to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
):
    if not _data_adapter.supabase:
        raise HTTPException(status_code=503, detail="Database connection unavailable.")

    try:
        resp = (
            _data_adapter.supabase
            .table("core_behavior_profiles")
            .select("user_id, confirmed_interests, updated_at")
            .range(offset, offset + limit - 1)
            .execute()
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database query failed: {e}")

    summaries: List[ProfileSummary] = []
    for row in resp.data:
        interests = _parse_interests(row.get("confirmed_interests", []))
        facts = [i for i in interests if i.get("status") == "Stable Fact"]
        stable = [i for i in interests if i.get("status") == "Stable"]
        emerging = [i for i in interests if i.get("status") == "Emerging"]
        summaries.append(
            ProfileSummary(
                user_id=row["user_id"],
                total_raw_behaviors=row.get("total_raw_behaviors", 0),
                interest_count=len(interests),
                fact_count=len(facts),
                stable_count=len(stable),
                emerging_count=len(emerging),
                last_updated=row.get("updated_at"),
            )
        )

    return ProfileListResponse(total=len(summaries), profiles=summaries)


# ---------------------------------------------------------------------------
# GET /profiles/{user_id}
# ---------------------------------------------------------------------------

@router.get(
    "/{user_id}",
    response_model=ProfileResponse,
    summary="Get Full Core Behaviour Profile",
    description="Returns the complete Core Behaviour Profile for a specific user.",
)
async def get_profile(user_id: str):
    row = _get_profile_row(user_id)
    interests_raw = _parse_interests(row.get("confirmed_interests", []))
    interests = [InterestEntry(**i) for i in interests_raw]

    return ProfileResponse(
        user_id=user_id,
        total_raw_behaviors=row.get("total_raw_behaviors", 0),
        confirmed_interests=interests,
        identity_anchor_prompt=row.get("identity_anchor_prompt"),
        last_updated=row.get("updated_at"),
    )


# ---------------------------------------------------------------------------
# GET /profiles/{user_id}/interests
# ---------------------------------------------------------------------------

@router.get(
    "/{user_id}/interests",
    response_model=InterestsResponse,
    summary="Get Confirmed Interests",
    description=(
        "Returns only the `confirmed_interests` list for a user. "
        "Useful for rendering dashboard cards showing the user's tech, hobbies, etc."
    ),
)
async def get_interests(
    user_id: str,
    status_filter: str = Query(
        None,
        description="Filter by status: Stable | Emerging | ARCHIVED_CORE | Stable Fact | Noise",
    ),
):
    row = _get_profile_row(user_id)
    interests_raw = _parse_interests(row.get("confirmed_interests", []))

    if status_filter:
        interests_raw = [i for i in interests_raw if i.get("status") == status_filter]

    interests = [InterestEntry(**i) for i in interests_raw]
    return InterestsResponse(
        user_id=user_id,
        interests=interests,
        total_count=len(interests),
    )


# ---------------------------------------------------------------------------
# GET /profiles/{user_id}/facts
# ---------------------------------------------------------------------------

@router.get(
    "/{user_id}/facts",
    response_model=FactsResponse,
    summary="Get Critical Constraints (Facts)",
    description=(
        "Returns ONLY the interests with status='Stable Fact' — i.e., hard identity "
        "constraints like allergies, dietary restrictions, medical conditions. "
        "Ideal for a 'Never violate' alert panel in the frontend."
    ),
)
async def get_facts(user_id: str):
    row = _get_profile_row(user_id)
    interests_raw = _parse_interests(row.get("confirmed_interests", []))
    facts_raw = [i for i in interests_raw if i.get("status") == "Stable Fact"]
    facts = [InterestEntry(**f) for f in facts_raw]

    return FactsResponse(
        user_id=user_id,
        facts=facts,
        total_count=len(facts),
    )


# ---------------------------------------------------------------------------
# DELETE /profiles/{user_id}
# ---------------------------------------------------------------------------

@router.delete(
    "/{user_id}",
    status_code=204,
    summary="Delete User Profile",
    description=(
        "Permanently deletes the Core Behaviour Profile for a user from Supabase "
        "and the local JSON file if it exists."
    ),
)
async def delete_profile(user_id: str):
    if not _data_adapter.supabase:
        raise HTTPException(status_code=503, detail="Database connection unavailable.")

    # Verify profile exists first
    _get_profile_row(user_id)

    try:
        _data_adapter.supabase.table("core_behavior_profiles").delete().eq(
            "user_id", user_id
        ).execute()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Failed to delete from Supabase: {e}")

    # Also remove local JSON file if present
    local_path = os.path.join(_data_adapter.output_dir, f"{user_id}_profile.json")
    if os.path.exists(local_path):
        os.remove(local_path)

    # 204 No Content — return nothing
    return None
