# 🎮 Adivina el Personaje de Videojuegos (TikTok & YouTube Shorts)

*Idiomas: [English](README.md) | [Español](README_es.md)*

Sistema automatizado en **Python** para la generación y publicación periódica (cada 4 horas) de videos verticales estilo Shorts / TikTok de **"Adivina el personaje"**. 

El video presenta a un personaje icónico de videojuegos fuertemente difuminado que va perdiendo el desenfoque en distintas fases conforme avanza el tiempo y se muestran pistas, culminando con una revelación nítida, fanfarria y llamada a la acción para maximizar comentarios y retención.

---

## 📁 Carpeta de Salida Obligatoria

Todos los videos generados y sus metadatos asociados se guardan en la raíz del proyecto dentro de la carpeta:
```
Blurred_characters/
├── quiz_20260919_053253_mario.mp4
├── quiz_20260919_053253_mario.json
├── quiz_20260919_053421_kratos.mp4
└── quiz_20260919_053421_kratos.json
```
Cada video `.mp4` viene acompañado de un archivo `.json` con:
- Título sugerido optimizado para SEO
- Descripción con hashtags (`#Shorts`, `#Gaming`, `#AdivinaElPersonaje`, etc.)
- Nombre del personaje y saga
- Estado de publicación en redes sociales

---

## ⏱️ Dinámica del Video (13 Segundos, Formato 9:16)

1. **0.0s – 3.5s (Fase 1 - Difuminado 100%)**:
   - Marco neón cyberpunk con fondo contrastado.
   - Pista 1: *"¿Reconoces los colores del personaje?"*.
   - Música de suspense con ritmo ascendente.
2. **3.5s – 6.5s (Fase 2 - Difuminado 50%)**:
   - Se reduce el desenfoque a la mitad, revelando la silueta básica.
   - Pista 2: Datos clave del personaje (año de lanzamiento, historia o creador).
3. **6.5s – 9.0s (Fase 3 - Cuenta Atrás & Difuminado 20%)**:
   - El difuminado se reduce al 20%, los detalles principales son visibles.
   - Cuenta atrás de tensión en pantalla: `3... 2... 1...` con beeps ascendentes.
   - Barra de tiempo inferior agotándose.
4. **9.0s – 13.0s (Fase 4 - ¡Revelación!)**:
   - Desenfoque al 0% (imagen totalmente nítida y en alta definición).
   - Acorde triunfal de victoria / fanfarria e impacto de bajo.
   - Anuncio destacado: `>> ¡ES [NOMBRE]! <<` y su saga.
   - Llamada a la acción: *"¿Lo adivinaste? ¡Comenta en qué segundo!"*.

---

## 💻 Instalación en Otros Dispositivos

Para llevar este proyecto a cualquier otro ordenador o servidor (Windows, Linux, Mac o VPS):

### En Windows:
Simplemente haz doble clic sobre:
```
setup.bat
```
*(O ejecuta en PowerShell: `powershell -ExecutionPolicy Bypass -File .\setup.ps1`)*

El script se encargará automáticamente de:
1. Detectar e instalar **Python 3.12** si no está presente.
2. Detectar e instalar **FFmpeg** si no está presente.
3. Crear todas las carpetas del proyecto (`Blurred_characters`, `assets`, `data`).
4. Instalar todas las librerías de `requirements.txt`.
5. Crear el archivo `.env` inicial.

Una vez instalado, puedes usar el menú interactivo haciendo doble clic en:
```
run.bat
```

### En Linux / macOS / Servidores VPS:
Ejecuta en tu terminal:
```bash
chmod +x setup.sh
./setup.sh
```

---

### 1. Generar 1 video de prueba de inmediato
```powershell
python main.py --once
```
*Selecciona automáticamente el siguiente personaje de la base de datos que no haya sido utilizado aún.*

### 2. Iniciar el modo automático cada 4 horas
```powershell
python main.py --schedule
```
*Generará un video inmediatamente y después programará uno nuevo cada 4 horas de forma indefinida.*

### 3. Generar un personaje específico
```powershell
python main.py --character sonic --once
```
*Puedes usar cualquier ID: `mario`, `sonic`, `kratos`, `master_chief`, `link`, `pikachu`, `pacman`, `cloud_strife`, `lara_croft`, `solid_snake`, `steve`, `crash_bandicoot`, `samus_aran`, `donkey_kong`, `geralt`, etc.*

### 4. Consultar el estado del catálogo y personajes ya usados
```powershell
python main.py --list-characters
```

---

## ⚙️ Conexión con YouTube Shorts y TikTok

Los videos siempre se generarán y quedarán guardados en `Blurred_characters/`. Cuando desees activar la subida directa:

### YouTube Shorts:
1. Ve a [Google Cloud Console](https://console.cloud.google.com/) y crea un proyecto.
2. Habilita la **YouTube Data API v3**.
3. En *Credenciales*, crea un **ID de cliente de OAuth** (tipo *Aplicación de escritorio*).
4. Descarga el archivo JSON y colócalo en la raíz del proyecto como `client_secret.json`.
5. La primera vez que el bot suba a YouTube, abrirá una ventana de navegador para que inicies sesión en tu canal. Después guardará el token en `youtube_token.json` y no volverá a pedirlo.

### TikTok:
1. Copia `.env.example` a un nuevo archivo `.env`:
   ```powershell
   copy .env.example .env
   ```
2. Introduce tu token de acceso en `TIKTOK_ACCESS_TOKEN`.

---

## 🎨 Agregar Nuevos Personajes

Para añadir más personajes, simplemente abre `data/characters.json` y añade un nuevo bloque:
```json
{
  "id": "shadow",
  "name": "Shadow the Hedgehog",
  "game": "Sonic / SEGA",
  "wiki_page": "Shadow_the_Hedgehog",
  "clues": [
    "Creado por el Dr. Gerald Robotnik como la forma de vida suprema.",
    "El gran rival oscuro de Sonic con botas propulsoras."
  ],
  "tags": ["#Shadow", "#Sonic", "#SEGA", "#Gaming", "#Shorts"]
}
```
El sistema descargará automáticamente la imagen oficial desde Wikipedia si no colocas tu propia imagen PNG en `assets/characters/shadow.png`.
