---
title: Platform Security - Complete Reference
description: Comprehensive guide to Ignition 8.3 authentication, authorization, permissions, user management, SSL/TLS, API security, and security best practices
---

> **Skill level:** 300 · **Read first:** [50-SECURITY-MODEL](50-SECURITY-MODEL.md)
> **You are here:** [00-INDEX](00-INDEX.md) › 51-PLATFORM-SECURITY-COMPLETE

# Platform Security - Complete Reference

Ignition provides comprehensive security mechanisms to safeguard data and applications. Control **who** accesses systems, **when** they can access them, and **where** they can access them.

---

## 1. AUTHENTICATION METHODS

Authentication verifies user identity before granting access.

### 1.1 Classic Authentication Strategy

**Overview:**
- Users stored in "User Sources" (configurations containing roles and users)
- Internal or external storage
- Active Directory/LDAP support
- Recommended for traditional IT environments

**Internal User Source (Gateway Storage):**
```
Gateway > Configure > Security > User Sources > [Create]
Storage: Internal (Ignition Gateway Database)
Users: Managed through Admin Console
Passwords: Salted, hashed storage
Default Credentials: admin / password (CHANGE THIS)
```

**Configuration Steps:**
1. Gateway > Security > User Sources
2. Click "Create new User Source"
3. Select Type: "Internal"
4. Configure password policy
5. Add users and assign roles

**SQL Database User Source:**
```
Type: Database
Connection: SQL Database
Tables: User table with password hash, role mappings
External AD/LDAP sync capability
Recommended for enterprise deployments
```

### 1.2 Identity Provider Authentication Strategy (Modern)

**Overview:**
- Federated identity management
- No user credentials stored in Ignition
- Uses Security Levels for authorization
- User Attribute Mapping from IdP claims

**Supported Providers:**
- **OpenID Connect (OIDC)** - Google, Okta, Auth0, Keycloak
- **SAML 2.0** - Enterprise SSO (Okta, Azure AD, Ping)
- **Ignition as IdP** - Isolated system federation

**Configuration Pattern:**
```
Gateway > Configure > Security > Identity Providers
Provider Type: OpenID Connect or SAML
Client ID / Client Secret: Obtained from IdP
Redirect URI: https://ignition-gateway/auth/oidc/callback
Scopes: profile, email, roles (provider-dependent)
User Attribute Mapping: Map IdP claims to Ignition attributes
  - Sub (subject) → Username
  - Email → Email
  - Groups → Roles (via Security Level Rules)
```

### 1.3 LDAP / Active Directory

**Overview:**
- Centralized authentication via corporate directory
- Single Sign-On (SSO) capability
- Password managed by IT department
- Real-time group membership sync

**Configuration:**
```
Gateway > Security > User Sources > Type: LDAP/Active Directory
LDAP Server: ldap://ad-server.company.com:389 (or ldaps://...389)
Bind User: service_account@company.com
Bind Password: Service account password
Base DN: dc=company,dc=com
User Filter: (uid=%s) or (sAMAccountName=%s)
Group Filter: (memberUid=%s) or (member=%s)
Role Mapping: LDAP groups → Ignition roles
```

**Active Directory Sync:**
- Automatic group → role mapping
- Real-time changes reflected
- Nested group support
- Security group synchronization

### 1.4 OAuth 2.0 Integration

**Overview:**
- Third-party authentication providers
- No password storage in Ignition
- Delegated authorization
- Social/corporate OAuth providers

**Supported Flows:**
- Authorization Code (recommended, web apps)
- Client Credentials (service-to-service)
- Refresh Token grants

**Configuration:**
```
Gateway > Security > OAuth 2.0 Clients
Client ID: Provided by OAuth provider
Client Secret: Sensitive - stored encrypted
Authorization URL: Provider endpoint
Token URL: Token exchange endpoint
User Info URL: User claims endpoint (if OIDC)
Scopes: openid profile email
Redirect URIs: Must match provider configuration
  - https://ignition-gateway:8088/auth/oauth/callback
```

**Common Providers:**
- Google OAuth
- GitHub
- Microsoft Azure AD
- Okta
- Custom OAuth 2.0 servers

---

## 2. AUTHORIZATION & ROLES SYSTEM

Authorization determines what authenticated users can do.

### 2.1 Role-Based Access Control (RBAC)

