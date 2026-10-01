import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
from fastmcp import FastMCP
from pydantic import Field

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

_DATA_PATH = Path(__file__).parent / "data" / "sling.json"
_db: dict = json.loads(_DATA_PATH.read_text())


def _match(record: dict, field: str, value: str) -> bool:
    """Case-insensitive substring match on a field."""
    return value.lower() in str(record.get(field, "")).lower()


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

mcp = FastMCP(
    name="sling-mock",
    version="1.0.0",
    instructions=(
        "Mock Sling shift management platform for Big Grove Brewery. Query employee schedules, "
        "open shifts, time off requests, and labor summaries across Iowa City, Solon, and Event Space "
        "locations. Use get_open_shifts to find coverage gaps and get_schedule to view the weekly schedule."
    ),
)

# ---------------------------------------------------------------------------
# Locations
# ---------------------------------------------------------------------------

@mcp.tool()
def get_locations(
    id: Optional[str] = Field(default=None, description="Filter by location ID, e.g. loc-001"),
    name: Optional[str] = Field(default=None, description="Filter by location name (partial match)"),
) -> list[dict]:
    """List locations. Optionally filter by ID or name."""
    results = _db["locations"]
    if id:
        results = [r for r in results if r["id"].lower() == id.lower()]
    if name:
        results = [r for r in results if _match(r, "name", name)]
    return results


# ---------------------------------------------------------------------------
# Positions
# ---------------------------------------------------------------------------

@mcp.tool()
def get_positions(
    id: Optional[str] = Field(default=None, description="Filter by position ID, e.g. pos-001"),
    name: Optional[str] = Field(default=None, description="Filter by position name (partial match)"),
    department: Optional[str] = Field(default=None, description="Filter by department: FOH | BOH | Management"),
) -> list[dict]:
    """List positions. Optionally filter by ID, name, or department."""
    results = _db["positions"]
    if id:
        results = [r for r in results if r["id"].lower() == id.lower()]
    if name:
        results = [r for r in results if _match(r, "name", name)]
    if department:
        results = [r for r in results if _match(r, "department", department)]
    return results


# ---------------------------------------------------------------------------
# Employees
# ---------------------------------------------------------------------------

@mcp.tool()
def get_employees(
    id: Optional[str] = Field(default=None, description="Filter by employee ID, e.g. emp-001"),
    name: Optional[str] = Field(default=None, description="Partial match on first or last name"),
    location_id: Optional[str] = Field(default=None, description="Filter by primary location ID"),
    position_id: Optional[str] = Field(default=None, description="Filter by position ID"),
    position_name: Optional[str] = Field(default=None, description="Filter by position name (partial match)"),
    status: Optional[str] = Field(default=None, description="Filter by status: active | inactive"),
) -> list[dict]:
    """List employees. Optionally filter by ID, name, location, position, or status."""
    results = _db["employees"]
    if id:
        results = [r for r in results if r["id"].lower() == id.lower()]
    if name:
        results = [
            r for r in results
            if name.lower() in r["first_name"].lower() or name.lower() in r["last_name"].lower()
        ]
    if location_id:
        results = [r for r in results if r["location_id"].lower() == location_id.lower()]
    if position_id:
        results = [r for r in results if r["position_id"].lower() == position_id.lower()]
    if position_name:
        results = [r for r in results if _match(r, "position_name", position_name)]
    if status:
        results = [r for r in results if _match(r, "status", status)]
    return results


# ---------------------------------------------------------------------------
# Shifts
# ---------------------------------------------------------------------------

