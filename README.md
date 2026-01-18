# IP Tracking & Security Middleware (Django)

## Overview

This project implements a **Django-based IP tracking and security module** designed to improve application security, monitoring, and abuse prevention.  
It demonstrates core backend security concepts such as IP logging, blacklisting, geolocation, rate limiting, and anomaly detection using simple, maintainable tools.

The implementation prioritizes **clarity, performance, and ethical considerations**, making it suitable for learning and extension.

---

## Objectives Implemented

- Log incoming requests with IP address, timestamp, and path
- Block known malicious IP addresses
- Enrich request logs with geolocation data (country, city)
- Prevent abuse through rate limiting
- Detect suspicious IP behavior using rule-based anomaly detection
- Follow privacy and ethical best practices

---

## Key Features

### 1️⃣ IP Logging
- Logs:
  - IP address
  - Request path
  - Timestamp
  - Country & city (via GeoIP)
- Implemented using **custom Django middleware**

---

### 2️⃣ IP Blacklisting
- Blocks requests from known malicious IPs
- Returns **HTTP 403 Forbidden**
- Managed via:
  - `BlockedIP` model
  - Custom Django management command

---

### 3️⃣ IP Geolocation
- Uses **MaxMind GeoLite2 City** database
- Maps IPs to:
  - Country
  - City
- Results are cached for **24 hours** to improve performance

---

### 4️⃣ Rate Limiting
- Prevents abuse of sensitive endpoints (e.g. login)
- Implemented with **django-ratelimit**
- Limits:
  - **Authenticated users:** 10 requests/minute
  - **Anonymous users:** 5 requests/minute
- Returns **HTTP 429 Too Many Requests**

---

### 5️⃣ Anomaly Detection
- Uses a **Celery background task** that runs hourly
- Flags IPs that:
  - Exceed **100 requests/hour**
  - Access sensitive paths (`/admin`, `/login`)
- Flagged IPs are stored for review (not auto-blocked)

---

## Key Concepts Covered

| Concept | Description |
|------|------------|
| IP Logging | Request auditing and debugging |
| Blacklisting | Blocking known bad actors |
| IP Geolocation | Geographic enrichment of requests |
| Rate Limiting | Abuse prevention |
| Anomaly Detection | Early threat identification |
| Privacy & Ethics | Responsible handling of IP data |

---

## Tools & Libraries Used

- **Django Middleware** – request interception and logging
- **django-ipware** – reliable client IP extraction
- **django-ratelimit** – request rate limiting
- **GeoIP2 (MaxMind GeoLite2)** – IP geolocation
- **Celery** – background anomaly detection tasks
- **SQLite** – development database

---

## Project Structure
ip_tracking/
├── middleware.py
├── models.py
├── views.py
├── tasks.py
├── management/
│ └── commands/
│ └── block_ip.py
config/
├── settings.py
geoip/
└── GeoLite2-City.mmdb


---

## GeoIP Configuration
```python
GEOIP_PATH = BASE_DIR / "geoip"


----


## Testing & Validation
- IP logs stored in the database
- Blocked IPs receive 403 Forbidden
- Rate-limited requests receive 429 Too Many Requests
- Suspicious IPs are flagged automatically every hour


## Privacy & Ethical Considerations
- IP data is collected strictly for security purposes
- Logs should have limited retention in production
- IP anonymization or truncation is recommended
- Privacy policies should disclose IP tracking usage

## Future Improvements
- Redis for caching and rate limiting
- Automatic blocking of flagged IPs
- Dashboard for security analytics
- Advanced anomaly detection using ML
- Log rotation and retention policies


## License
- This project is intended for educational purposes and security learning demonstrations.