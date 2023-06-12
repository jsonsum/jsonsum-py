import decimal
import json
from zlib import crc32

type_null = b'n'
type_true = b't'
type_false = b'f'
type_number = b'i'
type_string = b's'
type_object = b'o'
type_array_start = b'['
type_array_end = b']'

def crc32_to_bytes(s):
    return s.to_bytes(length=4, byteorder='big', signed=False)

def jsonsum_crc32(j, sum=0):
    if j is None:
        return crc32(type_null, sum)
    elif j is True: # must come before isinstance(j, int) because that is also true for bools
        return crc32(type_true, sum)
    elif j is False:
        return crc32(type_false, sum)
    elif isinstance(j, dict):
        sum = crc32(type_object, sum)
        obj_sum = 0
        seen = set()
        for k, v in j.items():
            if k in seen:
                # can't really happen with dicts
                raise ValueError("duplicate key")
            seen.add(k)
            item_sum = jsonsum_crc32(k)
            item_sum = jsonsum_crc32(v, item_sum)
            obj_sum ^= item_sum
        return crc32(crc32_to_bytes(obj_sum), sum)
    elif isinstance(j, list):
        sum = crc32(type_array_start, sum)
        for v in j:
            sum = jsonsum_crc32(v, sum)
        return crc32(type_array_end, sum)
    elif isinstance(j, str):
        sum = crc32(type_string, sum)
        j = crc32_to_bytes(crc32(j.encode()))
        return crc32(j, sum)
    elif isinstance(j, bytes):
        sum = crc32(type_string, sum)
        j = crc32_to_bytes(crc32(j))
        return crc32(j, sum)
    elif isinstance(j, (int, float)):
        sum = crc32(type_number, sum)
        return crc32(normalize_number(j).encode(), sum)
    else:
        raise ValueError("unsupported type")

def normalize_number(n):
    if n == 0:
        return '0e0'
    with decimal.localcontext(prec=decimal.MAX_PREC) as ctx:
        d = decimal.Decimal(n).as_tuple()
        digits = ''.join(str(digit) for digit in d.digits) # n is now a string of digits, without decimal point but may have trailing zeros
        stripped_digits = digits.rstrip('0')
        exp = d.exponent + (len(digits) - len(stripped_digits)) # e.g. digits is 100 and exponent is -3, then stripped_digits is 1 and the new exponent is -1
        sign = '-' if d.sign == 1 else ''
        return sign + stripped_digits + 'e' + str(exp)
