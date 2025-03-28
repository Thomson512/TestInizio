import subprocess
import json
import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from starlette.requests import Request

PYTHON = sys.executable
app = FastAPI()
current_results = []

@app.get("/", response_class=HTMLResponse)
@app.head("/")
async def read_root(request: Request):
    template_path = os.path.join("templates", "index.html")
    print(f"[LOG] Načítám šablonu: {template_path}")
    return FileResponse("index.html")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/search")
def search(query: str):
    global current_results
    print("[LOG] Dekorátor search - vstup, použitý Python: ", PYTHON)

    try:
        result = subprocess.run(
            [PYTHON, "scraper.py", query],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        if result.returncode != 0:
            print(">>> stderr:", result.stderr)
            return {"[ERR]": "Chyba při spouštění scraperu", "detail": result.stderr}

        output = result.stdout.strip()
        #Debug: print(">>> stdout:", output)
        print("[LOG] Vráceny výsledky z scraper.py ")

        if output:
            print("[LOG] Validace výsledků z scraper.py - OK ")
            current_results = json.loads(output)
            return current_results
        else:
            return {"[ERR]": "Nezískali jsme žádné výsledky"}

    except Exception as e:
        return {"[ERR]": "Obecná chyba", "detail": str(e)}

@app.get("/export")
def export():
    try:
        if not current_results:
            return {"[ERR]": "Nebyly nalezeny žádné výsledky k exportu"}

        filename = "results.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(current_results, f, ensure_ascii=False, indent=2)

        return FileResponse(filename, media_type='application/json', filename=filename)

    except Exception as e:
        return {"[ERR]": "Chyba při exportu", "detail": str(e)}
