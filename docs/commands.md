#To validate the liveliness, home and readiness status of the test manually before CI runs
python -m pytest tests/test_health.py
### To validate the entire test_health.py file:
python -m pytest