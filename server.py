from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from analysis import analyze_project, generate_graphs
import os
import shutil
import tempfile
import matplotlib.pyplot as plt


app = FastAPI()
@app.post("/analyze")
def analyze_code(file: UploadFile = File(...)):
    # ... ניתוח הקוד, יצירת הגרף
    output_path = "graphs/function_lengths.png"
    plt.savefig(output_path)
    return FileResponse(output_path, media_type="image/png", filename="function_lengths.png")

@app.post("/alerts")
async def alerts(files: list[UploadFile] = File(...)):
    with tempfile.TemporaryDirectory() as tmpdir:
        for f in files:
            contents = await f.read()
            path = os.path.join(tmpdir, f.filename)
            with open(path, "wb") as out:
                out.write(contents)

        report = analyze_project(tmpdir)
        return JSONResponse(content=report["issues"])
