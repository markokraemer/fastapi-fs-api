from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import subprocess
from typing import Optional

app = FastAPI()

WORKSPACE_DIR = "your_workspace_directory"  # Set your workspace directory

# Ensure the workspace directory exists
os.makedirs(WORKSPACE_DIR, exist_ok=True)

class FileContent(BaseModel):
    filepath: str
    content: str = ""

class Command(BaseModel):
    command: str

def find_file(filename: str) -> Optional[str]:
    for root, dirs, files in os.walk(WORKSPACE_DIR):
        if filename in files:
            return os.path.join(root, filename)
    return None

@app.post("/create-file")
def create_file(file: FileContent):
    file_path = file.filepath if os.path.isabs(file.filepath) else os.path.join(WORKSPACE_DIR, file.filepath)
    with open(file_path, 'w') as f:
        f.write(file.content)
    return {"message": "File created successfully"}

@app.get("/read-file/{filepath:path}")
def read_file(filepath: str):
    file_path = filepath if os.path.isabs(filepath) else os.path.join(WORKSPACE_DIR, filepath)
    if not os.path.exists(file_path):
        file_path = find_file(os.path.basename(filepath))
        if not file_path:
            raise HTTPException(status_code=404, detail="File not found")
    with open(file_path, 'r') as f:
        content = f.read()
    return {"content": content}

@app.put("/update-file")
def update_file(file: FileContent):
    file_path = file.filepath if os.path.isabs(file.filepath) else os.path.join(WORKSPACE_DIR, file.filepath)
    if not os.path.exists(file_path):
        file_path = find_file(os.path.basename(file.filepath))
        if not file_path:
            raise HTTPException(status_code=404, detail="File not found")
    with open(file_path, 'w') as f:
        f.write(file.content)
    return {"message": "File updated successfully"}

@app.delete("/remove-file/{filepath:path}")
def remove_file(filepath: str):
    file_path = filepath if os.path.isabs(filepath) else os.path.join(WORKSPACE_DIR, filepath)
    if not os.path.exists(file_path):
        file_path = find_file(os.path.basename(filepath))
        if not file_path:
            raise HTTPException(status_code=404, detail="File not found")
    os.remove(file_path)
    return {"message": "File removed successfully"}

@app.post("/execute-command")
def execute_command(cmd: Command):
    try:
        output = subprocess.check_output(cmd.command, shell=True, text=True, cwd=WORKSPACE_DIR)
        return {"output": output}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/get-file-tree")
def get_file_tree():
    file_tree = []
    for root, dirs, files in os.walk(WORKSPACE_DIR):
        for file in files:
            file_tree.append(os.path.join(root, file))
    return {"file_tree": file_tree}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
