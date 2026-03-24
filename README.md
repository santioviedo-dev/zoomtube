# ZOOM-TO-YOUTUBE

Este proyecto automatiza la descarga de grabaciones de Zoom y su posterior subida a YouTube, generando también iframes para incrustar los videos.

## 📝 Requisitos previos

- Python 3.8+
- Cuenta de Zoom con acceso API
- Cuenta de Google con acceso a YouTube API
- Credenciales de API de Zoom y YouTube

## 🛠️ Configuración

1. Clona el repositorio:
```bash
git clone https://github.com/santioviedo-dev/zoomtube
cd zoom-to-youtube
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. Configura las variables de entorno:
   - Crea un archivo `.env` en la carpeta `config/` con este contenido:
```ini
RECORDINGS_BASE_PATH=data/recordings
ZOOM_ACCOUNT_ID=tu_account_id
ZOOM_CLIENT_ID=tu_client_id
ZOOM_CLIENT_SECRET=tu_client_secret
```

4. Configura las credenciales de YouTube:
   - Coloca tu `client_secret.json` en la carpeta `config/`

5. Ejecuta la autenticación inicial:
```bash
python src/upload_youtube.py --mode single --file [RUTA_A_ARCHIVO_DE_PRUEBA]
```
(Sigue las instrucciones para autorizar el acceso a tu cuenta de YouTube)

## 🚀 Uso

### Descargar grabaciones de Zoom:
```bash
python main.py --action download --date YYYY-MM-DD
```

### Subir videos a YouTube:
```bash
# Subir un video específico
python main.py --action upload --file [RUTA_AL_VIDEO]

# Subir todos los videos de una carpeta
python main.py --action upload --folder [RUTA_A_CARPETA]

# Subir videos por fecha (busca en RECORDINGS_BASE_PATH/YYYY-MM-DD)
python main.py --action upload --date YYYY-MM-DD
```

### Descargar y subir automáticamente:
```bash
python main.py --action all --date YYYY-MM-DD
```

## 📂 Estructura del proyecto
```
zoom-to-youtube/
├── config/
│   ├── .env                  # Variables de entorno
│   ├── client_secret.json    # Credenciales YouTube
│   └── token.pickle          # Token de autenticación
├── data/
│   ├── recordings/           # Grabaciones descargadas
│   │   ├── YYYY-MM-DD/       # Organizadas por fecha
│   │   └── ...
│   └── iframes.json          # Iframes generados
├── logs/
│   └── uploaded.log          # Registro de videos subidos
├── output/
│   └── iframes_clean.html    # HTML con iframes
└── src/
    ├── download_zoom.py      # Descarga grabaciones de Zoom
    └── upload_youtube.py     # Sube videos a YouTube
```

## ⚙️ Opciones avanzadas

### Subida manual de videos:
```bash
python src/upload_youtube.py --mode [single|batch] --file [RUTA] --folder [CARPETA] --date [FECHA]
```

### Descarga manual de grabaciones:
```bash
python src/download_zoom.py --date YYYY-MM-DD
```

## 📌 Notas
- Los videos se suben a YouTube como "No listados"
- Se generan iframes en `data/iframes.json` y `output/iframes_clean.html`
- El sistema evita subir videos duplicados mediante `logs/uploaded.log`
- Las grabaciones muy cortas (<15 segundos) se ignoran automáticamente