# FleetSec — Entregable 01

API mínima para telemetría de flotas, con autenticación JWT y pipeline DevSecOps en GitHub Actions.

## Ejecución local en Windows PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Abrir: http://127.0.0.1:8000/docs

Credenciales de laboratorio: `demo` / `DemoPass123!`.

## Tests

```powershell
pytest -q
```

## Seguridad

- Consultas SQL parametrizadas.
- JWT firmado con algoritmo HS256 y expiración.
- Endpoint `/vehicles` protegido.
- SAST con dos reglas propias de Semgrep.
- SCA, SBOM CycloneDX, Gitleaks y Trivy en GitHub Actions.
- La imagen Docker debe usar un digest real en lugar del marcador `REPLACE_WITH_DIGEST` antes de construirla.

## Evidencia pendiente

- Reemplazar el digest de la imagen base por un digest verificado.
- Agregar staging y DAST autenticado con OWASP ZAP.
- Agregar Terraform del Entregable 03.
- Configurar CODEOWNERS y el procedimiento break-glass.
- Documentar resultados de cada ejecución.
