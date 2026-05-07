from datetime import datetime, timezone
from pydantic import BaseModel, field_serializer

class BaseSchema(BaseModel):
    @field_serializer('*', mode='wrap', check_fields=False)
    def serialize_dt(self, value, handler, _info):
        if isinstance(value, datetime):
            if value.tzinfo is None:
                return value.replace(tzinfo=timezone.utc).isoformat().replace('+00:00', 'Z')
            return value.isoformat().replace('+00:00', 'Z')
        return handler(value)
