import sys
from urllib.parse import urlparse
from urllib.request import urlopen


def check(url):
    try:
        # Safe: base_url is checked to be http(s) below. Ruff cannot see that check.
        with urlopen(url, timeout=5) as response:  # noqa: S310
            return response.status == 200
    # OSError covers what urlopen raises: URLError (connection refused, DNS),
    # HTTPError (e.g. 503) and TimeoutError. Bugs in our own code still crash loudly.
    except OSError as error:
        print(f"  reason: {error}")
        return False


# Usage: python scripts/check_health.py [base_url]
# Default is the local Flask dev server; pass http://localhost:8000 for the container.
base_url = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://localhost:5000"

# Only allow web URLs. Without this, "file:///etc/passwd" would read a local file.
if urlparse(base_url).scheme not in ("http", "https"):
    print(f"Invalid URL {base_url!r}: must start with http:// or https://")
    sys.exit(1)

all_ok = True

for endpoint in ("/health", "/ready"):
    ok = check(f"{base_url}{endpoint}")
    print(f"{endpoint}: {'OK' if ok else 'FAIL'}")
    all_ok = all_ok and ok

sys.exit(0 if all_ok else 1)
