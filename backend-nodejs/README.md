# ComplaintHub Node.js Backend

A simple, reliable Node.js backend for the ComplaintHub application.

## Features

- ✅ **Simple Setup**: No complex dependencies or virtual environments
- ✅ **Authentication**: JWT-based authentication with bcrypt password hashing
- ✅ **Database**: SQLite database with automatic table creation
- ✅ **CORS**: Configured for frontend communication
- ✅ **Error Handling**: Comprehensive error handling and logging
- ✅ **Windows Compatible**: Works seamlessly on Windows

## Quick Start

### Prerequisites
- Node.js (v14 or higher)
- npm

### Installation

1. **Navigate to the backend directory:**
   ```bash
   cd backend-nodejs
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the server:**
   ```bash
   npm run dev
   ```

   Or use the Windows batch file:
   ```bash
   start_server.bat
   ```

### API Endpoints

The server will be running on `http://localhost:8001`

#### Authentication
- `POST /api/v1/auth/signup` - User registration
- `POST /api/v1/login/access-token` - User login
- `GET /api/v1/users/me` - Get current user (requires auth)

#### Brands
- `POST /api/v1/brands` - Create brand (requires auth)
- `GET /api/v1/brands` - Get user's brands (requires auth)

#### Tickets
- `POST /api/v1/tickets` - Create ticket (requires auth)
- `GET /api/v1/tickets` - Get user's tickets (requires auth)
- `PUT /api/v1/tickets/:id` - Update ticket (requires auth)

#### Admin (Admin role required)
- `GET /api/v1/users` - Get all users
- `GET /api/v1/admin/tickets` - Get all tickets

#### Health Check
- `GET /` - API status
- `GET /health` - Health check

## Database

The backend uses SQLite with automatic table creation:
- `users` - User accounts and authentication
- `brands` - Brand management
- `tickets` - Complaint tickets

## Environment Variables

Create a `.env` file for production:
```
JWT_SECRET=your-super-secret-key-here
PORT=8001
```

## Troubleshooting

### Port Already in Use
If port 8001 is already in use, change the PORT in server.js or set the PORT environment variable.

### Database Issues
The database file (`voicebot.db`) will be created automatically. If you need to reset it, simply delete the file and restart the server.

### CORS Issues
The server is configured to accept requests from:
- `http://localhost:5173`
- `http://127.0.0.1:5173`

If you're using a different frontend URL, update the CORS configuration in server.js.

## Development

The server uses nodemon for automatic reloading during development. Any changes to server.js will automatically restart the server. 