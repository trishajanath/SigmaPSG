# Security Policy

## Secure Coding Practices

This project follows several secure coding practices to ensure the security and integrity of the application.

---

### From `app.py`

#### 1. Input Validation
The application uses `pydantic`'s `field_validator` for validating input data to prevent injection attacks.
```python
from pydantic import BaseModel, field_validator, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    name: str
    password: str

    @field_validator("username", "name")
    def validate_no_special_chars(cls, value):
        if not value.isalnum():
            raise ValueError("Must contain only alphanumeric characters.")
        return value
```

#### 2. HTTPS Configuration
The application forces HTTPS using middleware to ensure secure communication.
```python
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

app.add_middleware(HTTPSRedirectMiddleware)
```

#### 3. Secure Password Storage
Passwords are hashed securely using bcrypt and never stored as plaintext.
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

### From `auth.py`

#### 1. JWT Authentication
The application uses JSON Web Tokens (JWT) for secure authentication and session management.
```python
from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "uE#8r$7zD3*Q8!jN^w@1*Z8^uB5&yE0m"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

### From `users.py`

#### 1. Input Constraints
Input constraints are enforced using pydantic's Field to ensure the integrity of user data.
```python
from pydantic import BaseModel, Field

class User(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str
    password: str = Field(..., min_length=8)
```

#### 2. Separation of Concerns
User data models for input and database storage are separated to enhance security.
```python
class UserInDB(User):
    hashed_password: str
```

### From `Dockerfile`

#### 1. HTTPS Configuration for FastAPI with Docker
The application is configured to use SSL certificates for secure communication.
```Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload", 
     "--ssl-keyfile", "/app/certs/localhost.key", "--ssl-certfile", "/app/certs/localhost.crt"]
```

## Reporting a Vulnerability
If you discover any security vulnerabilities, please report them to the project maintainers immediately. We take security issues seriously and will address them promptly.

## License
This project is licensed under the MIT License.