**Core Concepts:**
```
User → Role(s) → Permissions
One user can have multiple roles
Roles group related permissions
Permissions define allowed actions
```

**Role Definition:**
```
Gateway > Security > User Sources > [Source] > Roles > [Create]
Role Name: e.g., "ProductionOperator", "MaintenanceTech", "Analyst"
Description: Purpose and responsibilities
Permissions: Read/Write/Execute on specific resources
Inherits From: Optional parent role inheritance
```

### 2.2 Built-in Roles

**Administrator:**
- Full system access
- All Gateway configuration rights
- All project permissions
- All tag read/write
- Cannot be restricted

**User (Custom):**
- Limited access, fully configurable
- Specific tag permissions
- Specific view access
- Restricted actions/scripts

### 2.3 Custom Role Examples

**Example 1: Production Operator**
```
Permissions:
  - Read: All Production tags
  - Write: Setpoint tags (limited set)
  - Read: Production dashboard views
  - Execute: Start/Stop sequences (via buttons)
  - Cannot: Modify tag definitions, designer access
```

**Example 2: Maintenance Technician**
```
Permissions:
  - Read: All Production + Maintenance tags
  - Write: Maintenance tags, calibration values
  - Write: Diagnostic tags
  - Execute: Maintenance scripts
  - Read: Maintenance views + dashboards
  - Cannot: Production setpoint changes, gateway config
```

**Example 3: Data Analyst**
```
Permissions:
  - Read: Historical data, database access
  - Read: All tags (no write)
  - Execute: Report generation
  - Access: Analytics views
  - Cannot: Modify tag values, system configuration
```

### 2.4 Security Levels (Advanced Authorization)

**Overview:**
- Hierarchical security model
- Assign levels to designer, gateway areas, projects
- Users must have minimum level to access
- Especially important with Identity Provider strategy

**Security Level Hierarchy (0-9):**
```
Level 0: No restriction (public)
Level 1: Basic user access
Level 2: Power user access
Level 3: Technician access
Level 4: Administrator access
Level 5-9: Super-admin, system-level access
```

**Assignment:**
```
Designer Access: Require Level 4+ (admin)
Gateway Security Config: Require Level 5 (super-admin)
Project Areas: Assign Level 1-3 (department-specific)
View Access: Assign Level 1+ (all authenticated)
```

**Security Level Rules (IdP):**
```
If User has "admin" group in IdP
  → Assign Security Level 5
Else if User has "operator" group
  → Assign Security Level 2
Else
  → Assign Security Level 1
```

---

## 3. PERMISSION MODEL (Read, Write, Execute)

Granular permission control at multiple scopes.

### 3.1 Tag Permissions

**Permission Types:**
- **Read**: Query/subscribe to tag values
- **Write**: Modify tag values
- **Execute**: Run tag scripts/actions (if tag contains code)

**Tag Permission Configuration:**
```
Designer > Tags > [Tag] > Permissions
Read: Roles that can read this tag
Write: Roles that can write this tag
Execute: Roles that can execute tag scripts
```

**Example:**
```
Tag: /production/reactor_temp
- Administrators: Read + Write + Execute
- ProductionOperator: Read + Write
- DataAnalyst: Read only
- Maintenance: No access (fully restricted)

Tag: /system/emergency_stop
- Administrators: Read + Write + Execute
- ProductionOperator: Execute only (can trigger)
- Others: No access
```

**Wildcard Permissions:**
```
Path: /production/*
  - All tags under /production path
  - Applies permission to matching tags
  - Useful for department/area-based access

Path: /*/temperature
  - All tags ending with /temperature
  - Permission applied across hierarchy
```

### 3.2 View/Component Permissions

**View-Level Security:**
```
Designer > View > Properties > Permissions
Visible To: [List of roles]
Edit Mode: [List of roles]
Users without permission see "Access Denied"
View hidden from sidebar/menu for non-authorized users
```

**Component-Level Binding:**
```javascript
// Show component only to admins:
{expr: "if('admin' in {user.roles}, true, false)"}

// Show component to multiple roles:
{expr: "if(any({user.roles} == ['operator','supervisor','admin']), true, false)"}

// Disable input based on role:
{expr: "if('readonly' in {user.roles}, true, false)"}
```

