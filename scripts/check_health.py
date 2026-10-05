import sys
from urllib.request import urlopen


def check(url):
    try:
        with urlopen(url, timeout=5) as response:
            return response.status == 200
    except Exception as error:
        print(f"  reason: {error}")
        return False



base_url = "http://localhost:5000"
all_ok = True

for endpoint in ("/health", "/ready"):
    ok = check(f"{base_url}{endpoint}")
    print(f"{endpoint}: {'OK' if ok else 'FAIL'}")
    all_ok = all_ok and ok

sys.exit(0 if all_ok else 1)