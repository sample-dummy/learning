# import os
# from dotenv import load_dotenv

from typing import Annotated

import jwt
from jwt.exceptions import InvalidTokenError

from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Query, Depends, status
from sqlmodel import select
from pwdlib import PasswordHash
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.database import SessionDep
from app.models import User, UserCreate, UserPublic, Token, TokenData, UserRole
from app.config import settings

routerAuth = APIRouter()

# load_dotenv()                         old version of doing this, not doing it now
# secret_key = os.getenv("SECRET_KEY")
# algorithm = os.getenv("ALGORITHM")



password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "login")

def get_password_hash(password):
    return password_hash.hash(password)

def verify_password(entered_password, hashed_password):
    return password_hash.verify(entered_password, hashed_password)

def get_user_from_db(session, email):
    # returns the user from the DB
    statement = select(User).where(User.email == email)
    db_user = session.exec(statement).first()

    return db_user

#rename this to verify_password
def authenticate_user(client_data, session):
    #here, client_data is sent by the client and db_user is the record from the DB
    db_user = get_user_from_db(session, client_data.username)
    if not db_user:
            raise HTTPException(status_code=404, detail = "Invalid details")
    
    is_valid = verify_password(client_data.password, db_user.hashed_password)
    
    if not is_valid:
        raise HTTPException(status_code=404, detail="Re-enter email or password")

    return db_user

def create_access_token(data: dict, expires_delta:timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta

    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

#ouath2_scheme needs to be executed before this function runs and that takes us to the tokenUrl that is /login as can be seen in the beginning of the file
def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail = "Could not validate credentials",
        headers={"WWW-Authenticate":"Bearer"}
    )                        
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email = payload.get("sub")
        #get sends None if it can't find any instead of an exception, so no crashing
        if email is None:
            raise credentials_exception
        token_data =TokenData(email = email)
    except InvalidTokenError:
        raise credentials_exception

    user = get_user_from_db(session, token_data.email)
    if user is None:
        raise credentials_exception

    return user

def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="User not active")
    return current_user

def check_if_admin(current_active_user: Annotated[User, Depends(get_current_active_user)]):
    if current_active_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Forbidden to access")
    return current_active_user
# manually seed the 👉admin with a script and then create a function that manually checks the admin role, gets a Depends(get_current_active_user). pass the function as a dependency 
# to the required endpoints

@routerAuth.post("/auth/register", response_model=UserPublic)
def register_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep):

   
    db_user = get_user_from_db(session, form_data.username)

    if db_user:
        raise HTTPException(
            status_code=400, detail="A user with this email already exists"
        )

    new_user = User(
        email = form_data.username,
        hashed_password = get_password_hash(form_data.password)
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

@routerAuth.post("/login")
def login_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep):
    db_user = authenticate_user(form_data, session)
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    #'sub' is just another variable name to make fetching easier
    #only send the email as data to the token so it doesn't contain any passowrd
    access_token = create_access_token(data = {"sub": db_user.email}, expires_delta = access_token_expires)

    return Token(access_token=access_token, token_type="bearer")




