#!/usr/bin/env python3

import json
from jsonsum import jsonsum_crc32
import pytest

with open('testdata.json', 'r') as f:
    testdata = json.load(f)

@pytest.mark.parametrize(['name', 'jsons', 'expected'], testdata)  
def test_testdata(name, jsons, expected):  
    for j in jsons:
        j = json.loads(j)
        assert jsonsum_crc32(j) == expected
