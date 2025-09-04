# 🏗️ Arquitectura del Sistema

## Arquitectura a Alto Nivel

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│   FRONTEND      │◄──►│   BACKEND       │◄──►│   DATABASE      │
│                 │    │                 │    │                 │
│ • HTML/CSS/JS   │    │ • Django Views  │    │ • SQLite/       │
│ • Bootstrap 5   │    │ • REST API      │    │   PostgreSQL    │
│ • Responsive    │    │ • Business      │    │ • 6 Modelos     │
│ • AJAX          │    │   Logic         │    │ • Relaciones    │
│                 │    │ • Authentication│    │   Complejas     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         │              │                 │              │
         └──────────────►│   MIDDLEWARE    │◄─────────────┘
                        │                 │
                        │ • Rate Limiting │
                        │ • Security      │
                        │ • CORS          │
                        │ • Caching       │
                        └─────────────────┘
```

## Componentes Principales

### 1. Frontend Layer

**Tecnologías**: HTML5, CSS3, Bootstrap 5, JavaScript, AJAX

**Responsabilidades**:

- Interfaz de usuario responsive
- Formularios interactivos con validación
- Comunicación asíncrona con API
- Experiencia de usuario optimizada

**Características**:

- **Mobile-First Design**: Responsive en todos los dispositivos
- **Progressive Enhancement**: Funciona sin JavaScript
- **Accessibility**: Cumple estándares WCAG
- **Performance**: Optimización de assets y carga

### 2. Backend Layer

**Framework**: Django 5.1.2 (Python)

**Componentes**:

- **Views**: Lógica de presentación y control
- **Models**: Definición de datos y relaciones
- **Forms**: Validación y procesamiento de datos
- **API**: Endpoints REST para funcionalidades avanzadas
- **Authentication**: Sistema de usuarios integrado

**Patrones Implementados**:

- **MVC (Model-View-Controller)**: Separación de responsabilidades
- **Repository Pattern**: Abstracción de acceso a datos
- **Service Layer**: Lógica de negocio centralizada
- **Decorator Pattern**: Rate limiting y permisos

### 3. Database Layer

**Desarrollo**: SQLite | **Producción**: PostgreSQL

**Modelos de Datos**:

```python
User (AbstractUser)
├── Listing (1:N)
├── Bid (1:N)
├── Comment (1:N)
├── Watchlist (1:N)
└── Notification (1:N)

Listing
├── Bid (1:N)
├── Comment (1:N)
├── Watchlist (1:N)
└── Notification (1:N)
```

### 4. Middleware Layer

**Funcionalidades**:

- **Rate Limiting**: Protección contra abuso
- **Security Headers**: XSS, CSRF, Clickjacking
- **CORS**: Cross-Origin Resource Sharing
- **Caching**: Optimización de performance
- **Logging**: Monitoreo y debugging

## Flujo de Datos

### 1. Flujo de Creación de Subasta

```
Usuario → Formulario → Validación → Modelo Listing → Base de Datos
   ↓
Notificación → Watchlist Users → Email/Push Notification
```

### 2. Flujo de Puja

```
Usuario → Bid Form → Validación Business Logic → Actualización Listing
   ↓
Notificación → Previous Bidder → Listing Owner → Watchers
```

### 3. Flujo de API

```
Cliente → API Endpoint → Serializer → View → Model → Database
   ↓
Response ← JSON Serializer ← Business Logic ← Query Result
```

## Seguridad

### Medidas Implementadas

- **Authentication**: Django's built-in system
- **Authorization**: Permission-based access control
- **CSRF Protection**: Cross-Site Request Forgery
- **XSS Protection**: Input sanitization
- **SQL Injection**: ORM protection
- **Rate Limiting**: Custom decorator implementation
- **Input Validation**: Form and model validation

### Rate Limiting Configuration

```python
RATE_LIMITS = {
    'API_ANONYMOUS': '20/m',
    'LOGIN_ATTEMPTS': '5/m',
    'LISTING_CREATION': '5/m',
    'BIDDING': '10/m',
    'COMMENTS': '10/m'
}
```

## Escalabilidad

### Estrategias Implementadas

- **Database Indexing**: Optimización de queries
- **Pagination**: Manejo eficiente de grandes datasets
- **Caching**: Redis para datos frecuentes
- **Static Files**: CDN para assets
- **API Design**: RESTful para integración

### Preparación para Crecimiento

- **Microservices Ready**: Arquitectura modular
- **Container Support**: Docker configuration
- **Load Balancer Ready**: Stateless design
- **Database Sharding**: Preparado para particionado

## Deployment Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   CDN       │    │ Load        │    │ App         │
│ (Static)    │    │ Balancer    │    │ Servers     │
└─────────────┘    └─────────────┘    └─────────────┘
                           │                   │
                   ┌─────────────┐    ┌─────────────┐
                   │ Database    │    │ Redis       │
                   │ (Primary)   │    │ (Cache)     │
                   └─────────────┘    └─────────────┘
```

## Monitoreo y Observabilidad

- **Logging**: Structured logging con Django
- **Metrics**: Performance y business metrics
- **Health Checks**: Endpoints de salud
- **Error Tracking**: Manejo centralizado de errores
