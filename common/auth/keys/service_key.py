import logging
from base64 import b64encode
from dataclasses import dataclass
from datetime import datetime, timedelta, UTC
from typing import NamedTuple
from uuid import uuid4

from peewee import DoesNotExist

from common.entities import Project, ServiceAccountKey

from .lib import create_digest, extract_digest, extract_key, generate_passphrase, hash_value
from .settings import DEFAULT_EXPIRY_DAYS, HASH_ITERATIONS

LOG = logging.getLogger(__name__)


class ServiceAccountKeyData(NamedTuple):
    valid: bool
    allowed_services: list[str]
    project_id: str


@dataclass
class KeyPair:
    key_entity: ServiceAccountKey
    encoded_key: str


def generate_key(
    *,
    project: Project,
    allowed_services: list[str],
    name: str | None = None,
    description: str | None = None,
    expiration_days: int = DEFAULT_EXPIRY_DAYS,
) -> KeyPair:
    """Generate a new Service Account key for the given service name."""
    passphrase = generate_passphrase()
    salt = str(uuid4())
    passphrase_hash = hash_value(value=passphrase, salt=salt)
    expiry = datetime.now(UTC) + timedelta(days=expiration_days)
    digest = create_digest(iterations=HASH_ITERATIONS, salt=salt, passphrase_hash=passphrase_hash)

    # Give the key a pretty unique name if none provided (Name only has to be unique per-project so this should safe)
    if name is None:
        name = f"Key [{str(uuid4())[:8]}]"

    db_key = ServiceAccountKey.create(
        allowed_services=allowed_services,
        project=project,
        digest=digest,
        expiry=expiry,
        description=description,
        name=name,
    )
    db_key.save()

    key_bytes = str(db_key.id).encode("utf-8") + passphrase.encode("utf-8")

    return KeyPair(db_key, b64encode(key_bytes).decode("utf-8"))


def validate_key(api_key: str) -> ServiceAccountKeyData:
    """
    Validate a service account key.

    NOTE: This function is rather paranoid about exception handling. The work-factor of repeatedly hashing the
    passphrase of a key is part of the security. If the system fails fast for any reason then the work factor could be
    accidentally eliminated.

    Because of this, if there are any errors along the way a work factor is faked using the default iterations value.
    This is also true for the case of keys that generated no errors but happen to be expired. This preserves the work
    factor.
    """
    fake_salt: str = str(uuid4())
    fake_pass: str = str(uuid4())
    try:
        key = extract_key(api_key)
    except Exception:
        LOG.exception("Unable to decode the Service Account key.")
        hash_value(value=fake_pass, salt=fake_salt)  # Fake a work-factor before failing
        return ServiceAccountKeyData(False, [""], "")

    try:
        db_entry = ServiceAccountKey.get(id=key.db_key)
    except DoesNotExist:
        LOG.warning("ServiceAccountKey with primary key `%s` does not exist.", key.db_key)
        hash_value(value=fake_pass, salt=fake_salt)  # Fake a work-factor before failing
        return ServiceAccountKeyData(False, [""], "")
    except Exception:
        LOG.exception("Error looking up ServiceAccountKey")
        hash_value(value=fake_pass, salt=fake_salt)  # Fake a work-factor before failing
        return ServiceAccountKeyData(False, [""], "")

    if db_entry.is_expired():
        LOG.debug("ServiceAccountKey with primary key `%s` is expired", key.db_key)
        hash_value(value=fake_pass, salt=fake_salt)  # Fake a work-factor before failing
        return ServiceAccountKeyData(False, [""], "")

    try:
        digest_parts = extract_digest(db_entry.digest)
    except Exception:
        LOG.exception("Unable to extract digest from ServiceAccountKey database entry.")
        hash_value(value=fake_pass, salt=fake_salt)  # Fake a work-factor before failing
        return ServiceAccountKeyData(False, [""], "")

    try:
        passphrase_hash = hash_value(
            value=key.passphrase, salt=digest_parts.salt, hash_iterations=digest_parts.iterations
        )
    except Exception:
        LOG.exception("Unable to hash the given Service Account key.")
        hash_value(value=fake_pass, salt=fake_salt)  # Fake a work-factor before failing
        return ServiceAccountKeyData(False, [""], "")

    # Compare the hash values
    if digest_parts.passphrase_hash == passphrase_hash:
        return ServiceAccountKeyData(True, db_entry.allowed_services, str(db_entry.project.id))
    else:
        return ServiceAccountKeyData(False, [""], "")
