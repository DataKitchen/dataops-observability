from uuid import uuid4

import pytest

from common.auth.keys import lib


@pytest.fixture(scope="session")
def passphrase():
    yield lib.generate_passphrase()


@pytest.fixture(scope="session")
def salt():
    yield str(uuid4())


@pytest.mark.unit
def test_hash_value(salt, passphrase):
    """Hash values are consistent by iteration."""
    hash_1 = lib.hash_value(value=passphrase, salt=salt, hash_iterations=1)
    hash_2 = lib.hash_value(value=passphrase, salt=salt, hash_iterations=1)
    assert hash_1 == hash_2


@pytest.mark.unit
def test_hash_value_iterations(salt, passphrase):
    """Iteration value changes hash result."""
    hash_1 = lib.hash_value(value=passphrase, salt=salt, hash_iterations=1)
    hash_2 = lib.hash_value(value=passphrase, salt=salt, hash_iterations=2)
    assert hash_1 != hash_2


@pytest.mark.unit
def test_create_and_extract_digest(salt, passphrase):
    """Digest data can be extracted from a digest of bytes."""
    iterations = 100
    passphrase_hash = lib.hash_value(value=passphrase, salt=salt, hash_iterations=2)
    digest = lib.create_digest(passphrase_hash=passphrase_hash, iterations=iterations, salt=salt)
    digest_parts = lib.extract_digest(digest)
    assert digest_parts.iterations == iterations
    assert digest_parts.salt == salt
    assert digest_parts.passphrase_hash == passphrase_hash


@pytest.mark.unit
def test_extract_digest_reserved_bytes(salt):
    """Digest data can be extracted when hash contains reserved bytes."""
    iterations = 100
    passphrase_hash = b"this|has|lots|of|reserved|bytes"
    digest = lib.create_digest(passphrase_hash=passphrase_hash, iterations=iterations, salt=salt)
    digest_parts = lib.extract_digest(digest)
    assert digest_parts.iterations == iterations
    assert digest_parts.salt == salt
    assert digest_parts.passphrase_hash == passphrase_hash


@pytest.mark.unit
def test_key_salt_reserved_chars(passphrase):
    """Error raised when attempting to create a digest with reserved characters in the key salt."""
    bad_salt = "this|salt_has_reserved_characters"
    passphrase_hash = lib.hash_value(value=passphrase, salt=bad_salt, hash_iterations=2)
    with pytest.raises(ValueError):
        lib.create_digest(passphrase_hash=passphrase_hash, iterations=2, salt=bad_salt)


@pytest.mark.unit
def test_extract_digest_invalid():
    """Invalid digest data yields a ValueError."""
    digest = b"|".join((b"5", b"salt"))
    with pytest.raises(ValueError):
        lib.extract_digest(digest)


@pytest.mark.unit
def test_generate_passphrase_collisions():
    """No collisions when generating passphrases."""
    # NOTE: This is not meant to test entropy or to be an exhaustive way to ensure the implementation yields no
    # collisions. Rather it makes sure that the function appears to be working properly and that no caching or other
    # things are added to the function which would render it insecure.
    passphrases = [lib.generate_passphrase() for _ in range(100_000)]
    assert len(passphrases) == len(set(passphrases)), "Unexpected collision detected in 'generate_passphrase'"
