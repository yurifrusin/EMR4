"""Offline dependency compatibility candidate; execution needs Host A's binding.

No application imports. These library oracles do not establish application login,
tenant isolation, one-use storage, TLS endpoint, or provider compatibility.
"""
import base64
import json
import sys
from datetime import datetime, timedelta, timezone

import pytest
import jwt
from OpenSSL import crypto
from authlib.integrations.base_client.sync_openid import OpenIDMixin
from cryptography import x509
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from joserfc.errors import (
    BadSignatureError,
    ExpiredTokenError,
    InvalidClaimError,
    MissingClaimError,
    UnsupportedAlgorithmError,
)

HMAC_KEY = b"synthetic-hmac-key-for-compatibility-only-" + b"a" * 32
OTHER_HMAC_KEY = b"synthetic-hmac-key-for-compatibility-only-" + b"b" * 32
ISSUER = "https://issuer.invalid/synthetic"
CLIENT_ID = "synthetic-client"
NONCE = "synthetic-nonce-for-offline-compatibility"
KID = "synthetic-rsa-key"
CERT_TIME = datetime(2030, 1, 1, tzinfo=timezone.utc)


@pytest.fixture(scope="module", autouse=True)
def target_runtime():
    # Package/wheel/native-library identities are an external preflight gate.
    assert sys.version_info[:2] == (3, 11)
    assert sys.platform == "linux"


@pytest.fixture(scope="module")
def rsa_keys():
    # Exactly two fresh memory-only keys; never serialized to a file or log.
    return tuple(
        rsa.generate_private_key(public_exponent=65537, key_size=2048)
        for _ in range(2)
    )


def _private_pem(key):
    return key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )


def _tamper_signature(token):
    header, payload, signature = token.split(".")
    decoded = bytearray(
        base64.urlsafe_b64decode(signature + "=" * (-len(signature) % 4))
    )
    decoded[0] ^= 1
    changed = base64.urlsafe_b64encode(decoded).rstrip(b"=").decode("ascii")
    assert changed != signature
    return ".".join((header, payload, changed))


@pytest.mark.parametrize(
    "mutation,error",
    [
        pytest.param("wrong-key", jwt.exceptions.InvalidSignatureError, id="wrong-key"),
        pytest.param("tamper", jwt.exceptions.InvalidSignatureError, id="tamper"),
        pytest.param("expired", jwt.exceptions.ExpiredSignatureError, id="expired"),
        pytest.param("algorithm", jwt.exceptions.InvalidAlgorithmError, id="algorithm"),
    ],
)
def test_hs256_rejection(mutation, error):
    now = int(datetime.now(timezone.utc).timestamp())
    claims = {
        "sub": "00000000-0000-4000-8000-000000000001",
        "practice_id": "00000000-0000-4000-8000-000000000002",
        "exp": now + 3600,
    }
    valid = jwt.encode(claims, HMAC_KEY, algorithm="HS256")
    assert jwt.decode(valid, HMAC_KEY, algorithms=["HS256"]) == claims

    token, verification_key = valid, HMAC_KEY
    if mutation == "wrong-key":
        verification_key = OTHER_HMAC_KEY
    elif mutation == "tamper":
        token = _tamper_signature(valid)
    elif mutation == "expired":
        token = jwt.encode({**claims, "exp": now - 3600}, HMAC_KEY, algorithm="HS256")
    elif mutation == "algorithm":
        token = jwt.encode(claims, HMAC_KEY, algorithm="HS512")
    else:
        raise AssertionError("unknown test mutation")
    with pytest.raises(error):
        jwt.decode(token, verification_key, algorithms=["HS256"])


