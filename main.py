import time
import uuid
import jwt
from fastapi import FastAPI, Request, Response, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

ALLOWED_ORIGIN = "https://dash-lcgyi0.example.com"
EMAIL = "25f2007453@ds.study.iitm.ac.in"
EXPECTED_ISSUER = "https://idp.exam.local"
EXPECTED_AUDIENCE = "tds-37ns7qli.apps.exam.local"

PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2ok0HspNjGa+2rTLbeuY
cxIP/hg8C6Sb9iwg3yiLAA4HCNpItcbWCSelvbyGuc3EbNy4xFyf5Cbj5DHJMID
EkRy0gyd2gIIBOUBJ8S63uGcnRpObh9NFatfNwheKuzPuVNldu6A9cNteNpXc
WyJjG2axVfmq7i6SuKr1JoWYG7xTTAvKPujS140tsQf03h5NepzdfXpr28oNnzfw
ed+zcLR6BcmNno/WVfJ4xyCLSF0bC0gdTgw6PdaChd1l9VDetJZVEgC5tkyvXsFI
SI6iyrYjKR0NEBSqq4XKadEjsCs4F1Rncs4LLgnit7GlkL9Mce3b0wGLS9/7ZIX
dQIDAQAB
-----END PUBLIC KEY-----"""

class TokenRequest(BaseModel):
    token: str

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
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
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

@app.post("/verify")
def verify_token(payload: TokenRequest):
    try:
        # Decode without strict options first to check signature, issuer, audience, and exp manually if needed
        decoded = jwt.decode(
            payload.token,
            PUBLIC_KEY,
            algorithms=["RS256"],
            audience=EXPECTED_AUDIENCE,
            issuer=EXPECTED_ISSUER,
            options={"verify_exp": True}
        )
        return {
            "valid": True,
            "email": decoded.get("email", ""),
            "sub": decoded.get("sub", ""),
            "aud": decoded.get("aud", "")
        }
    except Exception as e:
        return JSONResponse(status_code=401, content={"valid": False})