**Python Script:**
```python
def onComponentOpen(self, event=None):
    user = system.user.getUser()
    roles = user.roles
    
    if "admin" in roles:
        self.props.visible = True
    elif "operator" in roles:
        self.props.components.button_write.visible = False
    else:
        self.props.visible = False
```

### 3.3 Designer Access Control

**Designer-Level Permissions:**
```
Gateway > Security > User Sources > [Source] > User [Edit]
Designer Access: Enabled/Disabled
If Enabled:
  - Can edit projects
  - Can modify tag definitions
  - Can change configurations (if role permits)
```

**Project-Level Security:**
```
Designer > Project > Properties > Security
Restrict Project: Yes/No
If Restricted:
  - Only specific users can edit
  - Password-protected access
  - Separate read-only mode available
```

### 3.4 Gateway Configuration Permissions

**Sensitive Areas Requiring Restrictions:**
- User/Role management
- Database connections
- Tag provider configuration
- OPC-UA settings
- Security certificates
- API key management
- Backup/restore operations

**Configuration:**
```
Each area can require Security Level 4+ (admin)
Controlled via:
  - View Restrictions in Designer
  - Security Level Rules (if using IdP)
  - Role-based access in Admin Console
```

---

## 4. USER MANAGEMENT

Complete user lifecycle management.

### 4.1 User Creation & Administration

**Creating Users (Internal Source):**
```
Gateway > Security > User Sources > [Internal Source] > Users > [Create]
Username: Unique identifier (lowercase recommended: john.smith)
Full Name: Display name
Email: User email address
Password: Initial password (force change on first login)
Roles: Assign one or more roles
Enabled: Checkbox to activate/deactivate
```

**User Properties:**
```
Username: Login identifier
Full Name: Display name (used in audit logs)
Email: Contact information, password reset notifications
Password: Hashed storage, configurable policy
Last Login: Track access activity
Failed Attempts: Locked after N failures (configurable)
```

### 4.2 User Lifecycle

**Creation:**
```
1. Create user account
2. Assign initial password
3. Set temporary password flag (force change)
4. Assign roles
5. Enable account
```

**Activation:**
```
User logs in
Prompted to change temporary password (if set)
Session created with assigned roles
Audit log entry created
```

**Modification:**
```
Update Full Name: Admin console
Change Email: Admin console or user self-service
Reset Password: Admin-initiated or self-service
Disable Account: Immediate deactivation
Update Roles: Admin-initiated role assignment changes
```

**Deactivation:**
```
Flag account as Disabled
Existing sessions maintained (grace period)
No new logins permitted
Audit trail preserved
Option to retain user history or archive
```

### 4.3 User Self-Service Features

**Password Management:**
```
Self-service password change: User → Profile → Change Password
Self-service password reset: Gateway login → Forgot Password
(Requires email configuration)
```

**Profile Settings:**
```
View/update own full name
View/update email address
View assigned roles (read-only)
View login history (recent sessions)
Manage API keys (if enabled)
```

### 4.4 External User Management (LDAP/OAuth)

**LDAP Synchronization:**
```
Users managed in LDAP/Active Directory
Ignition syncs group membership
On login:
  1. LDAP authenticates credentials
  2. Ignition syncs group membership
  3. Groups mapped to Ignition roles
  4. Session created with mapped roles
```

**OAuth/OIDC Flow:**
```
User clicks "Login with [Provider]"
Redirects to OAuth provider login
Provider authenticates and returns claims (email, groups, etc.)
Ignition creates session based on claims
User Attribute Mapping applies to determine roles
```

### 4.5 Session Management

**Session Lifecycle:**
```
Login:
  - Credentials validated
  - Session token created
  - User roles cached in session
  - Last login timestamp recorded

Active Session:
  - Activity tracked
  - Idle timeout countdown active
  - Token refreshed on activity

Logout:
  - Session destroyed
  - Token invalidated
  - Audit entry logged
  - Redirected to login screen
```

**Session Configuration:**
```
Gateway > Configure > Security > Session Settings
Session Timeout: Idle timeout in minutes (default: 30)
Session Persistence: Remember login (true/false)
Concurrent Sessions: Allow multiple logins per user (default: allowed)
Max Session Duration: Total time before re-authentication required
```

---

## 5. SECURITY BEST PRACTICES

### 5.1 Password Security

