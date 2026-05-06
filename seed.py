import sys
import os
import argparse
import logging
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.masters import UserStatus, Skill, Status, Priority
from app.models.roles import Role
from app.models.master import MasterLookup
from app.models.user import User

from app.models import project, issue, milestone, task, timelog, user, roles, document, template, timesheet, task_list, team, audit

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

_UNIFIED_STATUS_DEFS = {
    "Open":         {"label": "Open",         "color": "#6366f1", "icon": "pi-circle"},
    "In Progress":  {"label": "In Progress",  "color": "#0ea5e9", "icon": "pi-spin pi-spinner"},
    "In Review":    {"label": "In Review",    "color": "#f59e0b", "icon": "pi-eye"},
    "To Be Tested": {"label": "To Be Tested", "color": "#a855f7", "icon": "pi-check-square"},
    "Completed":    {"label": "Completed",    "color": "#10b981", "icon": "pi-check"},
    "On Hold":      {"label": "On Hold",      "color": "#f97316", "icon": "pi-pause"},
    "Closed":       {"label": "Closed",       "color": "#64748b", "icon": "pi-lock"},
    "Re-Opened":    {"label": "Re-Opened",    "color": "#ef4444", "icon": "pi-undo"},
    "Active":       {"label": "Active",       "color": "#10b981", "icon": "pi-play"},
    "Cancelled":    {"label": "Cancelled",    "color": "#ef4444", "icon": "pi-times"},
    "Planning":     {"label": "Planning",     "color": "#8b5cf6", "icon": "pi-calendar"},
}

_UNIFIED_PRIORITIES = {
    "Critical":     {"label": "Critical",     "color": "#7f1d1d", "icon": "pi-bolt"},
    "High":         {"label": "High",         "color": "#ef4444", "icon": "pi-arrow-up"},
    "Medium":       {"label": "Medium",       "color": "#f59e0b", "icon": "pi-minus"},
    "Low":          {"label": "Low",          "color": "#22c55e", "icon": "pi-arrow-down"},
}

_CLASSIFICATIONS = [
    ("None", "None", "#94a3b8"), ("Security", "Security", "#ef4444"), ("CrashHang", "Crash/Hang", "#7f1d1d"),
    ("DataLoss", "Data Loss", "#b91c1c"), ("Performance", "Performance", "#f97316"), 
    ("UIUsability", "UI/UX Usability", "#a855f7"), ("OtherBugs", "Other Bugs", "#6366f1"),
    ("NewFeature", "Feature (New)", "#0ea5e9"), ("Enhancement", "Enhancement", "#10b981"),
]

_BILLING_TYPES = [
    ("Billable", "Billable", "#10b981"), ("NonBillable", "Non-Billable", "#64748b"), ("Internal", "Internal", "#6366f1"),
]

_MAPPINGS = {
    "TaskStatus":          ["Open", "In Progress", "In Review", "To Be Tested", "Completed", "On Hold", "Closed"],
    "IssueStatus":         ["Open", "In Progress", "In Review", "To Be Tested", "Closed", "Re-Opened"],
    "ProjectStatus":       ["Active", "On Hold", "Completed", "Cancelled"],
    "TaskPriority":        ["Critical", "High", "Medium", "Low"],
    "IssueSeverity":       ["Critical", "High", "Medium", "Low"],
    "ProjectBillingModel": ["Fixed Bid", "Time & Materials", "Internal", "Retainer"],
    "ProjectType":         ["Client Project", "Internal Project", "Research", "Support"],
}

_UNIFIED_PROJECT_DEFS = {
    "Fixed Bid":        {"label": "Fixed Bid",        "color": "#6366f1", "icon": "pi-wallet"},
    "Time & Materials": {"label": "Time & Materials", "color": "#0ea5e9", "icon": "pi-clock"},
    "Internal":         {"label": "Internal",         "color": "#64748b", "icon": "pi-home"},
    "Retainer":         {"label": "Retainer",         "color": "#f59e0b", "icon": "pi-sync"},
    "Client Project":   {"label": "Client Project",   "color": "#10b981", "icon": "pi-briefcase"},
    "Internal Project": {"label": "Internal Project", "color": "#6366f1", "icon": "pi-building"},
    "Research":         {"label": "Research",         "color": "#a855f7", "icon": "pi-search"},
    "Support":          {"label": "Support",          "color": "#f97316", "icon": "pi-info-circle"},
}

REQUIRED_STATUSES = list(set(_MAPPINGS["TaskStatus"] + _MAPPINGS["IssueStatus"] + _MAPPINGS["ProjectStatus"] + ["Planning"]))
REQUIRED_PRIORITIES = list(_UNIFIED_PRIORITIES.keys())

