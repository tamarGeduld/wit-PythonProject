import os

from fastapi import FastAPI, UploadFile, File, Query
from fastapi.responses import JSONResponse,FileResponse
import uvicorn

from analyzer import analyze_zip
from db import analysis_collection

from matplotlibFunc import get_all_function_lengths, generate_function_length_histogram, \
    generate_problem_type_pie_chart, generate_problem_count_bar_chart, generate_issue_trend_graph

app = FastAPI()

@app.post("/alert")
async def alert(zip_file: UploadFile = File(...)):
    zip_bytes = await zip_file.read()
    results = analyze_zip(zip_bytes, save_to_db=True)
    return {"results": results}


@app.post("/analyzer")
async def analyze(zip_file: UploadFile = File(...)):
    zip_bytes = await zip_file.read()
    results = analyze_zip(zip_bytes, save_to_db=False)

    # Get lengths of all functions for histogram visualization
    all_lengths = get_all_function_lengths(results)

    # Count how many issues of each type exist in total
    file_distribution = {
        "long_functions": sum(len(file["long_functions"]) for file in results.values()),
        "file_too_long": sum(len(file["file_too_long"]) for file in results.values()),
        "unused_variables": sum(len(file["unused_variables"]) for file in results.values()),
        "missing_docstrings": sum(len(file["missing_docstrings"]) for file in results.values()),
        "non_english_variable_names": sum(len(file["non_english_variable_names"]) for file in results.values()),
    }

    # Count how many total issues exist per file (for bar chart)
    long_vs_short = {
        filename: (
            len(file["long_functions"]) +
            len(file["file_too_long"]) +
            len(file["unused_variables"]) +
            len(file["missing_docstrings"]) +
            len(file["non_english_variable_names"])
        )
        for filename, file in results.items()
    }

    # Generate visualizations and save them as image files
    histogram_path = generate_function_length_histogram(all_lengths)
    pie_chart_path = generate_problem_type_pie_chart(file_distribution)
    bar_chart_path = generate_problem_count_bar_chart(long_vs_short)

    records = list(analysis_collection.find().sort("timestamp", 1))
    line_chart_path = generate_issue_trend_graph(records)

    return {
        "histogram_url": f"/graph/image?path={histogram_path}",
        "pie_chart_url": f"/graph/image?path={pie_chart_path}",
        "bar_chart_url": f"/graph/image?path={bar_chart_path}",
        "line_chart_url": f"/graph/image?path={line_chart_path}"
    }

@app.get("/graph/image")
async def get_graph_image(path: str):
    if os.path.exists(path):
        return FileResponse(path, media_type="image/png")
    return JSONResponse({"error": "File not found"}, status_code=404)

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)

