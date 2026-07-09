from datetime import datetime, timezone
import os
from rich import print

VERSION = "0.0.1"
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_FILE_PATH = os.path.join(CURRENT_DIR, "sushiSQL.db")

def get_time():
    return datetime.now(timezone.utc).isoformat()

def extension_splitter(attachment: str):
    name, extension = os.path.splitext(attachment) # split into the name and the extension (just the next dot)

    return {"name":name,"extension":extension}


def test_warning(text:str, head: str):
    print("[bold yellow]" + head + "[/bold yellow]: " + text)

def test_alert(text:str, head: str):
    print("[bold red]" + head + "[/bold red]: " + text)

def test_information(text:str):
    print("[bold]\\[Information][/bold]: " + text)

def test_succeed(text:str, head: str):
    print("[bold green]" + head + "[/bold green]: " + text)