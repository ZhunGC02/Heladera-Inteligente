# 🧊 Heladera Inteligente - App de Escritorio con IA

![Version](https://img.shields.io/badge/version-1.1.1--beta-blue)
![Python](https://img.shields.io/badge/Python-3.x-green)
![Framework](https://img.shields.io/badge/GUI-Flet-purple)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

Aplicación de escritorio para la gestión de inventario del hogar con integración a la API de **Google Gemini AI**. El sistema analiza los alimentos disponibles, sus categorías y cantidades para generar recetas personalizadas paso a paso.

---

## 🚀 Características Principales

* **Gestión de Stock:** Alta, baja y modificación de productos guardados localmente en SQLite.
* **Organización por Categorías:** Clasificación visual estructurada (Proteínas, Carbohidratos, Lácteos, etc.).
* **Generación de Recetas con IA:** Consultas dinámicas utilizando el modelo `gemini-2.5-flash`.
* **Diseño Portable & Seguro:** Configuración dinámica de la API Key mediante ventana emergente o variable de entorno, evitando la exposición de credenciales.
* **Arquitectura Modular:** Separación clara de responsabilidades (`gui`, `database`, `ia_service`).

---

## 🛠️ Tecnologías Utilizadas

| Componente | Tecnología |
| :--- | :--- |
| **Lenguaje** | Python 3.x |
| **Interfaz Gráfica (GUI)** | Flet (Flutter para Python) |
| **Base de Datos** | SQLite3 |
| **Integración IA** | Google GenAI SDK (`gemini-2.5-flash`) |
| **Empaquetado** | PyInstaller |

---

## 🔐 Requisitos de Seguridad

Por motivos de ciberseguridad y buenas prácticas, **las credenciales de API no están incluidas en el código fuente**. 

Para utilizar la app tenés dos opciones:
1. **Directamente en la App:** Al iniciar la aplicación, si no se detecta una clave activa, se abrirá un cuadro emergente donde podrás ingresar tu API Key de Google AI Studio.
2. **Variable de Entorno:** Podés definir previamente la variable `GEMINI_API_KEY`:
   ```bash
   # Windows (PowerShell)
   $env:GEMINI_API_KEY="tu_api_key_aqui"

   # Linux / macOS
   export GEMINI_API_KEY="tu_api_key_aqui"