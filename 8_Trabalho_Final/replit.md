# Natjus (Sistema de Pareceres Jurídicos)

## Overview

Natjus is a comprehensive Legal Opinion Management System (Sistema de Pareceres Jurídicos) built with Python Flask. Its primary purpose is to manage legal opinions (pareceres) through a multi-stage workflow, providing specialized dashboards with sorting, searching, and filtering capabilities. The system features a sophisticated form interface with stage-based validation and tab management, ensuring a structured progression of legal opinions. Natjus is fully authenticated, requiring user login for all functionalities, and aims to streamline the legal opinion process within an organization.

## User Preferences

Preferred communication style: Simple, everyday language (Portuguese).

## System Architecture

### Backend Architecture

**Framework**: Flask (Python web framework) is used for a single-server application architecture, including session management and flash messaging for user feedback.

**Database Layer**: SQLAlchemy ORM with PostgreSQL manages data. It features connection pooling, automatic table creation, and seed data population on startup. A migration system automatically verifies and creates the `id_elaborador` column.

**Data Models**:
-   **Parecer**: Core entity for legal opinions, tracking workflow stages (INICIADO, ELABORACAO, REVISAO, PRONTO_ENVIO), stage-specific validation, and automatic timestamps. Includes `id_elaborador` for tracking the elaborating user.
-   **Prazo**: Defines deadline options.
-   **Usuario**: Manages users with roles, including `nome`, `email`, `senha_hash`, and `perfil_id`.
-   **Perfil**: Defines user roles (Administrativo, Parecerista, Admin) for access control.
-   **Documento**: Handles document attachments with `nome_arquivo` and `url`.

**Design Pattern**: MVC (Model-View-Controller) separates concerns: Models for data and business logic, Views for Jinja2 templates with HTML/TailwindCSS, and Controllers for Flask route handlers.

### Frontend Architecture

**UI Framework**: TailwindCSS via CDN provides a responsive, utility-first design without a build process. Color-coded stage indicators and a tabbed interface enhance user experience.

**Template Structure**: Includes `base.html`, `index.html`, `painel_geral.html`, `painel_parecerista.html`, `historico.html`, `editar.html`, and `visualizar.html` for various views and forms.

**Dashboard Panels System**:
-   **Painel Geral (`/dashboard`)**: For Admin and Administrativo users, showing all pareceres with full management capabilities.
-   **Painel do Parecerista (`/meus-pareceres`)**: For Parecerista and Admin users, focusing on pareceres in ELABORACAO and REVISAO stages.
-   **Histórico de Pareceres (`/historico`)**: For all authenticated users, providing a historical view with advanced filtering (process number, status, parecerista, date range).
All panels feature pagination, sorting, and search functionalities.

**User Interface Features**: Includes sortable columns, search and filter options, stage-based tab navigation, row-level actions, and smart redirection based on user roles.

### Data Storage

**Database**: PostgreSQL is the primary data store, accessed via SQLAlchemy and `psycopg2-binary`. The schema is normalized with foreign key relationships and an Enum type for workflow status.

### Workflow Logic

**Stage Progression**: Defines a four-stage workflow (INICIADO → ELABORACAO → REVISAO → PRONTO_ENVIO), with clear transitions and validation.

**Validation Rules**: Enforces required fields at each stage and before advancement, providing clear error messages.

### Authentication and Authorization

**Role-Based Authentication**: A complete system requires login for all features. It includes login/logout, password hashing (scrypt), secure session management, and access control decorators.

**User Profiles and Permissions**:
-   **Admin**: Full system access, including user management.
-   **Administrativo**: Can create new pareceres, edit INICIADO and ELABORACAO stages, and view all pareceres.
-   **Parecerista**: Can edit ELABORACAO and REVISAO stages, and view relevant pareceres.

**User Management**: An Admin-only interface at `/usuarios` allows for listing, creating, editing, and deleting users, with unique email enforcement and password requirements.

## External Dependencies

### Python Packages
-   **Flask**: Web application framework.
-   **SQLAlchemy**: Database ORM.
-   **Flask-SQLAlchemy**: Flask integration for SQLAlchemy.
-   **psycopg2-binary**: PostgreSQL adapter.
-   **Werkzeug.security**: Password hashing.

### Frontend Libraries
-   **TailwindCSS**: Utility-first CSS framework (via CDN).

### Infrastructure Services
-   **PostgreSQL Database**: Primary data storage.
-   **Replit Secrets**: Environment variable management for sensitive configuration.

### Configuration Requirements
-   `DATABASE_URL`: PostgreSQL connection string.
-   `SESSION_SECRET`: Flask session encryption key.