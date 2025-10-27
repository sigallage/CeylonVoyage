from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from app.models.user import UserCreate, UserResponse, Token
from app.utils.security import get_password_hash, create_access_token
from app.database import get_database
from bson import ObjectId

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate):
    """
    Register a new user
    
    - **email**: valid email address
    - **username**: unique username (3-50 characters)
    - **password**: password (minimum 6 characters)
    - **full_name**: optional full name
    """
    db = get_database()
    users_collection = db.users
    
    # Check if email already exists
    existing_user = await users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    existing_username = await users_collection.find_one({"username": user.username})
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user document
    now = datetime.utcnow()
    user_dict = {
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
        "hashed_password": get_password_hash(user.password),
        "is_active": True,
        "is_verified": False,
        "created_at": now,
        "updated_at": now
    }
    
    # Insert user into database
    result = await users_collection.insert_one(user_dict)
    
    # Retrieve the created user
    created_user = await users_collection.find_one({"_id": result.inserted_id})
    
    # Convert ObjectId to string for response
    created_user["_id"] = str(created_user["_id"])
    
    return UserResponse(**created_user)


@router.post("/login", response_model=Token)
async def login(username: str, password: str):
    """
    Login with username and password to get access token
    
    - **username**: username or email
    - **password**: user password
    """
    from app.utils.security import verify_password
    
    db = get_database()
    users_collection = db.users
    
    # Find user by username or email
    user = await users_collection.find_one({
        "$or": [
            {"username": username},
            {"email": username}
        ]
    })
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": user["username"]})
    
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
async def get_current_user(token: str):
    """
    Get current user information
    
    - **token**: JWT access token
    """
    from app.utils.security import verify_token
    
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    db = get_database()
    users_collection = db.users
    
    user = await users_collection.find_one({"username": username})
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user["_id"] = str(user["_id"])
    return UserResponse(**user)
