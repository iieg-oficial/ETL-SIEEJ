---
name: python
description: Convenciones globales de estilo y estructura para código Python.
applyTo: "**/*.py"
---

# Python — Instrucciones globales

## Reglas generales

- Priorizar código simple, claro, mantenible y modular.
- Evitar sobreingeniería.
- Mantener consistencia en nombres, estructura y estilo en todo el proyecto.
- Antes de agregar archivos o módulos nuevos, respetar la estructura ya definida del repositorio.
- Toda lectura y escritura de archivos debe manejarse en UTF-8.
- No usar `print()` para depuración o seguimiento; usar `logging`.
- Separar responsabilidades: no mezclar acceso a datos, validación, lógica de negocio y presentación en un mismo archivo.

## Lenguaje y entorno

- Versión objetivo: Python 3.12+.
- Antes de ejecutar o probar código, verificar que se usa el entorno virtual correcto del proyecto.

## Imports

- Mantener imports solamente en la parte superior del archivo.
- No usar imports dentro de funciones, salvo que exista una razón técnica clara (ej: dependencia opcional o circular).
- Ordenar imports: stdlib → terceros → locales, separados por línea en blanco.

## Convenciones de nombres

- `snake_case` para variables, funciones, módulos y archivos.
- `PascalCase` para clases.
- `UPPER_CASE` para constantes.
- Nombres descriptivos; evitar abreviaciones crípticas.

## Funciones

- Toda función debe incluir type hints en parámetros y retorno.
- Toda función debe tener docstring clara y breve con:
  - descripción
  - args
  - returns
- Preferir funciones atómicas, reutilizables y con una sola responsabilidad.
- Evitar funciones demasiado largas (guideline: si supera ~40 líneas, considerar dividir).
- Evitar código duplicado; extraer lógica repetida a funciones reutilizables.

## Comentarios y logging

- Comentar únicamente bloques concretos cuando aporte claridad real.
- Los comentarios deben ser simples, cortos y usando `#`.
- No usar `print()` para seguimiento; usar `logging` con niveles apropiados (debug, info, warning, error).
- Mantener los mensajes de log sencillos, directos y consistentes.

## Manejo de errores

- Manejar errores de forma explícita y clara.
- Capturar excepciones específicas, no usar `except Exception` genérico salvo en capas superiores.
- Incluir contexto útil en los mensajes de error.

## Estilo de implementación

- Escribir primero código legible antes que código "inteligente".
- Preferir claridad sobre abreviaciones.
- Mantener cada archivo enfocado en una responsabilidad concreta.
- Si una solución se puede resolver de forma simple o compleja, elegir la simple.
- Al generar código nuevo, seguir el patrón existente del proyecto antes de proponer estructuras distintas.

## Qué evitar

- No usar `print()` para logging o depuración.
- No usar imports dentro de funciones sin razón técnica clara.
- No mezclar múltiples responsabilidades en un mismo archivo.
- No generar código innecesariamente abstracto.
- No agregar dependencias nuevas sin justificación clara.
- No ignorar errores silenciosamente (`except: pass`).
