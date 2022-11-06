from datetime import datetime

def format_nanoseconds(nanoseconds: int):
    dt = datetime.fromtimestamp(nanoseconds / 1e9)
    return '{}.{:09.0f}'.format(dt.strftime('%Y-%m-%dT%H:%M:%S'), nanoseconds % 1e9)