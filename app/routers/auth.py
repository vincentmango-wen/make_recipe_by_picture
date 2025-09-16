from fastapi import APIRouter, Form, Request, Depends, Response, HTTPException, Security
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from typing import List, Optional
from sqlmodel import Session, select
from passlib.context import CryptContext

from app.database import get_session
from app.models import User
from app.core.auth_cookie import set_login_cookie, clear_login_cookie, get_current_username
from app.core.security import SECRET_KEY, ALGORITHM, pwd_context, create_access_token

from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

templates = Jinja2Templates(directory="app/templates")


# --- サインアップ画面 ---
@router.get("/signup", response_class=HTMLResponse)
def signup_form(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request, "error": None})

# --- サインアップ処理 ---
@router.post("/signup", response_class=HTMLResponse)
def signup(
    request: Request,
    response: Response,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_session),
):
    # 重複チェック
    if db.exec(select(User).where(User.username == username)).first():
        return templates.TemplateResponse("signup.html", {"request": request, "error": "そのユーザー名は既に使われています。"})
    if db.exec(select(User).where(User.email == email)).first():
        return templates.TemplateResponse("signup.html", {"request": request, "error": "そのメールアドレスは既に登録済みです。"})

    # 作成
    user = User(
        username=username,
        email=email,
        hashed_password=pwd_context.hash(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # そのままログイン状態にする（Cookie付与してトップへ）
    redirect = RedirectResponse(url="/", status_code=303)
    set_login_cookie(redirect, user.username)
    return redirect


@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)):
    user = db.exec(select(User).where(User.username == form_data.username)).first()
    if not user or not user.verify_password(form_data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

def get_current_user(
    token: str = Security(oauth2_scheme),
    db: Session = Depends(get_session),
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
def login(username: str = Form(...), password: str = Form(...), response: Response = None, db: Session = Depends(get_session)):
    user = db.exec(select(User).where(User.username == username)).first()
    if not user or not user.verify_password(password):
        return HTMLResponse("ログイン失敗", status_code=401)
    set_login_cookie(response, user.username)
    return RedirectResponse(url="/", status_code=303)

@router.get("/logout")
def logout(response: Response):
    clear_login_cookie(response)
    return RedirectResponse(url="/", status_code=303)

def get_current_user(request: Request, db: Session = Depends(get_session)) -> User | None:
    username = get_current_username(request)
    if not username:
        return None
    return db.exec(select(User).where(User.username == username)).first()