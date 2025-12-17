from enum import Enum

class UserRole(str, Enum):
    admin = "admin"
    operator = "operator"

class CampaignStatus(str, Enum):
    draft = "draft"
    scheduled = "scheduled"
    sending = "sending"
    done = "done"
    failed = "failed"
    canceled = "canceled"

class CampaignRunStatus(str, Enum):
    created = "created"
    queued = "queued"
    ready = "ready"
    done = "done"
    failed = "failed"
    canceled = "canceled"