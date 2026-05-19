import logging
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.masters import UserStatus, Skill, Status, Priority
from app.models.roles import Role
from app.models.master import MasterLookup

logger = logging.getLogger("app.seeding")
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

def seed_simple_records(db: Session, model, data, name_field="name"):
    added = 0
    skipped = 0
    for name in data:
        existing = db.query(model).filter(getattr(model, name_field) == name).first()
        if not existing:
            db.add(model(**{name_field: name}))
            added += 1
        else:
            skipped += 1
    db.commit()
    return added, skipped

def seed_master_lookups(db: Session):
    lookups = {
        "ProjectStatus":      ["Planning", "Active", "In Progress", "On Hold", "Completed", "Closed", "Cancelled"],
        "TaskStatus":         ["Open", "In Progress", "In Review", "Completed", "Cancelled", "On Hold"],
        "TaskPriority":       ["Low", "Medium", "High", "Critical"],
        "IssueStatus":        ["Open", "In Progress", "Hold", "Cancelled", "Resolved", "Re-Open", "Not a defect", "Closed"],
        "IssueSeverity":      ["Low", "Medium", "High", "Critical", "Blocker", "Show Stopper"],
        "IssueClassification":["None", "Security", "Crash/Hang", "Data Loss", "Performance", "UI/UX Usability", "Other Bugs", "Feature (New)", "Enhancement"],
        "ProjectType":        ["Internal", "External"],
        "ProjectBillingModel":["T&M", "Fixed Price", "Retainer", "Non-Billable"],
        "TaskBillingType":    ["Billable", "Non-Billable", "Internal"],
        "MilestoneStatus":    ["Planning", "Active", "In Progress", "On Hold", "Completed", "Cancelled"],
    }

    from sqlalchemy import text
    dup_check = db.execute(text(
        "SELECT category, value, MIN(id) as keep_id "
        "FROM master_lookups "
        "GROUP BY category, value "
        "HAVING COUNT(*) > 1"
    )).fetchall()

    deleted_count = 0
    db.query(MasterLookup).filter(
        MasterLookup.category == "ProjectType",
        MasterLookup.label.in_(["Internal Project", "internal project", "Internal project"])
    ).delete(synchronize_session=False)
    
    for row in dup_check:
        cat, val, keep_id = row.category, row.value, row.keep_id
        dups = db.query(MasterLookup).filter(
            MasterLookup.category == cat,
            MasterLookup.value == val,
            MasterLookup.id != keep_id
        ).all()
        for dup in dups:
            db.delete(dup)
            deleted_count += 1
    if deleted_count:
        db.commit()
        logger.info(f"Deduplication: removed {deleted_count} duplicate MasterLookup rows.")

    # Safe Defect Status Migration
    new_issue_statuses = ["Open", "In Progress", "Hold", "Cancelled", "Resolved", "Re-Open", "Not a defect", "Closed"]
    new_status_ids = {}
    for idx, name in enumerate(new_issue_statuses):
        existing = db.query(MasterLookup).filter(
            MasterLookup.category == "IssueStatus",
            MasterLookup.value == name
        ).first()
        if not existing:
            new_status = MasterLookup(category="IssueStatus", label=name, value=name, order_index=idx)
            db.add(new_status)
            db.flush()
            new_status_ids[name] = new_status.id
        else:
            new_status_ids[name] = existing.id
            existing.order_index = idx

    from app.models.issue import Issue
    existing_lookups = db.query(MasterLookup).filter(MasterLookup.category == "IssueStatus").all()
    for l in existing_lookups:
        if l.value not in new_issue_statuses:
            target_name = None
            if l.value in ["Active", "In Review"]:
                target_name = "In Progress"
            elif l.value == "To Be Tested":
                target_name = "Resolved"
            elif l.value == "Re-Opened":
                target_name = "Re-Open"
            elif l.value == "On Hold":
                target_name = "Hold"
            
            if target_name and target_name in new_status_ids:
                target_id = new_status_ids[target_name]
                db.query(Issue).filter(Issue.status_id == l.id).update(
                    {Issue.status_id: target_id},
                    synchronize_session=False
                )
            db.delete(l)
    db.commit()

    total_inserted = 0
    total_skipped = 0
    for category, values in lookups.items():
        for idx, val in enumerate(values):
            existing = db.query(MasterLookup).filter(
                MasterLookup.category == category,
                MasterLookup.value == val
            ).first()
            if not existing:
                db.add(MasterLookup(category=category, label=val, value=val, order_index=idx))
                total_inserted += 1
            else:
                total_skipped += 1
    db.commit()
    logger.info(f"MasterLookups: {total_inserted} inserted, {total_skipped} already exist.")

def seed_roles(db: Session):
    canonical_roles = ["Admin", "Team Lead", "Project Manager", "Employee"]
    
    # Full permissions for Admin
    admin_perms = {
        'proj-view': True, 'proj-create': True, 'proj-edit': True, 'proj-delete': True,
        'task-view': True, 'task-create': True, 'task-edit': True, 'task-delete': True, 'task-assign': True,
        'issue-view': True, 'issue-create': True, 'issue-edit': True, 'issue-delete': True,
        'milestone-view': True, 'milestone-create': True, 'milestone-edit': True, 'milestone-delete': True,
        'time-view': True, 'time-create': True, 'time-edit': True, 'time-delete': True, 'timesheet-approve': True,
        'user-view': True, 'user-create': True, 'user-edit': True, 'user-delete': True,
        'team-view': True, 'team-create': True, 'team-edit': True, 'team-delete': True,
        'report-view': True, 'report-export': True,
        'settings-view': True, 'settings-edit': True, 'role-manage': True, 'automation-manage': True
    }

    for r_name in canonical_roles:
        role = db.query(Role).filter(Role.name == r_name).first()
        if not role:
            perms = admin_perms if r_name == "Admin" else {}
            db.add(Role(name=r_name, description=f"{r_name} role", permissions=perms))
            logger.info(f"Added Role: {r_name}")
        elif r_name == "Admin" and (not role.permissions or role.permissions == {}):
            role.permissions = admin_perms
            db.add(role)
            logger.info("Updated existing Admin role with default permissions")
            
    db.commit()


def seed_all(reset=False):
    if reset:
        logger.warning("Reset requested - Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        u_added, u_skip = seed_simple_records(db, UserStatus, ["Active", "Inactive", "Pending", "Onboarding", "On Leave"])
        if u_added: logger.info(f"Added User Statuses: {u_added}")
        
        s_added, s_skip = seed_simple_records(db, Status, ["Open", "In Progress", "In Review", "Completed", "Cancelled", "On Hold", "Planning", "Active", "Closed", "To Be Tested", "Re-Opened"])
        if s_added: logger.info(f"Added General Statuses: {s_added}")
        
        p_added, p_skip = seed_simple_records(db, Priority, ["Low", "Medium", "High", "Critical"])
        if p_added: logger.info(f"Added Priorities: {p_added}")
        
        sk_added, sk_skip = seed_simple_records(db, Skill, ["React", "Python", "FastAPI", "UI/UX Design", "Node.js", ".NET", "DevOps", "Project Management", "Data Analytics"])
        if sk_added: logger.info(f"Added Skills: {sk_added}")
        
        seed_roles(db)
        seed_master_lookups(db)
        
    logger.info("Database seeding completed successfully.")
