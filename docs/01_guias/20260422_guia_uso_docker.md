# Guía de Uso con Docker | AI Evaluadora M2 AI2
## 2026-04-22 - Comandos de Gestión y Actualización

Esta guía proporciona los comandos esenciales para administrar el ciclo de vida de la aplicación utilizando Docker Desktop o Docker Engine.

---

## 1. Instalación e Inicio Inicial
La primera vez que uses el proyecto, o si has borrado las imágenes, usa este comando para descargar dependencias y construir el contenedor:

```powershell
docker compose up --build
```
> [!TIP]
> Si deseas liberar la terminal y que la app corra en segundo plano, añade el flag `-d`:
> `docker compose up --build -d`

---

## 2. Uso Diario
Una vez construido, no es necesario reconstruir cada vez. Puedes simplemente iniciar y detener el servicio:

### Iniciar la aplicación
```powershell
docker compose start
```

### Detener la aplicación (Mantiene el contenedor)
```powershell
docker compose stop
```

---

## 3. Actualizar la Aplicación (Nuevos cambios)
Dependiendo de qué hayas cambiado, tienes dos opciones:

### Opción A: Solo cambios en el código (.py, .md)
Si solo editaste un script o texto y **no agregaste nuevas librerías**, puedes reiniciar rápidamente:
```powershell
docker compose restart
```
*Nota: Gracias al volumen configurado en el proyecto (`- .:/app`), los cambios de código se reflejan al reiniciar el servicio sin necesidad de reconstruir todo.*

### Opción B: Cambios en librerías o configuración (rebuild)
Si editaste el `requirements.txt`, el `Dockerfile` o quieres una limpieza total:
1. **Limpiar el entorno actual**:
   ```powershell
   docker compose down
   ```
2. **Reconstruir e iniciar de nuevo**:
   ```powershell
   docker compose up --build -d
   ```

---

## 4. Monitoreo y Solución de Problemas
Si la aplicación se cierra inesperadamente o quieres ver qué está pasando "bajo el capó":

### Ver logs en tiempo real
```powershell
docker compose logs -f
```

### Ejecutar un comando dentro del contenedor (Para diagnósticos)
```powershell
docker exec -it 20260318_m02s1ai2_app_evaluador-evaluador_app-1 bash
```

---

## 5. Puntos de Acceso
*   **URL de la Aplicación**: [http://localhost:8501](http://localhost:8501)
*   **API / Backend**: Gestionado internamente en el contenedor.


## 6. Repositio en Github

# 1. Inicializa el repositorio si no lo has hecho
git init

# 2. Agrega todos los archivos del proyecto
git add .

# 3. Primer commit
git commit -m "feat: implementacion inicial con motor de deteccion de color inclusivo y heuristica de verbos"

# 4. Configura la rama principal y el remoto
git branch -M main
git remote add origin git@github.com:jorgetzec/M2_S2_Act2_PL_Evaluator.git

# 5. Sube los cambios
git push -u origin main

---
**Asesoría Técnica | 2026-04-22**
