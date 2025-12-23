# 🔐 API Authentication Guide

## Overview
The API is now secured with token-based authentication. All endpoints except `/api/v1/auth/login/` require a valid authentication token.

## Authentication Endpoints

### 1. **Login** (Get Token)

**Endpoint:** `POST /api/v1/auth/login/`  
**Authorization:** None required  

**Request:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user_id": 1,
  "username": "admin",
  "email": "admin@atw.com",
  "role": "Admin"
}
```

### 2. **Logout** (Delete Token)

**Endpoint:** `POST /api/v1/auth/logout/`  
**Authorization:** Required  
**Headers:** `Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b`

**Response:**
```json
{
  "message": "Successfully logged out"
}
```

### 3. **Get Profile**

**Endpoint:** `GET /api/v1/auth/profile/`  
**Authorization:** Required  
**Headers:** `Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b`

**Response:**
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@atw.com",
  "first_name": "System",
  "last_name": "Administrator",
  "role": "Admin",
  "status": "active"
}
```

## Using Authenticated Endpoints

All other endpoints now require the token in the Authorization header:

**Example:**
```bash
curl -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" \
     http://localhost:8000/api/v1/trips/
```

## Flutter Integration

### Setup API Service

```dart
// lib/services/api_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  static const String baseUrl = 'http://10.0.2.2:8000/api/v1';
  String? _token;
  
  // Login and save token
  Future<Map<String, dynamic>> login(String username, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login/'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'username': username,
        'password': password,
      }),
    );
    
    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      _token = data['token'];
      
      // Save token to persistent storage
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('auth_token', _token!);
      
      return data;
    } else {
      throw Exception('Login failed');
    }
  }
  
  // Get headers with token
  Map<String, String> _getHeaders() {
    return {
      'Content-Type': 'application/json',
      if (_token != null) 'Authorization': 'Token $_token',
    };
  }
  
  // Load token from storage
  Future<void> loadToken() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString('auth_token');
  }
  
  // Get all trips (authenticated)
  Future<List<dynamic>> getTrips() async {
    await loadToken();
    
    final response = await http.get(
      Uri.parse('$baseUrl/trips/'),
      headers: _getHeaders(),
    );
    
    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else if (response.statusCode == 401) {
      throw Exception('Unauthorized - Please login again');
    } else {
      throw Exception('Failed to load trips');
    }
  }
  
  // Logout
  Future<void> logout() async {
    if (_token != null) {
      await http.post(
        Uri.parse('$baseUrl/auth/logout/'),
        headers: _getHeaders(),
      );
      
      _token = null;
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove('auth_token');
    }
  }
}
```

### Add Dependency

Add to `pubspec.yaml`:
```yaml
dependencies:
  shared_preferences: ^2.2.2  # For storing token
```

### Usage Example

```dart
// Login screen
final apiService = ApiService();

try {
  final userData = await apiService.login('admin', 'admin123');
  print('Logged in: ${userData['username']}');
  
  // Now you can call authenticated endpoints
  final trips = await apiService.getTrips();
  print('Trips: $trips');
} catch (e) {
  print('Error: $e');
}
```

## Test Users

After populating sample data:
- Username: `admin`, Password: `admin123`
- Username: `driver1`, Password: `driver123`
- Username: `paramedic1`, Password: `paramedic123`

## Setup Steps

1. **Run migrations** (create authtoken table):
   ```bash
   sudo docker-compose exec web python manage.py migrate
   ```

2. **Restart server**:
   ```bash
   sudo docker-compose restart web
   ```

3. **Test login**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/login/ \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "admin123"}'
   ```

## Security Notes

✅ **Enabled:**
- Token-based authentication
- CORS configured
- HTTPS redirect (in production)
- Secure cookies (in production)

⚠️ **Remember:**
- Change default passwords before production
- Use HTTPS in production
- Rotate tokens periodically
- Implement token expiration for enhanced security
