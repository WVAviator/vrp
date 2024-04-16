from utilities.hash_table import HashTable

def test_basic_usage():
    hash_table = HashTable()
    hash_table.insert(1, 'bar')
    hash_table.insert('foo', 'bar')
    assert hash_table.get(1) == 'bar'
    assert hash_table.get('foo') == 'bar'

def test_collisions():
    hash_table = HashTable()
    hash_table.insert(0, 'foo')
    hash_table.insert(40, 'bar')
    assert hash_table.get(0) == 'foo'
    assert hash_table.get(40) == 'bar'

