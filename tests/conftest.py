
def pytest_itemcollected(item):
    doc = getattr(item.function, "__doc__", None)
    if doc:
        item._nodeid = f"{item.nodeid} - {doc.strip()}"
