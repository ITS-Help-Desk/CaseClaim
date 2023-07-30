from enum import StrEnum


class Status(StrEnum):
    COMPLETED = "Completed",
    CHECKED = "Checked",
    PINGED = "Pinged",
    RESOLVED = "Resolved"
    KUDOS = "Kudos"
    DONE = "Done"

    @staticmethod
    def from_str(s: str) -> 'Status':
        match (s.lower()):
            case "completed":
                return Status.COMPLETED
            case "checked":
                return Status.CHECKED
            case "pinged":
                return Status.PINGED
            case "resolved":
                return Status.RESOLVED
            case "kudos":
                return Status.KUDOS
            case "done":
                return Status.DONE