MASTER_LOOKUPS_SEED_DATA = []

for category, keys in _MAPPINGS.items():
    for index, key in enumerate(keys, 1):
        is_status = "Status" in category
        is_project = "Project" in category and category not in ["ProjectStatus"]
        
        if is_status:
            src = _UNIFIED_STATUS_DEFS
        elif is_project:
            src = _UNIFIED_PROJECT_DEFS
        else:
            src = _UNIFIED_PRIORITIES
            
        lookup = {
            "category": category,
            "value": key.replace(" ", "").replace("-", ""),
            "label": src[key]["label"],
            "color": src[key]["color"],
            "order_index": index,
        }
        if "icon" in src[key]:
            lookup["icon"] = src[key]["icon"]
        MASTER_LOOKUPS_SEED_DATA.append(lookup)

for index, (val, label, color) in enumerate(_CLASSIFICATIONS, 1):
    MASTER_LOOKUPS_SEED_DATA.append({"category": "IssueClassification", "value": val, "label": label, "color": color, "order_index": index})

for index, (val, label, color) in enumerate(_BILLING_TYPES, 1):
    MASTER_LOOKUPS_SEED_DATA.append({"category": "BillingType", "value": val, "label": label, "color": color, "order_index": index})


def reset_database():
    logger.info("Dropping all tables for fresh creation...")
    Base.metadata.drop_all(bind=engine)
    logger.info("Creating all tables...")
    Base.metadata.create_all(bind=engine)


def create_database():
    logger.info("Creating all tables if they don't exist...")
    Base.metadata.create_all(bind=engine)


def seed_simple_records(db: Session, model, items, display_name):
    
    existing = {obj.name for obj in db.query(model).all()}
    missing = [name for name in items if name not in existing]
    if missing:
        db.add_all([model(name=name) for name in missing])
        db.commit()
        logger.info(f"Added {display_name}: {missing}")
    else:
        logger.info(f"{display_name} already seeded.")


def seed_master_lookups(db: Session):
    inserted = 0
    skipped = 0
    for row in MASTER_LOOKUPS_SEED_DATA:
        existing = db.execute(
            select(MasterLookup).where(
                MasterLookup.category == row["category"],
                MasterLookup.value == row["value"],
            )
        ).scalar_one_or_none()

        if existing:
            skipped += 1
            continue

        db.add(MasterLookup(**row))
        inserted += 1

    db.commit()
    logger.info(f"MasterLookups: {inserted} inserted, {skipped} already exist.")


def seed_roles(db: Session) -> dict:
    canonical_roles = ["Super Admin", "Admin", "Team Lead", "Project Manager", "Employee"]
    roles_dict = {}
    for r_name in canonical_roles:
        role = db.query(Role).filter(Role.name == r_name).first()
        if not role:
            role = Role(name=r_name, permissions={})
            db.add(role)
            db.commit()
            db.refresh(role)
            logger.info(f"Added Role: {r_name}")
        roles_dict[r_name] = role
    return roles_dict


def seed_admin_user(db: Session, roles_dict: dict):
    email = "test1@technorucspltd.onmicrosoft.com"
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            email=email,
            first_name="Test",
            last_name="Admin",
            username="test_admin",
            public_id="test_admin_uid",
            employee_id="EMP_TEST",
            role_id=roles_dict["Admin"].id,
            is_active=True
        )
        db.add(user)
        db.commit()
        logger.info(f"Created default admin user: {email}")
    else:
        logger.info(f"Admin user already exists: {email}")


def seed_all(reset=False):
    if reset:
        reset_database()
    else:
        create_database()

    with SessionLocal() as db:

        seed_simple_records(db, UserStatus, ["Active", "Inactive", "Pending", "Onboarding", "On Leave"], "User Statuses")
        seed_simple_records(db, Status, REQUIRED_STATUSES, "General Statuses")
        seed_simple_records(db, Priority, ["Low", "Medium", "High", "Critical"], "Priorities")
        seed_simple_records(db, Skill, ["React", "Python", "FastAPI", "UI/UX Design", "Node.js", ".NET", "DevOps", "Project Management", "Data Analytics"], "Skills")
        

        roles_dict = seed_roles(db)
        

        seed_master_lookups(db)
        

        seed_admin_user(db, roles_dict)

    logger.info("Database seeding completed successfully.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed the TechnoRUCS Database.")
    parser.add_argument("--reset", action="store_true", help="Drop and recreate all tables before seeding.")
    args = parser.parse_args()
    
    seed_all(reset=args.reset)
