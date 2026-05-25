import random
import string
from datetime import datetime

def generate_public_id(prefix: str, length: int = 6) -> str:
    chars = string.ascii_uppercase + string.digits
    random_str = ''.join(random.choices(chars, k=length))
    return f"{prefix}{random_str}"

def get_project_initials(name: str) -> str:
    if not name: return "PRJ"
    words = name.strip().split()
    if len(words) == 1:
        return words[0][:2].upper()
    return "".join(w[0] for w in words[:2]).upper()

def get_next_project_id(db, project_model) -> str:
    year = datetime.now().year
    prefix = f"PRJ-{year}-"
    latest = db.query(project_model).filter(project_model.public_id.like(f"{prefix}%")).order_by(project_model.id.desc()).first()
    if latest and latest.public_id:
        try:
            num = int(latest.public_id.replace(prefix, ""))
        except ValueError:
            num = 0
    else:
        num = 0
    return f"{prefix}{num + 1:03d}"

def get_next_sequence_id(db, model_class, project_name: str, project_id: int, separator: str, is_padded: bool = False, model_name: str = "") -> str:
    initials = get_project_initials(project_name)
    prefix = f"{initials}-{separator}"
    
    query = db.query(model_class.public_id).filter(model_class.public_id.like(f"{prefix}%"))
    if hasattr(model_class, 'project_id'):
        query = query.filter(model_class.project_id == project_id)
        
    all_ids = query.all()
    
    max_num = 0
    for (pid,) in all_ids:
        if pid:
            val = pid.replace(prefix, "")
            try:
                n = int(val)
                if n > max_num:
                    max_num = n
            except ValueError:
                pass
                
    num = max_num + 1
    if is_padded:
        return f"{prefix}{num:03d}"
    return f"{prefix}{num}"