@mcp.tool()
def get_shifts(
    id: Optional[str] = Field(default=None, description="Filter by shift ID, e.g. shf-001"),
    employee_id: Optional[str] = Field(default=None, description="Filter by employee ID"),
    employee_name: Optional[str] = Field(default=None, description="Partial match on employee name"),
    location_id: Optional[str] = Field(default=None, description="Filter by location ID"),
    location_name: Optional[str] = Field(default=None, description="Filter by location name (partial match)"),
    date: Optional[str] = Field(default=None, description="Filter by exact date, YYYY-MM-DD"),
    start_date: Optional[str] = Field(default=None, description="Filter shifts on or after this date, YYYY-MM-DD"),
    end_date: Optional[str] = Field(default=None, description="Filter shifts on or before this date, YYYY-MM-DD"),
    status: Optional[str] = Field(default=None, description="Filter by status: published | draft | pending | cancelled"),
    position_name: Optional[str] = Field(default=None, description="Filter by position name (partial match)"),
) -> list[dict]:
    """List shifts. Optionally filter by employee, location, date range, status, or position."""
    results = _db["shifts"]
    if id:
        results = [r for r in results if r["id"].lower() == id.lower()]
    if employee_id:
        results = [r for r in results if r["employee_id"].lower() == employee_id.lower()]
    if employee_name:
        results = [r for r in results if _match(r, "employee_name", employee_name)]
    if location_id:
        results = [r for r in results if r["location_id"].lower() == location_id.lower()]
    if location_name:
        results = [r for r in results if _match(r, "location_name", location_name)]
    if date:
        results = [r for r in results if r["date"] == date]
    if start_date:
        results = [r for r in results if r["date"] >= start_date]
    if end_date:
        results = [r for r in results if r["date"] <= end_date]
    if status:
        results = [r for r in results if _match(r, "status", status)]
    if position_name:
        results = [r for r in results if _match(r, "position_name", position_name)]
    return results


# ---------------------------------------------------------------------------
# Open Shifts
# ---------------------------------------------------------------------------

@mcp.tool()
def get_open_shifts(
    location_id: Optional[str] = Field(default=None, description="Filter by location ID"),
    position_name: Optional[str] = Field(default=None, description="Filter by position name (partial match)"),
    urgency: Optional[str] = Field(default=None, description="Filter by urgency: low | medium | high | critical"),
    date: Optional[str] = Field(default=None, description="Filter by exact date, YYYY-MM-DD"),
) -> list[dict]:
    """List open shifts needing coverage. Filter by location, position, urgency, or date."""
    results = _db["open_shifts"]
    if location_id:
        results = [r for r in results if r["location_id"].lower() == location_id.lower()]
    if position_name:
        results = [r for r in results if _match(r, "position_name", position_name)]
    if urgency:
        results = [r for r in results if _match(r, "urgency", urgency)]
    if date:
        results = [r for r in results if r["date"] == date]
    return results


# ---------------------------------------------------------------------------
# Time Off Requests
# ---------------------------------------------------------------------------

@mcp.tool()
def get_time_off_requests(
    employee_id: Optional[str] = Field(default=None, description="Filter by employee ID"),
    employee_name: Optional[str] = Field(default=None, description="Partial match on employee name"),
    status: Optional[str] = Field(default=None, description="Filter by status: approved | pending | denied"),
    start_date: Optional[str] = Field(default=None, description="Return requests starting on or after this date, YYYY-MM-DD"),
    end_date: Optional[str] = Field(default=None, description="Return requests starting on or before this date, YYYY-MM-DD"),
) -> list[dict]:
    """List time off requests. Filter by employee, status, or date range."""
    results = _db["time_off_requests"]
    if employee_id:
        results = [r for r in results if r["employee_id"].lower() == employee_id.lower()]
    if employee_name:
        results = [r for r in results if _match(r, "employee_name", employee_name)]
    if status:
        results = [r for r in results if _match(r, "status", status)]
    if start_date:
        results = [r for r in results if r["start_date"] >= start_date]
    if end_date:
        results = [r for r in results if r["start_date"] <= end_date]
    return results


# ---------------------------------------------------------------------------
# Labor Summary
# ---------------------------------------------------------------------------