@pytest.mark.parametrize("mutation", ["wrong-key", "tamper"])
def test_fernet_rejection(mutation):
    cipher = Fernet(base64.urlsafe_b64encode(b"a" * 32))
    payload = json.dumps(
        {"attempt": "synthetic-only", "nonce": NONCE},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    valid = cipher.encrypt(payload)
    assert cipher.decrypt(valid) == payload
    assert json.loads(cipher.decrypt(valid))["nonce"] == NONCE

    token, decoder = valid, cipher
    if mutation == "wrong-key":
        decoder = Fernet(base64.urlsafe_b64encode(b"b" * 32))
    else:
        decoded = bytearray(base64.urlsafe_b64decode(valid))
        decoded[-1] ^= 1
        token = base64.urlsafe_b64encode(decoded)
        assert token != valid
    # The actual store uses decrypt without ttl; expiry/replay are app logic.
    with pytest.raises(InvalidToken):
        decoder.decrypt(token)


class _MemoryOpenID(OpenIDMixin):
    """Use Authlib's actual parse/claim validation, with only local metadata."""

    client_id = CLIENT_ID

    def __init__(self, public_key):
        jwk = jwt.algorithms.RSAAlgorithm.to_jwk(public_key, as_dict=True)
        jwk.update({"kid": KID, "use": "sig", "alg": "RS256"})
        self._jwks = {"keys": [jwk]}

    def load_server_metadata(self):
        return {
            "issuer": ISSUER,
            "id_token_signing_alg_values_supported": ["RS256"],
        }

    def fetch_jwk_set(self, force=False):
        # Even a library refresh remains entirely in memory.
        return self._jwks

    def _get_session(self, *args, **kwargs):
        raise AssertionError("network session is outside this test contract")

    def get(self, *args, **kwargs):
        raise AssertionError("HTTP is outside this test contract")


def _parse_id_token(client, token):
    return client.parse_id_token(
        {"id_token": token},
        nonce=NONCE,
        claims_options={
            "iss": {"essential": True, "values": [ISSUER]},
            "aud": {"essential": True, "values": [CLIENT_ID]},
            "sub": {"essential": True},
            "exp": {"essential": True},
            "nbf": {"essential": True},
            "iat": {"essential": True},
        },
        leeway=60,
    )


@pytest.mark.parametrize(
    "mutation,error,reason,claim",
    [
        pytest.param("wrong-key", BadSignatureError, "bad_signature", None, id="wrong-key"),
        pytest.param("tamper", BadSignatureError, "bad_signature", None, id="tamper"),
        pytest.param("expired", ExpiredTokenError, "expired_token", "exp", id="expired"),
        pytest.param("nonce", InvalidClaimError, "invalid_claim", "nonce", id="nonce"),
        pytest.param("issuer", InvalidClaimError, "invalid_claim", "iss", id="issuer"),
        pytest.param("audience", InvalidClaimError, "invalid_claim", "aud", id="audience"),
        pytest.param(
            "algorithm", UnsupportedAlgorithmError, "unsupported_algorithm", None,
            id="algorithm",
        ),
        pytest.param("missing-nbf", MissingClaimError, "missing_claim", "nbf", id="missing-nbf"),
    ],
)
def test_authlib_rs256_rejection(rsa_keys, mutation, error, reason, claim):
    signer, other_signer = rsa_keys
    client = _MemoryOpenID(signer.public_key())
    now = int(datetime.now(timezone.utc).timestamp())
    claims = {
        "iss": ISSUER,
        "aud": CLIENT_ID,
        "sub": "synthetic-subject",
        "nonce": NONCE,
        "iat": now - 120,
        "nbf": now - 120,
        "exp": now + 3600,
    }
    valid = jwt.encode(
        claims, _private_pem(signer), algorithm="RS256", headers={"kid": KID}
    )
    assert dict(_parse_id_token(client, valid)) == claims

    rejected_claims = dict(claims)
    rejected_signer, algorithm = signer, "RS256"
    if mutation == "wrong-key":
        rejected_signer = other_signer
    elif mutation == "expired":
        rejected_claims["exp"] = now - 3600
    elif mutation == "nonce":
        rejected_claims["nonce"] = "different-synthetic-nonce"
    elif mutation == "issuer":
        rejected_claims["iss"] = "https://other-issuer.invalid/synthetic"
    elif mutation == "audience":
        rejected_claims["aud"] = "different-synthetic-client"
    elif mutation == "algorithm":
        algorithm = "RS512"
    elif mutation == "missing-nbf":
        del rejected_claims["nbf"]
    elif mutation != "tamper":
        raise AssertionError("unknown test mutation")

    token = (
        _tamper_signature(valid)
        if mutation == "tamper"
        else jwt.encode(
            rejected_claims, _private_pem(rejected_signer),
            algorithm=algorithm, headers={"kid": KID},
        )
    )
    with pytest.raises(error) as rejected:
        _parse_id_token(client, token)
    assert rejected.value.error == reason
    if claim is not None:
        assert rejected.value.claim == claim


def test_encrypted_private_key_parsing(rsa_keys):
    key = rsa_keys[0]
    password = b"synthetic-test-password-only"
    encrypted = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.BestAvailableEncryption(password),
    )
    restored = serialization.load_pem_private_key(encrypted, password=password)
    assert restored.public_key().public_numbers() == key.public_key().public_numbers()
    with pytest.raises(ValueError):
        serialization.load_pem_private_key(encrypted, password=b"wrong-synthetic-password")
    with pytest.raises(ValueError):
        serialization.load_pem_private_key(b"not-a-PEM-key", password=None)


