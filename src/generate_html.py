import os
import json

def generar_html_desde_iframes(json_file="iframes.json", html_file="iframes_limpios.html"):
    if not os.path.exists(json_file):
        print("⚠️ No se encontró el archivo de iframes.")
        return

    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    with open(html_file, "w", encoding="utf-8") as f:
        f.write("""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Iframes de Videos Subidos</title>
  <style>
    body { font-family: sans-serif; padding: 20px; background-color: #f8f8f8; }
    .video-block { margin-bottom: 40px; background: #fff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); }
    .iframe-container { margin-top: 10px; }
    .copy-button { margin-top: 10px; padding: 6px 12px; background-color: #007BFF; color: white; border: none; border-radius: 4px; cursor: pointer; }
    .copy-button:hover { background-color: #0056b3; }
    textarea { display: none; }
  </style>
</head>
<body>
  <h1>Iframes generados de videos subidos</h1>
""")

        for idx, item in enumerate(data):
            f.write(f"""
  <div class="video-block">
    <h3>{item['title']}</h3>
    <div class="iframe-container">{item['iframe']}</div>
    <button class="copy-button" onclick="copiarIframe('iframe{idx}')">Copiar iframe</button>
    <textarea id="iframe{idx}">{item['iframe']}</textarea>
  </div>
""")

        # JS para copiar
        f.write("""
<script>
function copiarIframe(id) {
  const textarea = document.getElementById(id);
  textarea.style.display = 'block';
  textarea.select();
  document.execCommand('copy');
  textarea.style.display = 'none';
  alert("Iframe copiado al portapapeles");
}
</script>
</body>
</html>
""")

    print(f"✅ Archivo HTML generado: {html_file}")

# Ejecutar directamente si se llama como script
if __name__ == "__main__":
    generar_html_desde_iframes()
