# Import standard python libraries
import sys

# Import health module...
try:
    # ... if running tests from project root
    sys.path.append(".")
    from device.utilities.health import Health
except:
    # ... if running tests from same dir as health.py
    sys.path.append("../../")
    from device.utilities.health import Health


def test_update():
    health = Health(updates=4, minimum=50.0)

    # No reports
    assert health.percent == 100.0
    assert health.healthy == True

    # One report
    health.report_success()
    assert health.percent == 100.0
    assert health.healthy == True

    # Two reports
    health.report_failure()
    assert health.percent == 50.0
    assert health.healthy == True

    # Len(queue) == updates
    health.report_success()
    health.report_success()
    assert health.percent == 75.0
    assert health.healthy == True

    # Len(queue) > updates w/healthy
    health.report_failure()
    assert health.percent == 50.0
    assert health.healthy == True

    # Len(queue) > updates w/unhealthy
    health.report_failure()
    health.report_failure()
    assert health.percent == 25.0
    assert health.healthy == False

    # Reset case
    health.reset()
    assert health.percent == 100.0
    assert health.healthy == True

    # Test str
    assert str(health) == "Health(healthy=True, percent=100.0, minimum=50.0, updates=4)"
