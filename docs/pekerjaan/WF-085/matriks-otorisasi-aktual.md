# Implemented authorization

| Caller / action | Result |
|---|---|
| Guest GET /admin | Redirect to login; JSON request returns 401 |
| Active admin with current session | Protected landing page; operate-internal gate allowed |
| Non-admin or inactive credentials | Generic failed login; no session authenticated |
| Admin disabled after login | Gate denies the next request with 403 |
| Idle 30 minutes / absolute 8 hours / missing timestamp | Session invalidated; login required |
| Sixth failed login for normalized email + IP within 60 seconds | 429 with Retry-After |
| POST login/logout without antiforgery proof | Framework CSRF rejection (419) |
| Registration/profile role writes | No public routes; role fields rejected on login and guarded against mass assignment |
| Admin web session requesting draft through public API | Existing published-only runtime/RLS restriction remains |
| Runtime minting operator tokens or updating admin flags | No database grants and no web routes |
| Private account provisioning | Privileged CLI only, hidden password input, no existing-account mutation |

Session cookies remain HttpOnly/SameSite=Lax and default to Secure in production. Successful login regenerates the session and CSRF token; logout invalidates the session and regenerates CSRF. Password hashes are hidden from model serialization. Publisher credentials and tokens are not stored in browser sessions.