def _certificate(subject, issuer, public_key, signer, serial, start, end, is_ca):
    return (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(public_key)
        .serial_number(serial)
        .not_valid_before(start)
        .not_valid_after(end)
        .add_extension(x509.BasicConstraints(ca=is_ca, path_length=0 if is_ca else None), True)
        .add_extension(
            x509.KeyUsage(
                digital_signature=True, content_commitment=False,
                key_encipherment=not is_ca, data_encipherment=False,
                key_agreement=False, key_cert_sign=is_ca, crl_sign=is_ca,
                encipher_only=False, decipher_only=False,
            ),
            True,
        )
        .add_extension(x509.SubjectKeyIdentifier.from_public_key(public_key), False)
        .add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(signer.public_key()), False
        )
        .sign(signer, hashes.SHA256())
    )


@pytest.fixture(scope="module")
def certificates(rsa_keys):
    signer, other_key = rsa_keys
    root_name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Synthetic Root")])
    other_name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Other Synthetic Root")])
    leaf_name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "synthetic.invalid")])
    root = _certificate(
        root_name, root_name, signer.public_key(), signer, 1,
        CERT_TIME - timedelta(days=365), CERT_TIME + timedelta(days=365), True,
    )
    unrelated_root = _certificate(
        other_name, other_name, other_key.public_key(), other_key, 2,
        CERT_TIME - timedelta(days=365), CERT_TIME + timedelta(days=365), True,
    )
    leaf = _certificate(
        leaf_name, root_name, other_key.public_key(), signer, 3,
        CERT_TIME - timedelta(days=1), CERT_TIME + timedelta(days=1), False,
    )
    expired_leaf = _certificate(
        leaf_name, root_name, other_key.public_key(), signer, 4,
        CERT_TIME - timedelta(days=2), CERT_TIME - timedelta(days=1), False,
    )
    return root, unrelated_root, leaf, expired_leaf


def _verify_certificate(root, leaf):
    store = crypto.X509Store()
    store.add_cert(crypto.X509.from_cryptography(root))
    store.set_time(CERT_TIME)
    return crypto.X509StoreContext(
        store, crypto.X509.from_cryptography(leaf)
    ).verify_certificate()


@pytest.mark.parametrize(
    "mutation,code",
    [
        pytest.param("untrusted-issuer", 20, id="untrusted-issuer"),
        pytest.param("expired", 10, id="expired"),
    ],
)
def test_certificate_rejection(certificates, mutation, code):
    root, unrelated_root, leaf, expired_leaf = certificates
    assert _verify_certificate(root, leaf) is None
    rejected_root = unrelated_root if mutation == "untrusted-issuer" else root
    rejected_leaf = expired_leaf if mutation == "expired" else leaf
    with pytest.raises(crypto.X509StoreContextError) as rejected:
        _verify_certificate(rejected_root, rejected_leaf)
    # Stable X509_V_ERR values: unable-to-get-local-issuer / certificate-expired.
    # An unrelated parse, signature, key-size, or not-yet-valid error must fail.
    assert rejected.value.errors[:2] == [code, 0]
    assert rejected.value.certificate.to_cryptography().serial_number == rejected_leaf.serial_number


def test_certificate_pem_parsing(certificates):
    leaf = certificates[2]
    pem = leaf.public_bytes(serialization.Encoding.PEM)
    restored = x509.load_pem_x509_certificate(pem)
    assert restored.fingerprint(hashes.SHA256()) == leaf.fingerprint(hashes.SHA256())
    with pytest.raises(ValueError):
        x509.load_pem_x509_certificate(b"not-a-PEM-certificate")
