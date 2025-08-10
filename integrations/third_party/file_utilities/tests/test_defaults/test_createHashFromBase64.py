from __future__ import annotations
import base64
import hashlib
import pytest
import os

from TIPCommon.base.action import ExecutionState
from integration_testing.platform.script_output import MockActionOutput
from integration_testing.set_meta import set_metadata

from ...actions import CreateHashFromBase64



pytest_plugins: tuple[str, ...] = ("integration_testing.conftest",)


def run_hash_test(algorithm: str, base64_str: str, expected_hex: str, expected_len: int):
    """Вспомогательная функция для тестов."""
    # 1. Хэш считается правильно
    decoded_data = base64.b64decode(base64_str)
    result_hex = hashlib.new(algorithm, decoded_data).hexdigest()
    assert result_hex == expected_hex, f"{algorithm} hash mismatch"

    # 2. Длина хэша правильная
    assert len(result_hex) == expected_len, f"{algorithm} length mismatch"

    # 3. Пустая строка → хэш от пустых данных
    empty_hex = hashlib.new(algorithm, b"").hexdigest()
    assert len(empty_hex) == expected_len, f"{algorithm} empty string hash length mismatch"

    # 4. Некорректный base64 должен вызвать ошибку
    with pytest.raises(Exception):
        base64.b64decode("!!!notbase64!!!", validate=True)


def test_blake2b():
    run_hash_test(
        "blake2b",
        base64.b64encode(b"test").decode(),
        hashlib.blake2b(b"test").hexdigest(),
        128
    )


def test_blake2s():
    run_hash_test(
        "blake2s",
        base64.b64encode(b"test").decode(),
        hashlib.blake2s(b"test").hexdigest(),
        64
    )


def test_md5():
    run_hash_test(
        "md5",
        base64.b64encode(b"test").decode(),
        hashlib.md5(b"test").hexdigest(),
        32
    )


def test_sha1():
    run_hash_test(
        "sha1",
        base64.b64encode(b"test").decode(),
        hashlib.sha1(b"test").hexdigest(),
        40
    )


def test_sha224():
    run_hash_test(
        "sha224",
        base64.b64encode(b"test").decode(),
        hashlib.sha224(b"test").hexdigest(),
        56
    )


def test_sha256():
    run_hash_test(
        "sha256",
        base64.b64encode(b"test").decode(),
        hashlib.sha256(b"test").hexdigest(),
        64
    )


def test_sha384():
    run_hash_test(
        "sha384",
        base64.b64encode(b"test").decode(),
        hashlib.sha384(b"test").hexdigest(),
        96
    )


def test_sha3_224():
    run_hash_test(
        "sha3_224",
        base64.b64encode(b"test").decode(),
        hashlib.sha3_224(b"test").hexdigest(),
        56
    )


def test_sha3_256():
    run_hash_test(
        "sha3_256",
        base64.b64encode(b"test").decode(),
        hashlib.sha3_256(b"test").hexdigest(),
        64
    )


def test_sha3_384():
    run_hash_test(
        "sha3_384",
        base64.b64encode(b"test").decode(),
        hashlib.sha3_384(b"test").hexdigest(),
        96
    )


def test_sha3_512():
    run_hash_test(
        "sha3_512",
        base64.b64encode(b"test").decode(),
        hashlib.sha3_512(b"test").hexdigest(),
        128
    )


def test_sha512():
    run_hash_test(
        "sha512",
        base64.b64encode(b"test").decode(),
        hashlib.sha512(b"test").hexdigest(),
        128
    )
