from datetime import datetime, timezone
import os

def get_time():
    return datetime.now(timezone.utc).isoformat()

def extension_splitter(attachment: str):
    name, extension = os.path.splitext(attachment) # split into the name and the extension (just the next dot)

    return {"name":name,"extension":extension}