**Policy Configuration:**
```
Gateway > Security > User Sources > [Internal] > Password Policy
Minimum Length: 12+ characters (recommended)
Require Uppercase: Yes
Require Numbers: Yes
Require Special Characters: Yes (recommended)
Expiration: 90 days (configurable)
History: Prevent last N passwords (recommended: 5)
```

**Recommendations:**
- ✅ Enforce strong password policy
- ✅ Change default admin password immediately
- ✅ Never share passwords
- ✅ Use password manager for complexity
- ✅ Enable multi-factor authentication (via OAuth/OIDC)
- ❌ Don't store passwords in scripts/bindings
- ❌ Don't use same password across systems

### 5.2 Access Control Best Practices

**Principle of Least Privilege:**
```
Grant minimum permissions required
Review permissions regularly
Remove unnecessary role assignments
Audit role usage quarterly
```

**Role Design:**
- Create granular, function-specific roles
- Avoid "super-user" role outside admin
- Separate read-only and write roles
- Group related permissions logically

**Example Structure:**
```
✅ Good:
  - ProductionOperator (specific to production)
  - MaintenanceTech (maintenance-specific)
  - ReportViewer (read-only analytics)

❌ Bad:
  - PowerUser (too broad, unclear scope)
  - Everyone (no access control)
```

### 5.3 Audit & Monitoring

**Audit Logging:**
```
Gateway > Configure > System > Audit Log
Tracks:
  - User logins/logouts
  - Tag writes
  - Configuration changes
  - Designer project edits
  - Failed authentication attempts
  - Gateway restarts
  - Script execution
```

**Regular Reviews:**
```
Weekly: Check failed login attempts
Monthly: Review user access changes
Quarterly: Full role/permission audit
Annually: Security training for all admins
```

**Monitoring:**
```
Alert on:
  - Failed login attempts (3+ in 5 min)
  - Administrative actions outside business hours
  - Mass tag writes/modifications
  - Gateway configuration changes
  - Concurrent logins per user
```

### 5.4 Application Security

**Designer & Project Access:**
- Restrict designer access to admin/development team only
- Version control projects externally (Git)
- Code review for script changes
- No hardcoded credentials in scripts

**View/Component Security:**
```
✅ Good:
  // Check user role in view script:
  user = system.user.getUser()
  if "admin" in user.roles:
      showAdminPanel()
  
❌ Bad:
  // Hardcoded admin check by username:
  if system.user.getUser().name == "admin":
      showAdminPanel()
```

**Tag Binding Security:**
```
✅ Use permission expressions:
  {expr: "'admin' in {user.roles}"}

❌ Don't hide by CSS only:
  visibility: {expr: "'admin' in {user.roles}"}  
  → Still sends data to client
```

### 5.5 Network Security

**HTTPS/SSL:**
- ✅ Required for production deployments
- ✅ Use valid, signed certificates
- ✅ Enforce HTTPS redirect
- ✅ Set HSTS headers
- ✅ Strong TLS version (1.2+)

**Firewall Rules:**
```
Production Environment:
  - Gateway port (8088): Internal network only
  - Designer port (8000): VPN/admin network only
  - Database ports: Internal only
  - OPC-UA: Specific subnet access
```

**Network Isolation:**
```
SCADA Network:
  - Isolated from corporate network
  - Restricted internet access
  - Air-gapped if critical
  - Minimal outbound connectivity
```

### 5.6 Secrets Management

**Storing Credentials:**
```
✅ Recommended:
  - Gateway Secrets Manager (encrypted storage)
  - Password manager with Ignition integration
  - Environment variables (encrypted in transit)
  - Database credentials in gateway config

❌ Never:
  - Hardcoded in scripts
  - In project bindings
  - In comments
  - In version control
  - Plain text files
```

**Database Credentials:**
```
Gateway > Configure > Databases > [Connection]
User: Service account (not DBA account)
Password: Strong, stored encrypted in gateway
Connection pooling: Enable for efficiency
SSL to database: Enable in production
```

### 5.7 Data Protection

**Encryption in Transit:**
- All web traffic: HTTPS/SSL (TLS 1.2+)
- Database connections: SSL where supported
- OPC-UA: Sign & encrypt credentials
- API calls: HTTPS only

**Encryption at Rest:**
- Gateway secrets: Encrypted storage
- Database: Encrypted columns for sensitive data
- Backups: Encrypted files
- Logs: Redact sensitive information

### 5.8 Patch Management

