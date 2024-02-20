import subprocess

import pytest


@pytest.mark.functional
def test_empire_run():
    result = subprocess.run(["python", "scripts/run.py", "--dataset", "test", "--force"], timeout=20)
