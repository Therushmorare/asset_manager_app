# Talius Asset Manager

Enterprise-Grade Asset Lifecycle Management System  
Built with Flask, Flask-RESTX, Celery, JWT, and PostgreSQL.

---

## Overview

Talius Asset Manager is a scalable backend system designed to manage the complete lifecycle of organizational assets — from acquisition to depreciation, verification, disposal, and compliance tracking.

It provides secure role-based access control, financial depreciation processing, disposal workflows, audit logging, and background task processing.

---

## Core Features

### Authentication & Authorization
- JWT-based authentication
- Role-Based Access Control (RBAC)
- SUPERADMIN protections
- Login attempt protection
- Soft deletion of users
- MFA-ready architecture

### Asset Management
- Create, edit, and scan assets
- Bulk asset import via CSV
- QR code generation per asset
- Department and custodian assignment
- Asset verification workflows
- Status tracking:
  - ACTIVE
  - DAMAGED
  - MISSING
  - DESTROYED
  - DISPOSED

### Financial Depreciation Engine
- Automated monthly depreciation
- Supported methods:
  - Straight Line
  - Reducing Balance
  - Units of Production
- Residual value protection
- Duplicate period prevention
- Idempotent processing
- Background task execution (Celery)

### Disposal Workflow
- Custodian disposal requests
- Admin approval or rejection
- Gain/Loss calculation
- Automatic asset status update
- Full audit logging

### Audit & Compliance
- Activity logging
- Verification history tracking
- Financial change validation
- Role-restricted edits
- Protection against editing disposed assets

---

## Tech Stack

- Backend: Flask  
- API Documentation: Flask-RESTX  
- Authentication: Flask-JWT-Extended  
- ORM: SQLAlchemy  
- Database: PostgreSQL  
- Background Tasks: Celery + Redis  
- Password Hashing: Flask-Bcrypt  
- Rate Limiting: Flask-Limiter  

---

## Project Structure

```text
talius_asset_manager/
│
├── app/
│   ├── models/
│   ├── services/
│   ├── routes/
│   ├── tasks/
│   ├── utils/
│
├── migrations/
├── config.py
├── celery_worker.py
├── requirements.txt
└── run.py