import subprocess
import time
import shutil

def measure_execution_time(script_name: str) -> float:
    shutil.rmtree("output", ignore_errors=True)

    start = time.perf_counter()

    subprocess.run(
        ["python", script_name],
        check=True
    )

    end = time.perf_counter()

    return end - start

browser_time = measure_execution_time("browser.py")
browserEfficient_time = measure_execution_time("browserEfficient.py")

print(f"browser.py:          {browser_time:.2f} seconds")
print(f"browserEfficient.py: {browserEfficient_time:.2f} seconds")

speedup = browser_time / browserEfficient_time

print(f"Speedup: {speedup:.2f}x")
print(f"Time saved: {browser_time - browserEfficient_time:.2f} seconds")
