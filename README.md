# EduFee – Student Fee Management & Reconciliation System

EduFee is a Django-based student fee management system designed to manage students, fee structures, concessions, invoices, installments, payments, and payment reconciliation.

The system is being developed as a traditional server-rendered web application using Django Templates, HTML, CSS, and minimal JavaScript.

---

## 🚀 Project Overview

Educational institutions often manage student fees across multiple fee heads, concessions, invoices, installments, and payment transactions.

EduFee aims to provide a centralized system where:

- Students can view their fee-related information.
- Accounts staff can manage students, fee structures, concessions, invoices, and installments.
- Administrators can manage the overall system.
- Payment transactions can be tracked through explicit payment states.
- Payment records can later be reconciled with external gateway transactions.
- Financial changes can be audited.

The main focus of the project is **financial consistency, authorization, traceability, and maintainability**.

---

## 🛠️ Technology Stack

### Backend
- Python
- Django 5.2

### Frontend
- Django Templates
- HTML5
- CSS3
- Minimal JavaScript

### Database
- SQLite for development

### Authentication
- Django Authentication System
- Role-based access using Django Groups and Permissions

### Development Tools
- Git
- GitHub
- VS Code

---

## 📁 Project Structure

```text
Fee_application/
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── accounts/
│   ├── management/
│   │   └── commands/
│   │       └── setup_roles.py
│   ├── permissions.py
│   ├── urls.py
│   └── views.py
│
├── students/
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
│
├── fees/
│   ├── models.py
│   ├── forms.py
│   ├── services.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
│
├── payments/
├── reconciliation/
├── audit/
├── reports/
│
├── templates/
│   ├── base.html
│   ├── accounts/
│   ├── students/
│   └── fees/
│
├── static/
│   └── css/
│
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md
