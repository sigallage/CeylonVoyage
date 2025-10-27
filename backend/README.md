# CeylonVoyage Backend

FastAPI backend with MongoDB and JWT authentication.

## Features

- User registration (signup)
- User authentication (login) with JWT tokens
- Password hashing with bcrypt
- MongoDB integration with Motor (async)
- Input validation with Pydantic
- CORS enabled for frontend integration

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   - Copy `.env.example` to `.env`
   - Update the values in `.env` (especially `SECRET_KEY` and `MONGODB_URL`)

3. **Run MongoDB:**
   - Make sure MongoDB is running on your system
   - Default: `mongodb://localhost:27017`

4. **Run the application:**
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Access the API:**
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

## API Endpoints

### Authentication

- `POST /auth/signup` - Register a new user
  - Body: `{ "email": "user@example.com", "username": "johndoe", "password": "secret123", "full_name": "John Doe" }`
  
- `POST /auth/login` - Login and get access token
  - Body: `{ "username": "johndoe", "password": "secret123" }`
  
- `GET /auth/me` - Get current user info (requires token)
  - Query param: `token=<your_jwt_token>`

### Health Check

- `GET /` - Welcome message
- `GET /health` - Health check

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── database.py          # MongoDB connection
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py          # User models
│   ├── routers/
│   │   ├── __init__.py
│   │   └── auth.py          # Authentication routes
│   └── utils/
│       ├── __init__.py
│       └── security.py      # Security utilities (JWT, password hashing)
├── .env                      # Environment variables
├── .env.example             # Example environment variables
├── requirements.txt         # Python dependencies
└── README.md
```

## Security Notes

- Change the `SECRET_KEY` in `.env` before deploying to production
- Use strong passwords
- Keep your `.env` file secure and never commit it to version control
- In production, use HTTPS and secure MongoDB connection

## Database Schema

### Users Collection

```json
{
  "_id": "ObjectId",
  "email": "string (unique)",
  "username": "string (unique)",
  "full_name": "string (optional)",
  "hashed_password": "string",
  "is_active": "boolean",
  "is_verified": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## Development

- The API uses async/await with Motor for async MongoDB operations
- JWT tokens expire after 30 minutes (configurable in `.env`)
- Passwords are hashed using bcrypt
- Input validation is handled by Pydantic models
