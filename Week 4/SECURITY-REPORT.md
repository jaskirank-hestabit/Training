# SECURITY REPORT

**Base URL**: http://localhost:5000/api
**Environment**: Development
**Security Middleware Implemented**:
  - Joi Schema Validation
  - Payload Whitelisting (stripUnknown)
  - Rate Limiting (express-rate-limit)
  - Helmet (secure headers)
  - CORS Policy
  - Parameter Pollution Protection (hpp)
  - NoSQL Injection Sanitization
  - Payload Size Limiting

---

1. Schema-Level Validation (Joi)

Test 1: Invalid Query Parameter
Request: GET /api/products?page=-5
Expected Result
Status: 400
Code: VALIDATION_ERROR
Invalid query values are rejected before reaching business logic.
Screenshot:
![Invalid Query Parameter](./screenshots/day4/security-test-1.png)

Test 2: Invalid Sort Format
GET /api/products?sort=price:hack
Expected: 400 VALIDATION_ERROR
Regex validation prevents invalid sort injection.
Screenshot:
![Invalid Sort Format](./screenshots/day4/security-test-2.png)

Test 3: Invalid MongoDB ID
DELETE /api/products/123
Expected: 400 INVALID_ID
ObjectId validation prevents malformed ID attacks.
Screenshot:
![Invalid MongoDB ID](./screenshots/day4/security-test-3.png)

2. Payload Whitelisting

Request

POST /api/products
body: 
{
  "name": "iPhone",
  "price": 1000,
  "isAdmin": true
}

Expected Behavior:
Product created
isAdmin field removed automatically
Unknown fields stripped using:
stripUnknown: true

Screenshot: DB record without isAdmin
![Payload Whitelisting](./screenshots/day4/security-test-4.png)

3. NoSQL Injection Protection

Request

{
  "name": { "$gt": "" },
  "price": 100
}

Expected:
Validation failure
Injection does not execute
Operators like $gt are sanitized and blocked.

Screenshot:
![NoSQL Injection Protection](./screenshots/day4/security-test-5.png)

4. XSS Protection

Request

{
  "name": "<script>alert('hack')</script>",
  "price": 200
}

Expected:
Script tags removed or rejected
Stored value does not contain executable script.

Screenshot:
![XSS Protection](./screenshots/day4/XSS-protection.png)

5. Parameter Pollution Protection

Request

GET /api/products?page=1&page=2

Expected:
Request rejected (strict validation) 
No crash
Duplicate query parameters are rejected with 400 validation error.
System does not allow ambiguous input.
Screenshot:
![Parameter Pollution Protection](./screenshots/day4/security-test-6.png)

6. Rate Limiting

Test Command
for i in {1..120}; do curl http://localhost:5000/api/products; done

Expected:
Status: 429
Code: RATE_LIMIT_EXCEEDED
After 100 requests within 15 minutes, further requests are blocked.

Screenshot:
![Rate limit](./screenshots/day4/rate-limit.png)

7. Payload Size Limiting

Test:
Send JSON body larger than 10KB.
Expected:
413 Payload Too Large
Large payloads are rejected using:
express.json({ limit: "10kb" })

Screenshot:
![Payload Size Limiting](./screenshots/day4/payload-size-limiting.png)

8. Helmet Header Hardening

Checked Response Headers in Browser DevTools.
Headers Present:
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
Content-Security-Policy
Security headers successfully applied.

Screenshot: Network -> Response Headers
![Helmet Header Hardening](./screenshots/day4/helmet-headers.png)

9. CORS Policy Enforcement

Tested API call from unauthorized origin.
Expected:
Blocked by browser.
CORS restricts requests to allowed origins only.

Screenshot:
![CORS Policy Enforcement](./screenshots/day4/cors-blocked.png)