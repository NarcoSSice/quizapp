import enum


class ExportType(str, enum.Enum):
    json = "json"
    csv = "csv"
