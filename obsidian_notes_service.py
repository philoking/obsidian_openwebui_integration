import os
from datetime import datetime, timedelta
import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

VAULT_PATH = r"/mnt/raid_volume/notes" # Update with your vault location, this is a linux path but windows paths work also e:\notes

def collect_weekly_obsidian_notes():
    today = datetime.now()
    start_of_week = today.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=7) - timedelta(microseconds=1)
    
    weekly_notes = []
    total_files = 0
    markdown_files = 0
    files_this_week = 0

    print(f"Debug: Today's date: {today}")
    print(f"Debug: Start of week: {start_of_week}")
    print(f"Debug: End of week: {end_of_week}")

    for root, dirs, files in os.walk(VAULT_PATH):
        # Skip the _sf folder
        if '_sf' in dirs:
            dirs.remove('_sf')
            
        for file in files:
            total_files += 1
            if file.endswith('.md'):
                markdown_files += 1
                file_path = os.path.join(root, file)
                mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                print(f"Debug: File: {file}, Mod time: {mod_time}")
                
                if start_of_week <= mod_time <= end_of_week:
                    files_this_week += 1
                    with open(file_path, 'r', encoding='utf-8') as note:
                        content = note.read()
                        content = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)
                        weekly_notes.append({"filename": file, "content": content})
                else:
                    print(f"Debug: File {file} not in current week range")

    print(f"Debug: Total files scanned: {total_files}")
    print(f"Debug: Markdown files found: {markdown_files}")
    print(f"Debug: Files modified this week: {files_this_week}")
    return weekly_notes

@app.get("/api/weekly-notes")
async def get_weekly_notes():
    notes = collect_weekly_obsidian_notes()
    return {"notes": notes}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
