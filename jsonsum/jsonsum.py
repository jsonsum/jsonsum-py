import decimal
import hashlib
import json
from typing import Any, Callable, Optional, Protocol

type_null = b'n'
type_true = b't'
type_false = b'f'
type_number = b'i'
type_string = b's'
type_object = b'o'
type_array_start = b'['
type_array_end = b']'

class Hasher(Protocol):
    def update(self, data: bytes) -> None: ...
    def digest(self) -> bytes: ...

def jsonsum_sha256(j: Any) -> Hasher:
    hash_factory = hashlib.sha256
    sum = hash_factory()
    jsonsum(j, sum, hash_factory)
    return sum

def jsonsum(j: Any, sum: Hasher, hash_factory: Callable[[Optional[bytes]], Hasher]) -> None:
    if j is None:
        sum.update(type_null)
    elif j is True: # must come before isinstance(j, int) because that is also true for bools
        sum.update(type_true)
    elif j is False:
        sum.update(type_false)
    elif isinstance(j, dict):
        sum.update(type_object)
        obj_sum = b'\x00' * sum.digest_size
        seen = set()
        for k, v in j.items():
            if k in seen:
                # can't really happen with dicts
                raise ValueError("duplicate key")
            seen.add(k)
            item_sum = hash_factory()
            jsonsum(k, item_sum, hash_factory)
            jsonsum(v, item_sum, hash_factory)
            obj_sum = xor(obj_sum, item_sum.digest())
        sum.update(obj_sum)
    elif isinstance(j, list):
        sum.update(type_array_start)
        for v in j:
            jsonsum(v, sum, hash_factory)
        sum.update(type_array_end)
    elif isinstance(j, str):
        sum.update(type_string)
        j = hash_factory(j.encode()).digest()
        sum.update(j)
    elif isinstance(j, bytes):
        sum = sum.update(type_string)
        j = hash_factory(j).digest()
        sum.update(j)
    elif isinstance(j, (int, float)):
        sum.update(type_number)
        sum.update(normalize_number(j).encode())
    else:
        raise ValueError("unsupported type")


def xor(a: bytes, b: bytes) -> bytes:
    return bytes(ab ^ bb for ab, bb in zip(a, b))


def normalize_number(n):
    if n == 0:
        return '0e0'
    with decimal.localcontext() as ctx:
        ctx.prec = decimal.MAX_PREC
        d = decimal.Decimal(n).as_tuple()
        digits = ''.join(str(digit) for digit in d.digits) # n is now a string of digits, without decimal point but may have trailing zeros
        stripped_digits = digits.rstrip('0')
        exp = d.exponent + (len(digits) - len(stripped_digits)) # e.g. digits is 100 and exponent is -3, then stripped_digits is 1 and the new exponent is -1
        sign = '-' if d.sign == 1 else ''
        return sign + stripped_digits + 'e' + str(exp)
