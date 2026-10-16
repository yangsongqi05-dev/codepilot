from calc import add,divide,average
def test_add():
    assert add(1,2)==3
def test_divide():
    assert divide(10,2)==5
def test_average():
    assert average([1,2,3])==2