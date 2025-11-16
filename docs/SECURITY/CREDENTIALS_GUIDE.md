# 🔐 TwisterLab Credentials Management Guide

**Last Updated**: 2025-11-02  
**Status**: ACTIVE  
**Classification**: SECURITY CRITICAL

---

## 📋 Overview

This guide explains how to securely manage credentials for TwisterLab infrastructure using AES-256 encryption.

---

## 🎯 Quick Start

### Option 1: GPG Encryption (Recommended)

```powershell
# 1. Install GPG4Win (if not installed)
# Download: https://gpg4win.org/download.html

# 2. Fill in credentials template
# Edit: credentials\CREDENTIALS.md

# 3. Encrypt all credentials
cd C:\TwisterLab
.\credentials\encrypt_credentials.ps1

# 4. Delete unencrypted files (prompted by script)
```

### Option 2: 7-Zip Encryption (Alternative)

```powershell
# 1. Install 7-Zip (if not installed)
# Download: https://www.7-zip.org/download.html

# 2. Fill in credentials template
# Edit: credentials\CREDENTIALS.md

# 3. Encrypt all credentials
cd C:\TwisterLab
.\credentials\encrypt_credentials_7zip.ps1

# 4. Delete unencrypted files (prompted by script)
```

---

## 📂 File Structure

```
C:\TwisterLab\
├── credentials/                      # Git-ignored directory
│   ├── README.md                     # Security guidelines
│   ├── CREDENTIALS.md                # Template (fill this in)
│   ├── CREDENTIALS.encrypted.gpg     # Encrypted credentials (GPG)
│   ├── CREDENTIALS.encrypted.7z      # Encrypted credentials (7-Zip)
│   ├── edge-passwords.encrypted.gpg  # Browser passwords (GPG)
│   ├── edge-passwords.encrypted.7z   # Browser passwords (7-Zip)
│   ├── encrypt_credentials.ps1       # GPG encryption script
│   └── encrypt_credentials_7zip.ps1  # 7-Zip encryption script
└── .gitignore                        # Excludes credentials/ folder
```

**⚠️ CRITICAL**: The `credentials/` folder is **Git-ignored** to prevent accidental commits.

---

## 🔒 Encryption Process

### Step 1: Fill Credentials Template

1. Open `credentials\CREDENTIALS.md` in VS Code
2. Fill in all passwords, API keys, and secrets
3. Use strong passwords (20+ characters, mix of types)
4. Generate passwords: https://bitwarden.com/password-generator/

### Step 2: Encrypt Files

**Using GPG** (recommended for cross-platform):
```powershell
cd C:\TwisterLab
.\credentials\encrypt_credentials.ps1
```

**Using 7-Zip** (Windows-friendly):
```powershell
cd C:\TwisterLab
.\credentials\encrypt_credentials_7zip.ps1
```

**What happens:**
- You'll be prompted for a **master password** (choose strong!)
- Scripts encrypt:
  - `CREDENTIALS.md` → `CREDENTIALS.encrypted.gpg` (or `.7z`)
  - `Microsoft Edge Passwords.csv` → `edge-passwords.encrypted.gpg` (or `.7z`)
- You'll be asked to delete unencrypted originals (DO IT!)

### Step 3: Backup Encrypted Files

**Backup locations** (choose at least 2):
1. **External USB drive** (encrypted partition recommended)
2. **Cloud storage** with additional encryption:
   - OneDrive + Cryptomator
   - Dropbox + Veracrypt
   - Google Drive + Cryptomator
3. **Password manager** (1Password, Bitwarden) - Store as secure note
4. **Separate machine** (via secure copy, not email!)

**⚠️ NEVER**:
- Email encrypted files (even encrypted, avoid it)
- Store master password in same location as encrypted files
- Share master password via chat/email

---

## 🔓 Decryption Process

### Using GPG

```powershell
# Decrypt credentials
gpg --decrypt credentials\CREDENTIALS.encrypted.gpg > TEMP-CREDENTIALS.md

# View the file (then delete immediately!)
notepad TEMP-CREDENTIALS.md

# Delete after use
Remove-Item TEMP-CREDENTIALS.md -Force
```

### Using 7-Zip

```powershell
# Method 1: Right-click → 7-Zip → Extract
Right-click on .7z file → 7-Zip → Extract files → Enter password

# Method 2: Command line
& "C:\Program Files\7-Zip\7z.exe" x credentials\CREDENTIALS.encrypted.7z -o.
# Enter password when prompted

# Delete decrypted file after use!
Remove-Item CREDENTIALS.md -Force
```

