from enum import StrEnum

class Status(StrEnum):
    COMPLETED = "Completed",
    CHECKED = "Checked",
    PINGED = "Pinged",
    RESOLVED = "Resolved"