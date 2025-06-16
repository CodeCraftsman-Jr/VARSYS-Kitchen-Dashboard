# 🔐 Secure Credentials Folder

## ⚠️ IMPORTANT: This folder contains your actual Firebase credentials

### 📁 What's in this folder:
- `firebase_credentials.json` - Your actual Firebase configuration
- `jwt_secret.key` - Your JWT secret key (if needed)
- Other sensitive configuration files

### 🔒 Security Notes:
1. **This folder is excluded from Git** (in .gitignore)
2. **Never commit these files** to any repository
3. **Keep backups** in a secure location
4. **Only you should have access** to these files

### 🏗️ How it works for commercial distribution:
1. **You keep your credentials here** (secure, not in Git)
2. **Build script reads from here** and embeds them securely
3. **Customers get executable** with embedded, encrypted credentials
4. **Customers cannot access** your actual Firebase config
5. **You maintain control** of your Firebase project

### 📝 Instructions:
1. **Replace the placeholder values** in `firebase_credentials.json` with your actual Firebase configuration
2. **Run the secure build script** which will embed these credentials
3. **Distribute the executable** to customers
4. **Your credentials remain secure** and under your control

### 🚫 What customers CANNOT do:
- Extract your Firebase credentials
- Access your Firebase project directly
- Modify your Firebase configuration
- Use your Firebase without a valid license

### ✅ What you CAN do:
- Sell the software commercially
- Control access through licensing
- Monitor usage through Firebase
- Update the software with new features
- Maintain your Firebase project security
