# Authentication Setup Guide

## Overview

This server control panel now includes basic authentication to protect access to the system. A single user account is configured via environment variables.

## Features

- **Password Manager Friendly**: Login form uses proper HTML5 semantics with autocomplete attributes
- **Mobile Compatible**: Works seamlessly with password managers on mobile devices
- **Session-Based**: Secure session management with HTTP-only cookies
- **Single User**: Simple preset user configuration (no database required)
- **Secure Password Storage**: Passwords are hashed using Werkzeug's security utilities

## Quick Start

### Default Credentials (Development Only)

```
Username: admin
Password: admin
```

**⚠️ IMPORTANT: Change these credentials in production!**

## Production Setup

### Step 1: Create Environment File

Copy the example environment file:

```bash
cp .env.example .env
```

### Step 2: Generate a Secure Secret Key

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and set it as `SECRET_KEY` in your `.env` file.

### Step 3: Generate a Password Hash

```bash
python3 -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('your_secure_password_here'))"
```

Replace `your_secure_password_here` with your desired password, then copy the hash output.

### Step 4: Configure Your .env File

Edit your `.env` file:

```bash
# Your chosen username
AUTH_USERNAME=your_username

# The password hash you generated
AUTH_PASSWORD_HASH=scrypt:32768:8:1$...your_hash_here...

# The secret key you generated
SECRET_KEY=your_secret_key_here
```

### Step 5: Load Environment Variables

The application will automatically load environment variables. Make sure to:

1. Keep your `.env` file secure and never commit it to version control
2. Set appropriate file permissions: `chmod 600 .env`

## Using with Password Managers

### Desktop

Password managers like 1Password, Bitwarden, LastPass, etc. will automatically detect the login form and offer to save/autofill credentials.

### Mobile

The login form uses proper HTML5 attributes:
- `autocomplete="username"` for the username field
- `autocomplete="current-password"` for the password field

This ensures compatibility with iOS Keychain, Google Smart Lock, and other mobile password managers.

## Security Best Practices

1. **Use Strong Passwords**: Use a password manager to generate strong, unique passwords
2. **Secure the Secret Key**: Keep your SECRET_KEY secure and unique per deployment
3. **Use HTTPS**: In production, always use HTTPS to protect credentials in transit
4. **Regular Updates**: Periodically rotate your password and secret key
5. **File Permissions**: Ensure `.env` is not world-readable: `chmod 600 .env`
6. **Firewall**: Configure firewall rules to limit who can access the control panel

## Changing Your Password

1. Generate a new password hash:
   ```bash
   python3 -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('new_password'))"
   ```

2. Update `AUTH_PASSWORD_HASH` in your `.env` file

3. Restart the application

## Logout

Click the "Logout" button in the top-right corner of the control panel to end your session.

## Troubleshooting

### Can't Login

- Verify your username and password are correct
- Check that environment variables are loaded correctly
- Ensure the password hash was generated properly
- Check application logs for errors

### Password Manager Not Working

- Ensure you're using the latest browser version
- Try manually triggering the password manager
- Check that the login form is not inside an iframe
- Verify browser password manager is enabled

### Session Expired

Sessions expire when:
- You explicitly logout
- Browser is closed (session cookies)
- Server is restarted

Simply log in again to create a new session.

## Technical Details

- **Session Management**: Flask sessions with HTTP-only cookies
- **Password Hashing**: Werkzeug's `generate_password_hash()` using scrypt
- **CSRF Protection**: Form-based authentication (not API-based for initial login)
- **Cookie Security**: SameSite=Lax policy

## Support

For issues or questions, please refer to the main project documentation or create an issue in the repository.
