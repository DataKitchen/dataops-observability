import logging
import random
import sys
from base64 import b64decode
from functools import cache
from hashlib import pbkdf2_hmac
from typing import NamedTuple
from unicodedata import category, normalize

from .settings import HASH_ITERATIONS

LOG = logging.getLogger(__name__)
KEY_MARKER = b"|"
"""Bytes reserved to divide key data from other data."""


class AuthenticationKeyParts(NamedTuple):
    db_key: str
    passphrase: str


class DigestParts(NamedTuple):
    iterations: int
    salt: str
    passphrase_hash: bytes


@cache
def unicode_letters() -> str:
    """
    Return all unicode letters (but not all codepoints).

    Useful for getting a set of random text characters that can be used for generating complex passwords. This is
    rather intense to generate so the value is memoized.

    Only letters that are identical to their decomposed compatibility form are included. Some letters have more than
    one form or codepoint. If the letter can be decomposed into two separate codepoints. For example the codepoint
    Character: Ç can be expressed with the codepoint 00C7 i.e. "\u00c7" OR it can be expressed as a series of two
    characters; a normal 'C' (0043) + '̧' (0327) i.e. "\u0043\u0327" and these are not the same when split::

        >>> a ="\u0043\u0327"
        >>> b = "\u00c7"
        >>> a[0]
        'C'
        >>> b[0]
        'Ç'

    To make sure we always get normalized letters that are individual characters and never will mistakenly be composed
    into multiple characters, we start by only including codepoints in certain categories and exclude any that are
    combinging marks or other codepoints with special meaning. Then we attempt a compatibility decomposition (NFKD) on
    each character and compare it to the initial value; if the value is unchanged we know it is safe to presume it will
    always be a singular character.

    This means we can always ensure that the length of all strings generated from the characters returned from this
    function will always be of identical length regardless of their normalization form (length in terms of total
    characters, NOT in terms of bytes).
    """
    unicode_chars = (chr(n) for n in range(sys.maxunicode))
    letters = (c for c in unicode_chars if (category(c) in ("Lu", "Ll", "Ni", "Sc", "Lt", "Lo", "LC")))
    return "".join(x for x in letters if x == normalize("NFKD", x))


def generate_passphrase() -> str:
    return "".join(random.choice(unicode_letters()) for _ in range(36))


def hash_value(*, value: str, salt: str, hash_iterations: int = HASH_ITERATIONS) -> bytes:
    """Return the hash of value & a salt using pbkdf2 & sha256."""
    return pbkdf2_hmac("sha256", value.encode("utf-8"), salt.encode("utf-8"), hash_iterations)


def create_digest(*, iterations: int, salt: str, passphrase_hash: bytes) -> bytes:
    """Generate a digest of the passphrase, salt, and iterations used."""
    if "|" in salt:
        raise ValueError("Reserved character `|` is not allowed in key salts")
    return KEY_MARKER.join((passphrase_hash, str(iterations).encode("utf-8"), salt.encode("utf-8")))


def extract_digest(digest: bytes) -> DigestParts:
    """Extract a digest into it's constituent parts."""
    parts = digest.rsplit(KEY_MARKER, 2)
    if len(parts) != 3:
        raise ValueError(f"Invalid digest. Expected 3 parts, got {len(parts)}")

    # Decompose the parts and decode to appropriate types
    passphrase_hash, iter_bytes, salt_bytes = parts
    iterations: int = int(iter_bytes.decode("utf-8"))
    salt: str = salt_bytes.decode("utf-8")
    return DigestParts(iterations, salt, passphrase_hash)


def extract_key(value: str) -> AuthenticationKeyParts:
    """
    Given an authenticaton key, extract the key id and passphrase.

    An authentication key is always 2 components of identical length. A UUID representing the primary key for the API
    key, and the actual passphrase which is a string of random characters.
    """
    key_bytes: bytes = b64decode(value)
    key_text = key_bytes.decode("utf-8")
    db_key = key_text[0:36]
    passphrase = key_text[36:72]
    return AuthenticationKeyParts(db_key, passphrase)
