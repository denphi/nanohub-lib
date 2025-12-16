import os
import pytest

@pytest.fixture(autouse=True, scope="class")
def change_test_dir(request):
    """
    Automatically change the current working directory to the test file's directory
    for tests in the 'tests/rappture' folder.
    """
    if 'tests/rappture' in str(request.fspath):
        os.chdir(os.path.dirname(str(request.fspath)))
        yield
        os.chdir(request.config.invocation_dir)
    else:
        yield
