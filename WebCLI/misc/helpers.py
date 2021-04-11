from WebCLI.models import Algorithm_version, Molecule
from django.db.models.expressions import RawSQL

def to_positive_int_or_none(value):
    if not value:
        return None
    try:
        int_value = int(value)
        return int_value if int_value > 0 else None
    except ValueError:
        return None