**Ignition Updates:**
- Monitor security advisories monthly
- Test patches in dev environment first
- Apply patches within 30 days of release
- Critical vulnerabilities: 7 days
- Maintain upgrade documentation

**Operating System:**
- Keep OS patched and current
- Manage Java versions (Ignition requirement)
- Disable unused services
- Regular security scans

---

## 6. SSL/TLS CONFIGURATION

Secure communication between clients and gateway.

### 6.1 Certificate Management

**Certificate Types:**
```
Self-Signed: Development/testing only
  - Generated automatically on first run
  - Triggers browser warnings
  - Not trusted by clients

Signed Certificates (Production):
  - Issued by Certificate Authority (CA)
  - Recognized by browsers/systems
  - Valid domain name required
  - Automatic renewal possible
```

**Obtaining Certificate:**
```
Method 1: Certificate Authority (Recommended)
  1. Purchase from trusted CA (DigiCert, Comodo, etc.)
  2. Generate Certificate Signing Request (CSR)
  3. Submit to CA for signing
  4. Receive signed certificate
  5. Import into Ignition gateway

Method 2: Let's Encrypt (Free, automated)
  1. Use ACME client (Certbot, etc.)
  2. Prove domain ownership
  3. Automatic certificate generation
  4. Auto-renewal every 90 days
  5. Import to Ignition
```

### 6.2 Gateway Certificate Configuration

**Accessing Certificate Settings:**
```
Gateway > Configure > Security > SSL / TLS
Current Certificate: View details
Import Certificate: Replace with new certificate
Export Certificate: Backup current certificate
Renew Certificate: Generate new self-signed
Reset Certificate: Restore to auto-generated
```

**Certificate Details:**
```
Issuer: Certificate authority name
Subject: Common Name (domain), Organization
Valid From / Valid To: Expiration dates
Fingerprint: SHA1/SHA256 hash
Key Size: RSA 2048 minimum (4096 recommended)
```

### 6.3 Certificate Import Process

**Prerequisites:**
```
1. Private key (*.pem or *.key file)
2. Certificate file (*.crt or *.cer file)
3. CA bundle (intermediate certificates if needed)
4. Gateway access with admin rights
```

**Import Steps:**
```
Gateway > Configure > Security > SSL/TLS > Import Certificate
File Selection:
  - Private Key: [Upload .pem/.key file]
  - Certificate: [Upload .crt/.cer file]
  - CA Chain: [Upload intermediate certs if applicable]
Verify: Review certificate details
Import: Save to gateway
Restart: Gateway restart may be required
```

**Verification:**
```
After import:
1. Navigate to https://gateway-hostname:8088/
2. Check certificate is valid (browser lock icon)
3. No warning messages
4. Certificate details match
5. Valid until date is in future
```

### 6.4 SSL/TLS Configuration

**Protocol Settings:**
```
Gateway > Configure > System > SSL/TLS Settings
TLS Version: Minimum TLS 1.2 (1.3 if available)
Cipher Suites: Use strong ciphers only
  ✅ TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
  ✅ TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
  ❌ TLS 1.0, 1.1 (deprecated)
  ❌ NULL, EXPORT, DES ciphers
```

**Security Headers:**
```
HSTS (HTTP Strict Transport Security):
  - Forces HTTPS only
  - Prevents protocol downgrade
  - max-age: 31536000 (1 year)
  
HTTPS Redirect:
  - Automatic http → https redirect
  - Port 80 → Port 8088
```

### 6.5 Client Certificate Authentication

**Mutual TLS (mTLS):**
```
Client provides certificate to authenticate
Server verifies client certificate
Enhanced security for service-to-service communication
```

**Configuration:**
```
Gateway > Configure > System > SSL/TLS
Client Certificate Required: Yes/No
Trusted Client CA: Import client CA certificates
Client verification: Enabled for specific connections
```

### 6.6 Certificate Renewal & Rotation

**Renewal Process:**
```
Certificate Expiration Warning:
  - Gateway logs warning at 30 days
  - Renew before expiration
  - Test renewed certificate before deadline

Renewal Steps:
  1. Obtain new certificate from CA
  2. Import using SSL/TLS settings
  3. Verify in browser
  4. Update DNS/infrastructure references
  5. Notify users of changes (if applicable)
```