@mcp.tool()
def get_labor_summary(
    location_id: Optional[str] = Field(default=None, description="Filter by location ID"),
    week_start: Optional[str] = Field(default=None, description="Filter by week start date, YYYY-MM-DD"),
) -> list[dict]:
    """Return labor summary records by location and week. Includes hours, cost, and department breakdown."""
    results = _db["labor_summary"]
    if location_id:
        results = [r for r in results if r["location_id"].lower() == location_id.lower()]
    if week_start:
        results = [r for r in results if r["week_start"] == week_start]
    return results


# ---------------------------------------------------------------------------
# Announcements
# ---------------------------------------------------------------------------

@mcp.tool()
def get_announcements(
    location_id: Optional[str] = Field(default=None, description="Filter to announcements for a specific location ID"),
    category: Optional[str] = Field(default=None, description="Filter by category: schedule | policy | event | general"),
    pinned: Optional[bool] = Field(default=None, description="If true, return only pinned announcements; if false, return only unpinned"),
) -> list[dict]:
    """List team announcements. Filter by location, category, or pinned status."""
    results = _db["announcements"]
    if location_id:
        results = [r for r in results if location_id.lower() in [lid.lower() for lid in r.get("location_ids", [])]]
    if category:
        results = [r for r in results if _match(r, "category", category)]
    if pinned is not None:
        results = [r for r in results if r["pinned"] == pinned]
    return results


# ---------------------------------------------------------------------------
# Schedule View
# ---------------------------------------------------------------------------

@mcp.tool()
def get_schedule(
    location_id: str = Field(description="Location ID to retrieve schedule for, e.g. loc-001"),
    start_date: str = Field(description="Start of date range, YYYY-MM-DD (inclusive)"),
    end_date: str = Field(description="End of date range, YYYY-MM-DD (inclusive)"),
) -> dict:
    """
    Return all published shifts for a location within a date range, grouped by date.
    Useful for viewing a weekly schedule at a glance.
    """
    shifts = [
        r for r in _db["shifts"]
        if r["location_id"].lower() == location_id.lower()
        and r["status"] == "published"
        and start_date <= r["date"] <= end_date
    ]

    grouped: dict[str, list[dict]] = {}
    for shift in sorted(shifts, key=lambda s: (s["date"], s["start_time"])):
        grouped.setdefault(shift["date"], []).append(shift)

    return {
        "location_id": location_id,
        "start_date": start_date,
        "end_date": end_date,
        "total_shifts": len(shifts),
        "schedule": grouped,
    }


# ---------------------------------------------------------------------------
# Write: Create Shift
# ---------------------------------------------------------------------------

@mcp.tool()
def create_shift(
    employee_id: str = Field(description="Employee ID, e.g. emp-004"),
    location_id: str = Field(description="Location ID, e.g. loc-001"),
    position_id: str = Field(description="Position ID, e.g. pos-001"),
    date: str = Field(description="Shift date, YYYY-MM-DD"),
    start_time: str = Field(description="Start time, HH:MM (24-hour)"),
    end_time: str = Field(description="End time, HH:MM (24-hour)"),
    notes: Optional[str] = Field(default=None, description="Optional notes for this shift"),
) -> dict:
    """Create a new shift with status=draft. Returns the created shift record."""
    # Resolve denormalized names from data
    employee = next((e for e in _db["employees"] if e["id"].lower() == employee_id.lower()), None)
    location = next((l for l in _db["locations"] if l["id"].lower() == location_id.lower()), None)
    position = next((p for p in _db["positions"] if p["id"].lower() == position_id.lower()), None)

    if not employee:
        return {"error": f"Employee '{employee_id}' not found."}
    if not location:
        return {"error": f"Location '{location_id}' not found."}
    if not position:
        return {"error": f"Position '{position_id}' not found."}

    # Generate a new ID
    existing_ids = [s["id"] for s in _db["shifts"]]
    nums = [int(sid.split("-")[1]) for sid in existing_ids if sid.startswith("shf-")]
    new_id = f"shf-{(max(nums) + 1):03d}"

    new_shift = {
        "id": new_id,
        "employee_id": employee["id"],
        "employee_name": f"{employee['first_name']} {employee['last_name']}",
        "location_id": location["id"],
        "location_name": location["name"],
        "position_id": position["id"],
        "position_name": position["name"],
        "date": date,
        "start_time": start_time,
        "end_time": end_time,
        "status": "draft",
        "break_minutes": 30,
        "notes": notes or "",
        "created_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
    }
    _db["shifts"].append(new_shift)
    return new_shift


