import pytest
from parameterized import parameterized

from forgesteel_warehouse.api_key import ApiKey

def test_form_key():
    uid = 2
    key = 'TEST_KEY_ABC'

    fullKey = ApiKey.makeApiKey(uid, key)

    assert fullKey == '$2$TEST_KEY_ABC'

def test_form_fails_with_delimeter_in_key():
    uid = 1
    key = 'SHOULD$FAIL'
    with pytest.raises(ValueError, match=r".*must not contain \"\$\""):
        ApiKey.makeApiKey(uid, key)

def test_parse_key():
    full = '$5$ABC123-001'
    (uid, key) = ApiKey.parseApiKey(full)

    assert uid == 5
    assert key == 'ABC123-001'

@parameterized.expand([
    ('5ABC123-001'),
    ('$tooFew'),
    ('$too$many$'),
    ('$wrong$type'),
    ('prefix$1$asdf')
])
def test_parse_key_malformed_delimeter(fullKey):
    with pytest.raises(ValueError, match=r"Malformed.*"):
        ApiKey.parseApiKey(fullKey)
