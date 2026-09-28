# miaseguradora.com.ar: versión con noticias automáticas

Cada día a las 8:00 (Argentina) GitHub busca titulares nuevos en los medios del sector,
actualiza `site/news.json` y Cloudflare Pages republica el sitio solo.
Solo se guardan título, enlace, fuente y fecha (nunca el texto de las notas).

## Puesta en marcha (una sola vez)
1. Creá una cuenta gratis en github.com y un repositorio nuevo (ej. `miaseguradora`).
2. Subí TODO el contenido de esta carpeta, incluida la carpeta oculta `.github`.
   Recomendado: instalar **GitHub Desktop**, agregar esta carpeta como repositorio y hacer "Publish".
   (Arrastrar archivos desde el navegador admite máximo 100 por vez y no siempre toma carpetas ocultas.)
3. En Cloudflare: *Workers & Pages → Create → Pages → Connect to Git* → elegí el repositorio.
   - Build command: (vacío)
   - Build output directory: `site`
4. Conectá el dominio en *Custom domains*, como ya hiciste.
5. Probá las noticias: en GitHub, pestaña *Actions → Actualizar noticias → Run workflow*.
   Abrí la ejecución y mirá el log: cada medio dice OK o FAIL.

## Mantenimiento
- Si un medio dice FAIL, su feed cambió: corregí la lista `FEEDS` en `scripts/update_news.py` o borralo.
- En el log aparece "REVISAR ESTADO SSN" cuando un titular menciona inhibiciones, prohibiciones, multas, etc.
  Las noticias NO cambian el "Estado SSN" de las fichas: eso se actualiza a mano.
- Cada trimestre, cuando la SSN publique nuevos balances, pedí el ZIP actualizado de las fichas.
- No hay Todo Riesgo en la lista porque su sitio no permite lectura automática.
