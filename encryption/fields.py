import logging

from cryptography.fernet import Fernet, MultiFernet, InvalidToken
from django.conf import settings
from django.db.models import TextField
from django.forms import PasswordInput
from django.utils.translation import gettext as _


logger = logging.getLogger("project.encryption")

def get_fernet() -> MultiFernet:
    if settings.ENCRYPTION_KEY:
        primary_fernet = Fernet(settings.ENCRYPTION_KEY)
    else:
        raise ValueError("ENCRYPTION_KEY setting is not set")

    fallback_fernets = []
    if settings.ENCRYPTION_KEY_FALLBACKS:
        fallback_fernets = [Fernet(key) for key in settings.ENCRYPTION_KEY_FALLBACKS]

    return MultiFernet([primary_fernet] + fallback_fernets)

def encrypt(value: str) -> str:
    return get_fernet().encrypt(value.encode("utf-8")).decode("utf-8")

def decrypt(value: str) -> str:
    return get_fernet().decrypt(value.encode("utf-8")).decode("utf-8")

def rotate(value: str) -> str:
    return get_fernet().rotate(value.encode("utf-8")).decode("utf-8")

class EncryptedTextField(TextField):
    description = _("Encrypted text")

    def from_db_value(self, value, expression, connection):
        try:
            return decrypt(value)
        except InvalidToken:
            logger.warning("Invalid encryption token: %s", value)
            return value

    def get_prep_value(self, value):
        return encrypt(value)

    def rotate(self):
        logger.debug("Rotating encryption keys for field %s", self.name)
        print("+++Rotating encryption keys for field %s", self.name)
        self.value = rotate(self.value)
        self.save()

    def formfield(self, **kwargs):
        # Use a PasswordInput widget for the form field
        kwargs["widget"] = PasswordInput(render_value=True)
        return super().formfield(**kwargs)
