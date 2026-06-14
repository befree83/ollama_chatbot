# Local Offline Multi-Expert Chatbot MVP

Este proyecto es un chatbot de expertos temáticos desarrollado con **Ollama SDK en Python** que permite interactuar de manera 100% offline con tres perfiles especializados (Programación, Marketing y Jurídico-Legal) utilizando el modelo de lenguaje local `gemma3:1b`.

La arquitectura sigue estándares profesionales y modulares, implementando persistencia del historial en disco, logs automatizados de auditoría, control de temperatura y streaming de tokens en tiempo real con optimización de memoria.

---

## 🏗️ Arquitectura del Sistema

El diseño sigue una estructura limpia y desacoplada, facilitando una futura transición hacia un entorno cliente-servidor (API REST + UI Web):

1. **Capa de Presentación (main.py):** Ciclo de eventos interactivo por consola en castellano. Gestiona el enrutamiento de comandos avanzados (`/change`, `/reset`, `/exit`) y renderiza la respuesta por flujo de tokens en tiempo real (*Streaming*).
2. **Capa del Núcleo de Dominio (core/):**
   * `chatbot.py`: Abstrae la conexión al servicio local de Ollama, valida la disponibilidad del modelo, gestiona fallos con rollback atómico y configura parámetros de muestreo (`temperature=0.3`, `keep_alive="3h"`) para alta velocidad.
   * `conversation.py`: Coordina la pila de mensajes (historial), encapsula la inyección estricta de prompts de sistema en castellano por turno y sincroniza el estado de la sesión.
3. **Capa de Datos y Persistencia (storage/ & logs):** Volcado inmediato del historial estructurado en ficheros JSON aislados por experto, y auditoría técnica centralizada en un fichero de diagnóstico continuo (`app.log`).

---

## 📂 Estructura de Archivos

El proyecto se organiza estrictamente bajo la siguiente estructura de carpetas y ficheros:

```text
├── main.py              # Punto de entrada de la aplicación (Interfaz CLI)
├── requirements.txt     # Especificación de dependencias del entorno
├── app.log              # Registro automático de auditoría y trazas operativas
├── storage/             # Almacenamiento persistente local de sesiones
│   └── chat_history.json
├── experts/
│   ├── __init__.py
│   └── expert_prompts.py # Prompts e instrucciones de sistema de los expertos
└── core/
    ├── __init__.py
    ├── chatbot.py       # Orquestador del SDK de Ollama y lógica transaccional
    └── conversation.py  # Gestor de estados de memoria del contexto