---

## 🛡️ Security Best Practices

### Password Requirements

| Type | Minimum Length | Requirements |
|------|----------------|--------------|
| **Master Password** | 20 characters | Upper, lower, numbers, symbols |
| **Production DB** | 32 characters | Random generated |
| **API Keys** | 64 characters | Random generated |
| **Session Secrets** | 64 characters | Random generated |

### Password Generation

```powershell
# Generate strong password (32 characters)
-join ((48..57) + (65..90) + (97..122) + 33,35,36,37,38,42,43,45,61 | Get-Random -Count 32 | % {[char]$_})

# Generate API key (64 characters, base64)
[Convert]::ToBase64String([System.Security.Cryptography.RNGCryptoServiceProvider]::Create().GetBytes(48))

# Using OpenSSL (if installed)
openssl rand -base64 32
```

### Access Control

- ✅ **Staging**: Simple passwords OK (local dev only)
- ⚠️ **Production**: Strong passwords + MFA required
- ✅ **API Keys**: Rotate every 90 days
- ✅ **SSH Keys**: Use key-based auth, no passwords
- ✅ **Database**: Use connection pooling with encrypted connections

### Git Protection

The following patterns are **automatically ignored** by Git:

```gitignore
# Credentials
CREDENTIALS.md
CREDENTIALS.encrypted
CREDENTIALS.pdf
credentials/
secrets/

# CSV exports
*.csv
*passwords*.csv
*Passwords*.csv
Microsoft*Passwords*.csv

# Keys
*.key
*.pem
*.p12
*.pfx
*.gpg

# Environment
.env.production
```

**Verify protection**:
```powershell
# Check what's ignored
git status --ignored | Select-String "credentials"

# Check what's tracked
git ls-files | Select-String "credentials"
# Should return NOTHING related to credentials/
```

---

## 🚨 Incident Response

### If Credentials Are Compromised

**Immediate Actions** (within 5 minutes):
1. Rotate ALL compromised passwords
2. Revoke ALL API tokens
3. Change database connection strings
4. Enable additional MFA everywhere
5. Check access logs for unauthorized access
6. Notify security team

**Containment** (within 1 hour):
1. Isolate compromised systems
2. Check for data exfiltration
3. Regenerate encryption keys
4. Deploy new secrets to production
5. Block suspicious IP addresses

**Recovery** (within 24 hours):
1. Full security audit
2. Update all documentation
3. Test all services with new credentials
4. Post-mortem analysis
5. Update security procedures

### Emergency Contacts

| Role | Contact |
|------|---------|
| **Admin** | youneselfakir0@gmail.com |
| **Security Lead** | (To be assigned) |
| **On-Call** | (To be assigned) |

---

## 📚 Additional Resources

- **GPG4Win**: https://gpg4win.org/
- **7-Zip**: https://www.7-zip.org/
- **Bitwarden** (Password Manager): https://bitwarden.com/
- **1Password** (Password Manager): https://1password.com/
- **Cryptomator** (Cloud Encryption): https://cryptomator.org/
- **Password Strength Checker**: https://bitwarden.com/password-strength/

---

## 🔍 Verification Checklist

Before considering credentials secure:

- [ ] All sensitive files are encrypted (GPG or 7-Zip)
- [ ] Unencrypted originals are deleted
- [ ] Encrypted files are backed up to 2+ locations
- [ ] Master password is stored in password manager
- [ ] `.gitignore` excludes credentials/ folder
- [ ] `git status` shows no tracked credential files
- [ ] Decryption tested and working
- [ ] Team members have access to encrypted files (if needed)
- [ ] Production passwords are 32+ characters
- [ ] MFA enabled on all critical services

---

## 📞 Support

For questions about credential management:

1. Read this guide first
2. Check `credentials/README.md` for additional info
3. Contact: youneselfakir0@gmail.com
4. Emergency: (To be assigned)

---

**⚠️ REMINDER**: Never commit unencrypted credentials to Git!  
**🔒 CRITICAL**: Always encrypt before storage!  
**💾 BACKUP**: Keep encrypted backups in multiple locations!

---

**Last Updated**: 2025-11-02  
**Version**: 1.0.0  
**Status**: ACTIVE
