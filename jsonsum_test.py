#!/usr/bin/env python3

import json
from jsonsum import jsonsum_sha256
import pytest

with open('testdata.json', 'r') as f:
    testdata = [[t['name'], t['inputs'], t['sha256']] for t in json.load(f)]

@pytest.mark.parametrize(['name', 'inputs', 'sha256'], testdata)  
def test_testdata(name, inputs, sha256):  
    for j in inputs:
        j = json.loads(j)
        assert jsonsum_sha256(j).hexdigest() == sha256
