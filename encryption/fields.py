import logging

from cryptography.fernet import Fernet, MultiFernet, InvalidToken
from django.conf import settings
from django.db.models import CharField, TextField
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
    logger.debug("Encrypting value: %s", value)
    return get_fernet().encrypt(value.encode("utf-8")).decode("utf-8")

def decrypt(value: str) -> str:
    logger.debug("Decrypting value: %s", value)
    return get_fernet().decrypt(value.encode("utf-8")).decode("utf-8")


class EncryptionMixin(object):
    def from_db_value(self, value, expression, connection):
        try:
            return decrypt(value)
        except InvalidToken:
            logger.error("Invalid encryption token: %s", value)
            return value

    def get_prep_value(self, value):
        return encrypt(value)


class EncryptedCharField(EncryptionMixin, CharField):
    pass


class EncryptedTextField(EncryptionMixin, TextField):
    pass
