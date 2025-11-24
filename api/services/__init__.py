"""
Package initializer for `api.services`.

This module exposes selected helpers from the legacy top-level `api.services` module
(`api/services.py`) so existing imports like `from .services import generate_equipment_report`
continue to work while the codebase also contains the `api/services/` package with
individual service modules (e.g. `html_pdf_generator.py`).

By re-exporting the legacy function we avoid import collisions between the
`api/services.py` module and the `api/services/` package.
"""

from importlib import import_module
from typing import Any

# Try to import the legacy `api.services_main` module and re-export
# the commonly used symbols. If it is not present ignore silently.
legacy_services = None
try:
	legacy_services = import_module('api.services_main')
except Exception:
	legacy_services = None

def _reexport(name: str) -> Any:
	if legacy_services and hasattr(legacy_services, name):
		return getattr(legacy_services, name)
	return None

# Re-export legacy top-level helpers if available
generate_equipment_report = _reexport('generate_equipment_report')

# Import and expose internal package modules commonly used by other parts
# of the app for convenience
try:
	from .html_pdf_generator import HTMLPDFGenerator  # type: ignore
except Exception:
	HTMLPDFGenerator = None  # type: ignore

try:
	from .maintenance_serializer import serialize_maintenance  # type: ignore
except Exception:
	serialize_maintenance = None  # type: ignore