**Automated Renewal (Let's Encrypt):**
```
Certbot automatic renewal:
  - Runs daily via cron
  - Renews 30 days before expiration
  - Exports to gateway import format
  - Restarts gateway automatically
```

---

## 7. API SECURITY

Control programmatic access to Ignition.

### 7.1 API Authentication Methods

**Session Tokens (Cookie-Based):**
```
Standard login authentication
Browser session with cookie
Good for web applications
Automatically maintained by client

Limitations:
  - Requires login first
  - Subject to session timeout
  - CSRF protection needed
  - Not suitable for service accounts
```

**API Keys (Token-Based):**
```
Long-lived authentication token
No password required
Generated per user/service
Can be scoped to specific permissions
```

### 7.2 API Key Management

**Creating API Keys:**
```
Gateway > Security > User Sources > [User] > API Keys > Generate
Key Name: Descriptive name (e.g., "DataLogger Service")
Expires: Optional expiration date
Permissions: Select specific API scopes
Description: Purpose and usage notes
```

**Key Properties:**
```
Token: Long random string (use as bearer token)
Secret: Optional additional secret
Generated: Creation timestamp
Expires: Expiration date (if set)
Last Used: Track actual usage
Status: Active/Revoked/Expired
```

**Using API Keys:**
```
HTTP Request Header:
Authorization: Bearer <api-key-token>

Or Query Parameter:
GET /api/v1/tags?apikey=<token>

Or Basic Auth:
Authorization: Basic base64(username:api-key)
```

### 7.3 REST API Endpoints

**Common Endpoints:**

```
GET  /api/v1/tags
     List all accessible tags with metadata
     
GET  /api/v1/tags/{path}
     Read specific tag value
     
POST /api/v1/tags/{path}
     Write tag value
     Query Parameters: value, quality
     
GET  /api/v1/tags/{path}/history
     Read historical data
     Query Parameters: startTime, endTime, limit
     
GET  /api/v1/status
     Gateway status and health
     
GET  /api/v1/users
     List users (admin only)
     
POST /api/v1/authenticate
     Obtain session token
     Body: username, password (or oauth token)
```

### 7.4 API Authorization

**Role-Based Access:**
```
API calls inherit user role permissions
Tag read/write permissions enforced
View access checked for report endpoints
Designer access restricted via API

Example:
  API User "DataLogger" has role "ReadOnlyAnalyst"
  → Can call GET /api/v1/tags
  → Cannot call POST /api/v1/tags (write)
  → Cannot access admin endpoints
```

**Scope-Based Permissions (Advanced):**
```
API Key "Integration-Service" scopes:
  - tags:read:production/*
  - tags:write:setpoints
  - history:read
  
Cannot:
  - Access tags outside scoped paths
  - Modify user accounts
  - Change gateway configuration
```

### 7.5 API Rate Limiting & Throttling

**Rate Limiting Configuration:**
```
Gateway > Configure > System > API Settings
Enable Rate Limiting: Yes
Requests per minute: 60 (per API key/user)
Burst limit: 120 (short burst allowance)
Timeout: 60 seconds
```

**Handling Rate Limits:**
```
Response Headers:
  X-RateLimit-Limit: 60
  X-RateLimit-Remaining: 45
  X-RateLimit-Reset: 1234567890
  
When limit exceeded:
  HTTP 429 Too Many Requests
  Retry-After: 60 seconds
```

### 7.6 API Security Best Practices

**Key Management:**
```
✅ Generate unique keys per service
✅ Use scoped/limited permissions
✅ Rotate keys regularly (quarterly)
✅ Monitor API key usage
✅ Revoke unused keys
✅ Store keys securely (password manager)

❌ Don't share API keys
❌ Don't commit keys to version control
❌ Don't use same key for multiple services
❌ Don't expose keys in logs/errors
```

**API Usage Patterns:**
```
✅ HTTPS only for API calls
✅ Implement API request signing
✅ Log all API access
✅ Monitor for unusual activity
✅ Set appropriate timeouts
✅ Validate all input parameters

❌ Don't accept unvalidated input
❌ Don't trust client IP address alone
❌ Don't expose detailed error messages
❌ Don't allow unbounded data requests
```

**Request Validation:**
```python
# Python API request with validation:
import requests
from requests.auth import HTTPBearerAuth

headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}

# Validate before sending:
if not tag_path or not tag_path.startswith('/'):
    raise ValueError("Invalid tag path")
    
response = requests.post(
    f'https://gateway.company.com:8088/api/v1/tags/{tag_path}',
    headers=headers,
    json={'value': new_value},
    timeout=30,
    verify=True  # Verify SSL certificate
)

if response.status_code == 429:
    # Handle rate limiting
    retry_after = response.headers.get('Retry-After')
```

### 7.7 CORS (Cross-Origin Resource Sharing)

**CORS Configuration:**
```
Gateway > Configure > Security > CORS Settings
Allow Credentials: Yes/No
Allowed Origins: List specific domains
  - https://dashboard.company.com
  - https://analytics.company.com
  - NOT: * (wildcard not recommended)
  
Allowed Methods: GET, POST, PUT, DELETE
Allowed Headers: Authorization, Content-Type
Max Age: 3600 seconds (cache preflight)
```

**CORS Best Practices:**
```
✅ Specify exact allowed origins
✅ Use HTTPS origins only
✅ Include credentials carefully
✅ Limit methods/headers
✅ Disable in development only

❌ Don't allow wildcard origin (*)
❌ Don't allow http origins
❌ Don't enable unneeded methods
```

---

## 8. SECURITY ZONES (Network-Based Access Control)

Restrict access by network location.

### 8.1 Zone Configuration

**Overview:**
- Define trusted networks/IP ranges
- Restrict designer, gateway admin access by zone
- Geo-fencing capability

**Configuration:**
```
Gateway > Configure > Security > Security Zones
Zone Name: e.g., "OfficeNetwork", "VPN", "ProductionPlant"
IP Range: CIDR notation (192.168.1.0/24)
Allow Designer: Yes/No
Allow Gateway Config: Yes/No
Priority: Zone matching order
```

**Example Setup:**
```
Zone 1: Office Network (192.168.1.0/24)
  - Allow Designer: Yes
  - Allow Gateway Config: Yes
  
Zone 2: Production Plant (10.0.0.0/8)
  - Allow Designer: No
  - Allow Gateway Config: No (view-only)
  
Zone 3: VPN Network (Any)
  - Allow Designer: Yes (with 2FA)
  - Allow Gateway Config: Restricted admin only
  
Default (Everything Else):
  - Allow Designer: No
  - Allow Gateway Config: No
```

---

## 9. SECURITY TROUBLESHOOTING

### 9.1 Common Issues

**"Access Denied" for Valid User:**
```
Troubleshooting:
1. Verify user exists and is enabled
   Gateway > Security > Users > [Check]
2. Confirm user has correct roles assigned
   Gateway > Security > Users > [User] > Roles
3. Verify role has required permissions
   Designer > Tag/View > Permissions
4. Check view/tag permissions configuration
   Is user role listed in permissions?
5. If using IdP, verify attribute mapping
   Security Levels correctly assigned?
6. Check session timeout hasn't expired
   Login again if inactive > 30 min
```

**Password Policy Blocking User:**
```
Issue: User cannot set password
Solution:
1. Gateway > Security > User Source > Password Policy
2. Review minimum length, complexity requirements
3. Verify password meets all criteria:
   - Length: 12+ characters
   - Uppercase: At least one A-Z
   - Number: At least one 0-9
   - Special: At least one !@#$%^&*
4. Reset user password as admin
```

**Certificate Expiration Blocking Access:**
```
Error: "NET::ERR_CERT_DATE_INVALID"
Solution:
1. Import new valid certificate
   Gateway > Configure > Security > SSL/TLS
2. Verify certificate not expired:
   openssl x509 -in cert.pem -noout -dates
3. Check system time on gateway (NTP sync)
   Gateway > Configure > System > Date & Time
4. Restart gateway after certificate import
5. Clear browser cache and try again
```

**Failed Login Attempts Locking User:**
```
Error: "Account locked - too many failed attempts"
Solution:
1. Verify correct password entered
2. Check CAPS LOCK is off
3. Wait for lockout period (typically 15 min)
   OR
4. Admin unlock:
   Gateway > Security > Users > [User] > Unlock
5. Reset password via self-service if enabled
```

### 9.2 Audit Log Review

**Accessing Audit Logs:**
```
Gateway > Configure > System > Audit Logs
Filters: User, Event Type, Date Range
Export: Download as CSV/JSON
View: Chronological entry details
```

**Key Events to Monitor:**
```
Authentication:
  - User login success/failure
  - Failed login attempts (3+)
  - Logout events
  
Authorization:
  - Tag write operations
  - Configuration changes
  - Designer project edits
  - Permission changes
  
Gateway:
  - Startup/shutdown
  - Certificate updates
  - Database connection issues
  - Service restarts
```

---

## 10. SECURITY CHECKLIST

### Pre-Production Deployment

- [ ] Change default admin password
- [ ] Configure password policy (min 12 chars, complexity)
- [ ] Import valid SSL/TLS certificate (not self-signed)
- [ ] Enable HTTPS redirect and HSTS headers
- [ ] Configure user sources (LDAP/OAuth if available)
- [ ] Create roles with appropriate permissions
- [ ] Assign users to roles (no direct permissions)
- [ ] Configure view/tag permissions
- [ ] Enable audit logging
- [ ] Configure session timeouts (30 min default)
- [ ] Set up monitoring/alerting for failed logins
- [ ] Review and restrict designer access
- [ ] Configure CORS if using external APIs
- [ ] Set API rate limiting
- [ ] Test backup/restore procedures
- [ ] Document access controls
- [ ] Security awareness training for admins/users

### Ongoing Maintenance

- [ ] Monthly review of audit logs (failed logins, changes)
- [ ] Quarterly: Role/permission audit
- [ ] Quarterly: Remove inactive users
- [ ] Quarterly: Review API keys in use
- [ ] Quarterly: Check for expired certificates
- [ ] Bi-annually: Rotate admin passwords
- [ ] Annually: Full security assessment
- [ ] Annually: Update security documentation
- [ ] Monitor Ignition security advisories
- [ ] Apply patches within 30 days
- [ ] Test patches in dev environment first
- [ ] Maintain current certificate renewals
- [ ] Review and update password policy
- [ ] Conduct security awareness training

---

## 11. QUICK REFERENCE

### Authentication Commands

```python
# Get current user
user = system.user.getUser()
username = user.name
full_name = user.fullName
roles = user.roles  # List of role names
is_authenticated = system.user.isAuthenticated()

# Check if user has role
if "admin" in system.user.getRoles():
    print("User is admin")

# Get current session info
session_timeout = system.user.getSessionTimeout()
```

### Permission Check Pattern

```python
# Common permission check in scripts:
def check_permission(required_role):
    user = system.user.getUser()
    if required_role in user.roles:
        return True
    else:
        print(f"Permission denied: {required_role} required")
        return False

# Before critical operation:
if check_permission("admin"):
    # Perform admin-only action
    system.db.runUpdateQuery("UPDATE table SET...")
```

### Common Gateway Paths

```
Gateway Address: https://gateway-hostname:8088/
Gateway Configuration: https://gateway-hostname:8088/admin
Designer Launcher: https://gateway-hostname:8088/designer
Perspective Views: https://gateway-hostname:8088/data/perspective/client/
API Endpoint: https://gateway-hostname:8088/api/v1/
Status/Health: https://gateway-hostname:8088/status
```

---

## References

- Ignition 8.3 Platform Documentation: docs.inductiveautomation.com/docs/8.3/platform/security
- NIST Cybersecurity Framework
- OWASP Top 10
- IEC 62443 (Industrial Automation and Control Systems Security)

**Last Updated:** July 2026
**Version:** Ignition 8.3.x
**Document Status:** Complete Reference

---

## See Also

**Prerequisites:** [50-SECURITY-MODEL](50-SECURITY-MODEL.md)

**Builds toward:** [61-GATEWAY-MANAGEMENT](61-GATEWAY-MANAGEMENT.md), [88-OPC-UA-SERVER-CONFIGURATION](88-OPC-UA-SERVER-CONFIGURATION.md), [93-MOBILE-MODULE-OPERATIONS](93-MOBILE-MODULE-OPERATIONS.md)

**Related:** [50-SECURITY-MODEL](50-SECURITY-MODEL.md), [61-GATEWAY-MANAGEMENT](61-GATEWAY-MANAGEMENT.md), [88-OPC-UA-SERVER-CONFIGURATION](88-OPC-UA-SERVER-CONFIGURATION.md), [84-CLUSTERING-HA-ARCHITECTURE](84-CLUSTERING-HA-ARCHITECTURE.md)

[↑ Back to INDEX](00-INDEX.md) · [Knowledge Graph](KNOWLEDGE-GRAPH.md)
