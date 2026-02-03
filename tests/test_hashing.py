# tests/test_hashing.py
from app.hashing import canonicalise, sha256_hex
from datetime import datetime, timezone

def test_sha256_known_vectors():
    # RFC 6234 / NIST vectors
    assert sha256_hex("") == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    assert sha256_hex("abc") == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    assert sha256_hex("abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq") == \
           "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1"

def test_canonicalise_dict_key_order_irrelevant():
    a = {"b": 2, "a": 1}
    b = {"a": 1, "b": 2}
    assert canonicalise(a) == canonicalise(b)

def test_canonicalise_nested_and_types():
    obj = {
        "s": "line1\r\nline2",               # newline normalisation
        "n": 1.23,
        "b": True,
        "none": None,
        "list": [3, {"x": 1, "y": 2}],
        "tuple": (1, 2, 3),
        "set": {"b", "a"},
        "bytes": b"\x00\x01",
        "dt": datetime(2025, 1, 2, 3, 4, 5, tzinfo=timezone.utc),
    }
    can = canonicalise(obj)
    # deterministic, compact JSON: no spaces after commas/colons
    assert ":[" in can and ",{" in can and ',"n":1.23' in can
    # set is sorted and represented deterministically
    assert '"set":["a","b"]' in can
    # bytes encoded with marker
    assert '"__bytes__"' in can

def test_canonicalise_is_stable_for_equivalent_inputs():
    x = {"z": [1, 2, {"a": 3}], "a": {"b": 1, "c": 2}}
    y = {"a": {"c": 2, "b": 1}, "z": [1, 2, {"a": 3}]}
    assert canonicalise(x) == canonicalise(y)
