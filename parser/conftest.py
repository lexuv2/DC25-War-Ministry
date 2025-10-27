import os
import pytest
import logging

BASE_LOG_DIR = "logs"


@pytest.fixture(autouse=True)
def capture_test_logs(request, capsys):
    test_dir = os.path.basename(os.path.dirname(request.fspath))
    test_file = str(os.path.basename(request.fspath)).replace(".py", ".log")

    log_path = os.path.join(BASE_LOG_DIR, test_dir, test_file)

    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    file_handler = logging.FileHandler(log_path, mode="w")
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    yield

    captured = capsys.readouterr()
    if captured.out:
        file_handler.stream.write("\n=== STDOUT ===\n")
        file_handler.stream.write(captured.out)
    if captured.err:
        file_handler.stream.write("\n=== STDERR ===\n")
        file_handler.stream.write(captured.err)

    file_handler.close()
