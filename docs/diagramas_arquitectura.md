# 🏗️ Diagramas de Arquitectura - Sistema Empresa

> Fecha: 2026-09-05
> Herramienta de renderizado recomendada: [mermaid.live](https://mermaid.live)

---

## 1️⃣ Arquitectura General del Sistema

Visión global de cómo se conectan los componentes principales.

```mermaid
flowchart TB
    subgraph ENTRY["🚪 Punto de Entrada"]
        APP[app.py]
        WSGI[wsgi.py]
    end

    subgraph AUTH["🔐 Autenticación"]
        LOGIN[auth/login.py]
        USERS[(users.json)]
    end

    subgraph CORE["⚙️ Núcleo Reutilizable (core/)"]
        direction TB
        REG[blueprint_registry.py]
        MENU[menu.py]
        DBJSON[db_json.py]
        ARBOL[arbol_bp.py]
        CRUDBP[crud_bp.py]
        EVENT[event.py]
        CAL[calendar.py]
        SCH[scheduler.py]
    end

    subgraph APPS["📦 Aplicaciones (templates/Aplic/*)"]
        direction LR
        A1[agenda]
        A2[tareas]
        A3[pagos]
        A4[estadosderepuestos]
        A5[listarepuestos]
        A6[instalaciones]
        A7[crearrubros]
        A8[crearalmacenes]
        A9[crearubicaciontecnica]
        A10[gestiondebloqueos]
        A11[estadisticadeparadas]
        A12[graficosrepuestos]
        A13[listarot]
        A14[bajadadeot]
        A15[GestionAplic]
        A16[detectorderostros]
    end

    subgraph DATA["💾 Persistencia (DataBase/)"]
        direction LR
        D1[(Config/menu.json)]
        D2[(time/agenda.json)]
        D3[(time/dataTask.json)]
        D4[(hogar/GASTOS.json)]
        D5[(dataRep/REPUESTOS.json)]
        D6[(dataRep/almacenes.json)]
        D7[(dataRep/ubicacion_tecnica.json)]
        D8[(dataRep/rubro.json)]
        D9[(dataOT/ordenes_*.JSON)]
        D10[(planos/nodo.json)]
    end

    subgraph STATIC["🎨 Frontend Estático"]
        direction LR
        CSS[css/base + css/apps]
        JS[js/apps + js/utils]
        TPL[templates/layout.html]
    end

    WSGI --> APP
    APP --> AUTH
    APP --> CORE
    APP --> APPS

    REG -.descubre.-> APPS
    APPS --> CORE
    APPS --> DATA
    AUTH --> USERS
    CORE --> DATA
    MENU --> D1

    APPS --> STATIC
    TPL --> CSS
    TPL --> JS
```

**Leyenda de conexiones:**
- `──▶` dependencia directa / import
- `-.─▶` relación indirecta / descubrimiento dinámico

---

## 2️⃣ Flujo de Auto-Registro de Blueprints

Cómo el sistema descubre y registra automáticamente cada aplicación nueva **sin tocar `app.py`**.

```mermaid
sequenceDiagram
    participant W as wsgi.py
    participant A as app.py
    participant R as blueprint_registry.py
    participant FS as Filesystem<br/>(templates/Aplic/*)
    participant F as Flask App

    W->>A: import app
    A->>A: init_routes_login(app)
    A->>R: auto_register_blueprints(app)

    loop Por cada carpeta en templates/Aplic/*/BackEnd/
        R->>FS: glob("*/BackEnd/*.py")
        FS-->>R: lista de módulos
        loop Por cada archivo .py
            R->>R: importlib.import_module()
            R->>R: buscar atributos Blueprint
            alt Es instancia de Blueprint
                R->>F: app.register_blueprint(bp)
                Note over R,F: Nombre único evita duplicados
            end
        end
    end

    R-->>A: (registered, errors)
    A->>A: setup_scheduler(app, mail)
    A->>A: context_processor inject_menu()
    A-->>W: app lista
```

**Ventaja clave:** agregar una app nueva = solo crear la carpeta, **cero cambios en `app.py`**.

---

## 3️⃣ Módulos Core y sus Consumidores

Qué aplicaciones usan cada módulo reutilizable de `core/`.

```mermaid
flowchart LR
    subgraph CORE["core/"]
        ARBOL[arbol_bp.py<br/>crear_blueprint_arbol]
        CRUD[crud_bp.py<br/>crear_blueprint_crud]
        DBJSON[db_json.py<br/>JsonStore]
        EVENT[event.py<br/>EventStore]
        MENU[menu.py<br/>cargar_menu/guardar_menu]
        CAL[calendar.py<br/>generar_calendario]
        SCH[scheduler.py<br/>setup_scheduler]
    end

    subgraph CONSUMIDORES["Apps que lo usan"]
        CR1[crearrubros]
        CR2[crearalmacenes]
        CR3[crearubicaciontecnica]
        CR4[gestion_menu]
        CR5[crear_procedimiento]

        TA[tareas]

        AG[agenda]
        AP[app.py]

        PA[pagos]
        ER[estadosderepuestos]
        LR[listarepuestos]
        GR[graficosrepuestos]
        IN[inventario]
        INST[instalaciones]

        TODAS[todas las apps]
    end

    ARBOL --> CR1
    ARBOL --> CR2
    ARBOL --> CR3
    ARBOL --> CR4
    ARBOL --> CR5

    CRUD --> TA

    DBJSON --> TA
    DBJSON --> ER
    DBJSON --> INST

    EVENT --> AG
    EVENT --> SCH

    MENU --> TODAS
    CAL -.usada por.-> AG
    SCH --> AP
```

---

## 4️⃣ Flujo de Autenticación y Autorización

Cómo se valida el acceso a las rutas protegidas.

```mermaid
flowchart TB
    U[Usuario] -->|GET /login| LG[login()]
    U -->|POST credenciales| LG
    U -->|POST rostro| LGF[login_rostro()]

    LG -->|valida| UD[users.json]
    LGF -->|compara| CV[comparar_rostros<br/>OpenCV]
    CV -->|lee| IMG[static/rostros/*.png]

    LG -->|éxito| LU[login_user]
    LGF -->|éxito| LU
    LU -->|crea| SE[Session Cookie]
    SE -->|redirige| IX[index /]

    subgraph PROTECCION["En cada ruta protegida"]
        LR2[@login_required]
        RR[@roles_required]
        CM[cargar_menu]
        CP[context_processor<br/>inject_menu]
    end

    IX --> LR2
    LR2 -->|valida sesión| RR
    RR -->|valida rol| RR2[Handler de la app]
    RR2 --> CM

    CP -.inyecta.-> TPL[layout.html]
    CM -.renderiza.-> TPL

    LG -->|fallo| FL[flash error]
    LGF -->|fallo| FL
```

**Roles del sistema:** `admin`, `editor`, `viewer`

---

## 5️⃣ Flujo de Datos (JSON Stores)

Cómo las aplicaciones leen y escriben datos persistentes.

```mermaid
flowchart TB
    subgraph APPS["Aplicaciones"]
        AG[agenda]
        TA[tareas]
        PA[pagos]
        ER[estadosderepuestos]
        IN[inventario]
        INST[instalaciones]
        RUB[crearrubros]
        ALM[crearalmacenes]
        UBI[crearubicaciontecnica]
        BLQ[gestiondebloqueos]
        OT[listar_ot]
        BD[bajada_de_ot]
    end

    subgraph STORES["JsonStore / helpers"]
        JS1[EventStore]
        JS2[JsonStore]
        HP[helpers.py<br/>cargar_almacenes<br/>cargar_estados<br/>cargar_ubicaciones]
        MD[models.py<br/>leer_repuestos]
    end

    subgraph FILES["Archivos JSON"]
        F1[(agenda.json)]
        F2[(dataTask.json)]
        F3[(GASTOS.json)]
        F4[(GASTO_YYYY_MM.json)]
        F5[(REPUESTOS.json)]
        F6[(almacenes.json)]
        F7[(ubicacion_tecnica.json)]
        F8[(rubro.json)]
        F9[(tabs.json)]
        F10[(estados.json)]
        F11[(nodo.json)]
        F12[(ordenes_*.JSON)]
        F13[(menu.json)]
    end

    AG --> JS1 --> F1
    TA --> JS2 --> F2
    PA --> F3
    PA --> F4
    ER --> MD --> F5
    ER --> HP
    IN --> F6
    IN --> F5
    INST --> F7
    RUB --> F8
    ALM --> F6
    UBI --> F7
    BLQ --> F11
    OT --> F12
    BD --> F12
    BD --> F1

    HP --> F6
    HP --> F7
    HP --> F8
    HP --> F9
    HP --> F10

    ER --> F9
```

---

## 6️⃣ Frontend: Módulos JS y su Relación con Backend

Cómo los scripts JS consumen las APIs Flask.

```mermaid
flowchart TB
    subgraph JSUTIL["js/utils/ (reutilizables)"]
        JU1[selectores_nivel.js<br/>SelectoresNivel]
        JU2[calendar.js<br/>Calendar]
        JU3[event_modal.js<br/>EventModal]
        JU4[notificaciones.js]
    end

    subgraph JSAPPS["js/apps/ (específicos)"]
        JA1[arbol_crud.js<br/>ArbolCRUD]
        JA2[logger.js<br/>Logger]
        JA3[image_uploader.js<br/>ImageUploader]
        JA4[layout_scripts.js]
        JA5[modal_animations.js]
        JA6[pagos.js / newPagos.js]
        JA7[tareas.js]
        JA8[agenda.js / evento.js]
        JA9[instalaciones.js]
        JA10[repuestoForm.js<br/>repuestoEvents.js<br/>repuestoUtils.js]
    end

    subgraph APIs["APIs Flask"]
        API1[/api/rubro_arbol<br/>/api/rubro]
        API2[/api/ubicacion_arbol<br/>/api/ubicacion]
        API3[/api/crear_almacenes_arbol<br/>/api/crear_almacenes]
        API4[/api/tareas]
        API5[/agenda/eventos]
        API6[/pagos/*]
        API7[/api/repuestos]
        API8[/api/ubicaciones<br/>/api/editar_ubicacion]
        API9[/api/subir_imagen]
    end

    subgraph LIBS["Librerías CDN"]
        L1[Bootstrap 5]
        L2[Select2]
        L3[SweetAlert2]
        L4[Noty]
        L5[ECharts]
        L6[MediaPipe]
    end

    JA1 --> API1
    JA1 --> API2
    JA1 --> API3
    JA1 --> L3
    JA1 --> L4

    JU1 --> API1
    JA6 --> JU1
    JA6 --> API6

    JA7 --> API4
    JA7 --> JA2
    JA7 --> L3
    JA7 --> L4

    JA8 --> API5
    JA8 --> JU2
    JA8 --> JU3

    JA9 --> API8
    JA9 --> API9
    JA9 --> JA3
    JA9 --> JA2

    JA10 --> API7
    JA10 --> L2

    JA4 --> L1
    JA5 --> L1
```

---

## 7️⃣ Diagrama de Caperas (resumen ejecutivo)

```mermaid
graph TB
    subgraph L1["Capa 1 — Presentación"]
        HTML[templates/*.html]
        CSS[static/css/]
        JS[static/js/]
    end

    subgraph L2["Capa 2 — Rutas / Blueprints"]
        BP[Blueprints por app<br/>templates/Aplic/*/BackEnd/*.py]
        APPPY[app.py + rutas globales]
    end

    subgraph L3["Capa 3 — Lógica de Negocio"]
        CORE2[core/*.py]
        HELP[helpers.py / services.py / models.py]
    end

    subgraph L4["Capa 4 — Persistencia"]
        JSON[(JSON files en DataBase/)]
    end

    subgraph L5["Capa 5 — Infraestructura"]
        AUTH2[auth/login.py]
        MAIL[Flask-Mail]
        SCH2[APScheduler]
    end

    L1 <-->|HTTP / fetch| L2
    L2 <-->|import| L3
    L3 <-->|read/write| L4
    L2 --> L5
    L5 --> L4
```

---

## 📌 Resumen de Conexiones Clave

| Módulo | Conecta con | Propósito |
|---|---|---|
| `app.py` | `auth/`, `core/`, `templates/Aplic/` | Orquestador principal |
| `blueprint_registry.py` | `templates/Aplic/*/BackEnd/*.py` | Auto-descubrimiento |
| `arbol_bp.py` | 5 apps (rubros, almacenes, ubicaciones, menú, procedimiento) | CRUD jerárquico genérico |
| `db_json.py` | 8+ apps | Persistencia JSON con ID autoincremental |
| `event.py` | agenda, scheduler | Gestión de eventos con recordatorios |
| `menu.py` | TODAS las apps | Menú de navegación global |
| `auth/login.py` | TODAS las rutas `@login_required` | Sesiones + roles + facial |
| `ArbolCRUD` (JS) | `arbol_bp.py` (backend) | Frontend del CRUD jerárquico |
| `SelectoresNivel` (JS) | APIs de árbol | Selectores multinivel reutilizables |
| `ImageUploader` (JS) | `/api/subir_imagen` | Subida de imágenes con drag&drop |
| `Logger` (JS) | Todos los módulos JS | Logs profesionales con colores |