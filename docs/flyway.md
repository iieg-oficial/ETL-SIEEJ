<div align="center">

# Guía de Flyway - ETL SIEEJ

<img src="https://img.shields.io/badge/Flyway-CC0200?style=for-the-badge&logoColor=white" alt="Flyway"/>
<img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL"/>
<img src="https://img.shields.io/badge/just-1D1D1D?style=for-the-badge&logoColor=white" alt="just"/>

---

### Versionado y migraciones de esquema de base de datos

</div>

---

## 📖 Índice

- [¿Qué es Flyway?](#-qué-es-flyway)
- [Instalación](#-instalación)
- [Estructura de migraciones](#-estructura-de-migraciones)
- [Configuración (flyway.conf)](#️-configuración-flywayconf)
- [Comandos disponibles](#-comandos-disponibles)
- [Convención de nombres](#-convención-de-nombres)
- [Agregar una nueva migración](#-agregar-una-nueva-migración)
- [Flujo completo de desarrollo](#-flujo-completo-de-desarrollo)
- [Troubleshooting](#-troubleshooting)

---

## ¿Qué es Flyway?

**Flyway** es una herramienta de versionado de esquemas de base de datos. Aplica scripts SQL en orden, lleva registro de qué scripts ya se ejecutaron y garantiza que todos los ambientes (desarrollo, staging, producción) tengan el **mismo esquema**.

```
migrations/
  censos_economicos/
    sql/
      V1__catalogos_ce.sql      ← se aplicó ✅
      V2__tabla_stg_ce_data.sql ← se aplicó ✅
      V3__diccionario_ce.sql    ← pendiente ⏳
```

> 💡 Flyway nunca modifica un script ya aplicado. Si necesitas cambiar algo, creas una **nueva migración**.

---

## Instalación

### Linux

```bash
# Descargar y extraer Flyway CLI
wget https://download.red-gate.com/maven/release/com/redgate/flyway/flyway-commandline/<version>/flyway-commandline-<version>-linux-x64.tar.gz
tar -xzf flyway-commandline-<version>-linux-x64.tar.gz

# Mover al directorio del sistema
sudo mv flyway-<version> /opt/flyway
```

Para que Flyway sea fácilmente accesible desde cualquier lugar, añádelo a la variable Path de tu sistema. Para ello, abre tu archivo de configuración ~/.bashrc (o ~/.zshrc para shells Zsh) y agregua la siguiente línea:

```bash
export PATH=$PATH:/opt/flyway/flyway-10.18.2

source ~/.bashrc
```
### macOS

```bash
brew install flyway
```

### Windows

1. Descarga el `.zip` desde la [página oficial de Flyway](https://documentation.red-gate.com/fd/command-line-277579359.html?_gl=1*4nv54*_gcl_au*MzY3ODgyMjg0LjE3NzI0NzAyOTc.*_ga*NTg1NTk0NDA2LjE3NzA3MzY5NDU.*_ga_X7VDRWRT4P*czE3NzI0NzI4NDgkbzMkZzEkdDE3NzI0NzI4NjQkajQ0JGwwJGg3MDA4NDA0OTM.)
2. Extrae en `C:\Program Files\Flyway`
3. Agrega `C:\Program Files\Flyway` a la variable de entorno `PATH`

---

### Verificar instalación

```bash
flyway -v
```

---

## Estructura de migraciones

Cada pipeline tiene su propia carpeta de migraciones:

```
migrations/
├── censos_economicos/
│   ├── flyway.conf.example     # Plantilla de configuración (commiteada)
│   ├── flyway.conf             # Tu config local con credenciales (¡NO committear!)
│   └── sql/
│       ├── V1__catalogos_ce.sql
│       ├── V2__tabla_stg_ce_data.sql
│       └── V3__diccionario_ce.sql
├── repd/
│   ├── flyway.conf.example
│   └── sql/
│       └── V1__tablas_repd.sql
├── fiscalia/
│   └── ...
└── cvegeo/
    └── ...
```

> ⚠️ `flyway.conf` contiene credenciales. Está en `.gitignore` y **nunca debe subirse al repo**.

---

## Configuración (flyway.conf)

### 1. Copiar la plantilla

```bash
cp migrations/<pipeline>/flyway.conf.example migrations/<pipeline>/flyway.conf
```

### 2. Editar con tus credenciales

```properties
# migrations/censos_economicos/flyway.conf

flyway.url=jdbc:postgresql://localhost:5432/censos_economicos
flyway.user=sieej_user
flyway.password=mi_pass_seguro
flyway.locations=filesystem:./sql/
flyway.schemas=public
flyway.cleanDisabled=false
```

<table>
<tr>
<td>

**Parámetro** | **Descripción**
:--- | :---
`flyway.url` | URL JDBC de la base de datos
`flyway.user` | Usuario de PostgreSQL
`flyway.password` | Contraseña (¡no la hardcodees en código!)
`flyway.locations` | Ruta a los scripts SQL
`flyway.schemas` | Schema donde se aplican las migraciones
`flyway.cleanDisabled` | `false` permite `flyway clean` (útil en dev)

</td>
</tr>
</table>

> ⚠️ En producción, considera poner `flyway.cleanDisabled=true` para evitar accidentes.

---

## Comandos disponibles

### Opción 1. just (recomendado)

Requiere tener `just` instalado. Ver [Guía de just](just.md).

<table>
<tr>
<td>

**Comando** | **Descripción**
:--- | :---
`just flyway-migrate <pipeline>` | Aplica migraciones pendientes en orden numérico
`just flyway-info <pipeline>` | Muestra qué scripts se aplicaron, están pendientes o fallaron
`just flyway-validate <pipeline>` | Verifica que los scripts aplicados no hayan sido modificados
`just flyway-clean <pipeline>` | Elimina TODAS las tablas, vistas y funciones del schema ⚠️
`just flyway-reset <pipeline>` | Clean + Migrate: reconstruye el schema desde cero ⚠️
---

### Opción 2. base

Comandos directos de Flyway, sin dependencias adicionales.

#### Migrate. Aplicar migraciones pendientes

```bash
flyway -configFiles=migrations/censos_economicos/flyway.conf migrate
```

#### Info. Ver estado de migraciones

```bash
flyway -configFiles=migrations/censos_economicos/flyway.conf info
```

#### Validate - Validar integridad de scripts

```bash
flyway -configFiles=migrations/censos_economicos/flyway.conf validate
```


#### 🗑️ Clean. Eliminar todos los objetos ⚠️

```bash
flyway -configFiles=migrations/censos_economicos/flyway.conf clean
```

> ⚠️ **Destructivo:** Elimina TODAS las tablas, vistas y funciones del schema. Solo usar en desarrollo.

#### 🔄 Reset - Clean + Migrate ⚠️

```bash
flyway -configFiles=migrations/censos_economicos/flyway.conf clean
flyway -configFiles=migrations/censos_economicos/flyway.conf migrate
```

> ⚠️ **Destructivo:** Borra todo y vuelve a aplicar todas las migraciones desde cero. Útil para probar que tus migraciones son reproducibles.

---

## 📝 Convención de nombres

Los archivos SQL deben seguir el formato de Flyway:

```
V{número}__{descripcion_en_snake_case}.sql
```

<table>
<tr>
<td>

**Componente** | **Regla** | **Ejemplo**
:--- | :--- | :---
`V` | Prefijo fijo (Versioned) | `V`
`{número}` | Entero incremental, único | `1`, `2`, `10`
`__` | Separador doble guion bajo | `__`
`{descripcion}` | Snake case, descriptivo | `catalogos_ce`
`.sql` | Extensión fija | `.sql`

</td>
</tr>
</table>

### Ejemplos correctos

```
✅ V1__catalogos_ce.sql
✅ V2__tabla_stg_ce_data.sql
✅ V10__agrega_indice_fecha.sql
✅ V11__vista_resumen_municipio.sql
✅ V1.0__vista_casos.sql

❌ v1_catalogos.sql        (V minúscula)
❌ V1_catalogos.sql        (un solo guion bajo)
❌ V01__catalogos.sql      (cero al inicio - aunque funciona, evitar)
❌ migration_01.sql        (sin prefijo V)
```

> 💡 Los números no necesitan ser consecutivos, solo ordenados. Puedes saltar del `V3` al `V10` sin problema.

---

## ➕ Agregar una nueva migración

### Paso 1.  Identificar el siguiente número

```bash
just flyway-info <pipeline>
# Revisa el último número aplicado o pendiente
```

### Paso 2. Crear el archivo SQL

```bash
# Ejemplo: agregar índice al pipeline censos_economicos
touch migrations/censos_economicos/sql/V4__indice_municipio.sql
```

### Paso 3. Escribir el SQL

```sql
-- migrations/censos_economicos/sql/V4__indice_municipio.sql

-- Agrega índice en columna municipio para mejorar queries de consulta
CREATE INDEX IF NOT EXISTS idx_ce_datos_municipio
    ON public.ce_datos (municipio);
```


### Paso 4. Probar migraciones

```bash
# Ver estado antes
just flyway-info censos_economicos

# Aplicar
just flyway-migrate censos_economicos

# Confirmar
just flyway-info censos_economicos
```

### Paso 5.  Commitear

```bash
git add migrations/censos_economicos/sql/V4__indice_municipio.sql
git commit -m "[FEAT] index on municipio column added to censos_economicos"
```

> Ver [Convención de Commits](convencion-commits.md) para los tipos de commit del proyecto.

---

## 🔄 Flujo completo de desarrollo

Para el flujo completo (levantar BD, aplicar migraciones y ejecutar el pipeline) consulta la [Guía de nuevo flujo](nuevo_flujo.md#-paso-5--probar-localmente).

En resumen:

```bash
# 1. Levantar BD de desarrollo y aplicar migraciones
just build-dev user=sieej_user pass=mi_pass db=sieej
cp migrations/censos_economicos/flyway.conf.example migrations/censos_economicos/flyway.conf
just flyway-migrate censos_economicos

# 2. Desarrollar → agregar migraciones según necesitas

# 3. Verificar reproducibilidad
just flyway-reset censos_economicos

# 4. Validar antes del PR
just flyway-validate censos_economicos
```

---

## 🐛 Troubleshooting

<details>
<summary><strong>❌ Error: "Validate failed: Migration checksum mismatch"</strong></summary>

**Causa:** Modificaste un script SQL que ya fue aplicado.

**Solución:** Nunca modifiques scripts ya aplicados. Crea una nueva migración con los cambios necesarios.

```bash
# Si estás en desarrollo y quieres empezar de cero:
just flyway-reset censos_economicos
```

</details>

<details>
<summary><strong>❌ Error: "Unable to connect to database"</strong></summary>

**Causa:** La base de datos no está corriendo o las credenciales son incorrectas.

**Solución:**

```bash
# Verificar que el contenedor esté corriendo
docker ps | grep postgres-dev

# Probar conexión manual
psql -h localhost -p 5432 -U sieej_user -d censos_economicos

# Revisar flyway.conf
cat migrations/censos_economicos/flyway.conf
```

</details>

<details>
<summary><strong>❌ Error: "Found non-empty schema without schema history table"</strong></summary>

**Causa:** La base de datos tiene tablas pero Flyway nunca se inicializó.

**Solución:**

```bash
# Inicializar el historial de Flyway (solo una vez)
flyway -configFiles=migrations/<pipeline>/flyway.conf baseline
```

</details>

<details>
<summary><strong>❌ Error: "cleanDisabled is set to true"</strong></summary>

**Causa:** Intentaste ejecutar `flyway-clean` con `flyway.cleanDisabled=true`.

**Solución:** Cambia a `flyway.cleanDisabled=false` en tu `flyway.conf` local.

> ⚠️ Nunca hagas esto en producción.

</details>

---

<div align="center">

¿Problemas con Flyway? Revisa los [docs oficiales](https://documentation.red-gate.com/flyway/) o abre un issue 🐛

<sub>Guía de Flyway - ETL SIEEJ - IIEG Jalisco</sub>

</div>
