from fastapi import APIRouter, Depends, Response, status, HTTPException, Query
from app.config import get_settings, Settings
from app.db import get_db
from sqlalchemy import text
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/healthz", tags=["internal"])
async def healthz(_: Settings = Depends(get_settings)):
    return {"status": "ok"}

# --- Auth placeholders (כבר היו) ---
@router.get("/sign-in", tags=["auth"])
async def get_sign_in(_: Settings = Depends(get_settings)):
    return {"status": "OK", "message": "Hello"}

@router.post("/sign-out", status_code=status.HTTP_204_NO_CONTENT, tags=["auth"])
async def post_sign_out(_: Settings = Depends(get_settings)):
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/change-pswd", tags=["auth"])
async def get_change_pswd(_: Settings = Depends(get_settings)):
    return {}

# --- Customers minimal CRUD ---

def _list_customers(db: Session, limit: int, offset: int):
    # לא מניחים שמות שדות – מחזירים את כל העמודות שקיימות
    stmt = text("SELECT * FROM customers LIMIT :limit OFFSET :offset")
    res = db.execute(stmt, {"limit": limit, "offset": offset})
    return [dict(row) for row in res.mappings().all()]

def _get_customer_columns(db: Session):
    # שולף שמות עמודות כדי לדעת מה מותר להכניס
    res = db.execute(text("SHOW COLUMNS FROM customers"))
    cols = [row[0] for row in res.all()]
    skip = {"id", "created_at", "updated_at", "created_on", "updated_on"}
    return [c for c in cols if c not in skip]

@router.get("/customers", tags=["records"])
async def get_customers(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    try:
        data = _list_customers(db, limit, offset)
        return {"items": data, "count": len(data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")

@router.post("/customers", status_code=status.HTTP_201_CREATED, tags=["records"])
async def create_customer(payload: dict, db: Session = Depends(get_db)):
    """
    הכנסת רשומת לקוח בצורה גנרית:
    מזהים אילו עמודות קיימות בטבלת customers ומכניסים רק מה שקיים בפיילוד.
    """
    allowed = _get_customer_columns(db)
    data = {k: v for k, v in payload.items() if k in allowed}
    if not data:
        raise HTTPException(status_code=400, detail=f"No valid fields. Allowed: {allowed}")

    cols = ", ".join(f"`{c}`" for c in data.keys())
    params = ", ".join(f":{c}" for c in data.keys())
    stmt = text(f"INSERT INTO customers ({cols}) VALUES ({params})")
    try:
        db.execute(stmt, data)
        db.commit()
        rid = db.execute(text("SELECT LAST_INSERT_ID() AS id")).mappings().first()
        return {"id": rid["id"] if rid else None, "inserted": data}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"DB insert error: {e}")

# שמות ישנים מהדמו – נשאיר כאליאסים
@router.get("/get-customers", tags=["records"])
async def get_customers_alias(limit: int = 50, offset: int = 0, db: Session = Depends(get_db)):
    return await get_customers(limit=limit, offset=offset, db=db)

@router.post("/create_record", status_code=status.HTTP_201_CREATED, tags=["records"])
async def create_record_alias(payload: dict, db: Session = Depends(get_db)):
    return await create_customer(payload=payload, db=db)
