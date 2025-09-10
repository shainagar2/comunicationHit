from fastapi import APIRouter, Depends, Response, status
from app.config import get_settings, Settings

router = APIRouter()

# GET /requirements -> 200 OK + empty JSON
@router.get("/requirements", tags=["public"])
async def get_requirements(_: Settings = Depends(get_settings)):
    return {}

# GET /sign-in -> 200 OK + empty JSON
@router.get("/sign-in", tags=["auth"])
async def get_sign_in(_: Settings = Depends(get_settings)):
    return {}

# POST /sign-out -> 204 No Content (no body)
@router.post("/sign-out", status_code=status.HTTP_204_NO_CONTENT, tags=["auth"])
async def post_sign_out(_: Settings = Depends(get_settings)):
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# GET /register -> 200 OK + empty JSON
@router.get("/register", tags=["auth"])
async def get_register(_: Settings = Depends(get_settings)):
    return {}

# POST /send-verification -> 204 No Content (no body)
@router.post("/send-verification", status_code=status.HTTP_204_NO_CONTENT, tags=["auth"])
async def post_send_verification(_: Settings = Depends(get_settings)):
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# GET /verify -> 200 OK + empty JSON
@router.get("/verify", tags=["auth"])
async def get_verify(_: Settings = Depends(get_settings)):
    return {}

# GET /change-pswd -> 200 OK + empty JSON
@router.get("/change-pswd", tags=["auth"])
async def get_change_pswd(_: Settings = Depends(get_settings)):
    return {}

# GET /get-customers -> 200 OK + empty JSON
@router.get("/get-customers", tags=["records"])
async def get_customers(_: Settings = Depends(get_settings)):
    return {}

# POST /create_record -> 204 No Content (no body)
@router.post("/create_record", status_code=status.HTTP_204_NO_CONTENT, tags=["records"])
async def post_create_record(_: Settings = Depends(get_settings)):
    return Response(status_code=status.HTTP_204_NO_CONTENT)