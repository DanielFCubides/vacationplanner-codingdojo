# Vacation Planner UI - Keycloak Authentication

A React application for vacation planning with dual authentication flows integrated with Keycloak for secure user authentication.

## 🔐 Authentication Flows

This vacation planning application supports two different OAuth 2.0 authentication flows with Keycloak:

### 1. **Direct Flow (Resource Owner Password Credentials)**
- Users enter username and password directly in the application
- Credentials are sent to Keycloak for validation
- Best for trusted first-party applications
- No redirects needed

### 2. **Standard Flow (Authorization Code Grant)**
- Users are redirected to Keycloak's login page
- Authentication happens on Keycloak's secure domain
- After login, users are redirected back with an authorization code
- Most secure option, recommended for production

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ and npm
- Access to a Keycloak instance
- Keycloak realm and client configured

### Installation
```bash
npm install
```

### Environment Configuration
Create a `.env.development` file:
```env
VITE_KEYCLOAK_URL=https://your-keycloak-domain.com
VITE_KEYCLOAK_REALM=your-realm
VITE_KEYCLOAK_CLIENT_ID=your-client-id
VITE_KEYCLOAK_REDIRECT_URI=http://localhost:3001/auth/callback
```

### Running the Application
```bash
npm run dev
```
Application will be available at `http://localhost:3001`

## 🧪 Testing Authentication Flows

### Testing Direct Flow (Username/Password)

1. **Enable Direct Flow** in `featureFlags.js`:
```javascript
export const FEATURE_FLAGS = {
  AUTH_FLOW: 'direct', // or 'both' to show both options
  // ... other flags
};
```

2. **Navigate to Login** (`/login`)
3. **Enter credentials** directly in the form
4. **Click "Continue"**
5. **Success**: You'll be redirected to `/dashboard`

**Flow sequence:**
```
Login Form → Send credentials to Keycloak → Receive tokens → Dashboard
```

### Testing Standard Flow (OAuth Redirect)

1. **Enable Standard Flow** in `featureFlags.js`:
```javascript
export const FEATURE_FLAGS = {
  AUTH_FLOW: 'standard', // or 'both' to show both options
  // ... other flags
};
```

2. **Navigate to Login** (`/login`)
3. **Click "Take me to Keycloak"**
4. **Login on Keycloak's page**
5. **Automatic redirect** back to your app
6. **Success**: You'll land on `/dashboard`

**Flow sequence:**
```
Login Page → Redirect to Keycloak → User logs in → 
Redirect to /auth/callback → Exchange code for tokens → Dashboard
```

### Testing Both Flows

Set `AUTH_FLOW: 'both'` to display both options on the login page.

## 🔧 Keycloak Configuration

### Required Keycloak Settings

1. **Client Configuration**:
   - Client ID: `your-client-id`
   - Client Protocol: `openid-connect`
   - Access Type: `public`

2. **For Direct Flow**:
   - Enable "Direct Access Grants"

3. **For Standard Flow**:
   - Valid Redirect URIs: `http://localhost:3001/auth/callback`
   - Web Origins: `http://localhost:3001`

## 🏗️ Project Structure

```
src/
├── services/
│   ├── authService.js           # Main authentication service
│   └── keycloakFlows/
│       ├── directFlow.js        # Username/password flow
│       └── standardFlow.js      # OAuth redirect flow
├── App.jsx                      # Main app with routing
├── LoginPage.jsx                # Login UI with both flow options
├── Dashboard.jsx                # Protected vacation planning dashboard
└── authContext.jsx              # React context for auth state
```

## 🔍 How It Works

### Direct Flow Details
1. User enters credentials in the React app
2. App sends POST request to Keycloak's token endpoint
3. Keycloak validates and returns tokens
4. App stores tokens and updates auth state
5. User can access protected routes

### Standard Flow Details
1. User clicks "Login with Keycloak"
2. App generates state parameter for CSRF protection
3. Browser redirects to Keycloak login page
4. User authenticates on Keycloak
5. Keycloak redirects back to `/auth/callback` with authorization code
6. App exchanges code for tokens via backend call
7. Tokens stored, user authenticated

## 🛡️ Security Features

- **CSRF Protection**: State parameter validation in OAuth flow
- **Secure Token Storage**: Tokens stored in localStorage with expiry checks
- **Protected Routes**: Automatic redirect to login for unauthenticated users
- **Token Refresh**: Automatic token refresh before expiry (if refresh token available)

## 📝 Common Issues & Solutions

### Issue: "Invalid state parameter"
**Solution**: Clear browser storage and try again. Ensure Keycloak preserves state parameter.

### Issue: Redirect loop
**Solution**: Check Valid Redirect URIs in Keycloak matches your app's callback URL exactly.

### Issue: CORS errors
**Solution**: Add your app's origin to Web Origins in Keycloak client settings.

### Issue: "Failed to fetch" on Direct Flow
**Solution**: Ensure "Direct Access Grants" is enabled in Keycloak client settings.

## 🧹 Development Commands

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint
```

## 📚 Resources

- [Keycloak Documentation](https://www.keycloak.org/documentation)
- [OAuth 2.0 Specification](https://oauth.net/2/)
- [React Router Documentation](https://reactrouter.com/)

## 📄 License

This project is licensed under the MIT License.