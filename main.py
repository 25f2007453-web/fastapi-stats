import time
import uuid
from fastapi import FastAPI, Request, Response, Query
from fastapi.responses import JSONResponse

app = FastAPI()

ALLOWED_ORIGIN = "https://dash-lcgyi0.example.com"
EMAIL = "25f2007453@ds.study.iitm.ac.in"

@app.middleware("http")
async def add_custom_headers_and_cors(request: Request, call_next):
    start_time = time.time()
    request_id = str(uuid.uuid4())
    origin = request.headers.get("origin")
    
    if request.method == "OPTIONS":
        response = Response()
        response.headers["X-Request-ID"] = request_id
        if origin == ALLOWED_ORIGIN:
            response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
            response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "*"
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.6f}"
        return response

    try:
        response = await call_next(request)
    except Exception as exc:
        process_time = time.time() - start_time
        response = JSONResponse({"detail": str(exc)}, status_code=500)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.6f}"
        if origin == ALLOWED_ORIGIN:
            response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
        return response

    process_time = time.time() - start_time
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{process_time:.6f}"
    
    if origin == ALLOWED_ORIGIN:
        response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN

    return response

@app.get("/stats")
def get_stats(values: str = Query(...)):
    try:
        nums = [int(x.strip()) for x in values.split(",") if x.strip() != ""]
    except ValueError:
        return {"error": "Invalid integer format"}, 400
    
    if not nums:
        return {"error": "Empty values list"}, 400

    return {
        "email": EMAIL,
        "count": len(nums),
        "sum": sum(nums),
        "min": min(nums),
        "max": max(nums),
        "mean": sum(nums) / len(nums)
    }
