def sanitize_for_log(value: object) -> str:
    return str(value).replace("\r", "").replace("\n", "")