# ---------------------------------------------------------------------------
# Write: Update Shift
# ---------------------------------------------------------------------------

@mcp.tool()
def update_shift(
    id: str = Field(description="Shift ID to update, e.g. shf-001"),
    status: Optional[str] = Field(default=None, description="New status: published | draft | pending | cancelled"),
    start_time: Optional[str] = Field(default=None, description="New start time, HH:MM (24-hour)"),
    end_time: Optional[str] = Field(default=None, description="New end time, HH:MM (24-hour)"),
    notes: Optional[str] = Field(default=None, description="Replace notes text"),
) -> dict:
    """Update a shift's status, times, or notes. Returns the updated record."""
    shift = next((s for s in _db["shifts"] if s["id"].lower() == id.lower()), None)
    if not shift:
        return {"error": f"Shift '{id}' not found."}

    if status is not None:
        shift["status"] = status
    if start_time is not None:
        shift["start_time"] = start_time
    if end_time is not None:
        shift["end_time"] = end_time
    if notes is not None:
        shift["notes"] = notes

    return shift


# ---------------------------------------------------------------------------
# Write: Approve Time Off
# ---------------------------------------------------------------------------

@mcp.tool()
def approve_time_off(
    id: str = Field(description="Time off request ID to approve, e.g. tor-003"),
    reviewed_by: str = Field(description="Name of the manager approving the request"),
) -> dict:
    """Approve a pending time off request. Sets status to approved and records reviewer."""
    request = next((r for r in _db["time_off_requests"] if r["id"].lower() == id.lower()), None)
    if not request:
        return {"error": f"Time off request '{id}' not found."}
    if request["status"] != "pending":
        return {"error": f"Request '{id}' is already '{request['status']}' and cannot be approved."}

    request["status"] = "approved"
    request["reviewed_by"] = reviewed_by
    return request


# ---------------------------------------------------------------------------
# Write: Create Open Shift
# ---------------------------------------------------------------------------

@mcp.tool()
def create_open_shift(
    location_id: str = Field(description="Location ID for the open shift, e.g. loc-001"),
    position_id: str = Field(description="Position ID needed, e.g. pos-001"),
    date: str = Field(description="Date of the open shift, YYYY-MM-DD"),
    start_time: str = Field(description="Start time, HH:MM (24-hour)"),
    end_time: str = Field(description="End time, HH:MM (24-hour)"),
    reason: str = Field(description="Reason: called_out | understaffed | new_shift"),
    urgency: str = Field(description="Urgency level: low | medium | high | critical"),
    notes: Optional[str] = Field(default=None, description="Optional notes about the open shift"),
) -> dict:
    """Create an open shift needing coverage. Returns the new open shift record."""
    location = next((l for l in _db["locations"] if l["id"].lower() == location_id.lower()), None)
    position = next((p for p in _db["positions"] if p["id"].lower() == position_id.lower()), None)

    if not location:
        return {"error": f"Location '{location_id}' not found."}
    if not position:
        return {"error": f"Position '{position_id}' not found."}

    existing_ids = [s["id"] for s in _db["open_shifts"]]
    nums = [int(sid.split("-")[1]) for sid in existing_ids if sid.startswith("opn-")]
    new_id = f"opn-{(max(nums) + 1):03d}" if nums else "opn-001"

    new_open = {
        "id": new_id,
        "location_id": location["id"],
        "location_name": location["name"],
        "position_id": position["id"],
        "position_name": position["name"],
        "date": date,
        "start_time": start_time,
        "end_time": end_time,
        "reason": reason,
        "status": "open",
        "notes": notes or "",
        "urgency": urgency,
    }
    _db["open_shifts"].append(new_open)
    return new_open


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
