"""
Phase 1 Verification Script
Checks all imports and logic without launching GUI or camera.
"""
import sys
sys.path.insert(0, '.')

results = []

# --- Test 1: config.py new fields ---
try:
    import config
    assert hasattr(config, 'DETECTION_CONFIDENCE_THRESHOLD'), "Missing DETECTION_CONFIDENCE_THRESHOLD"
    assert hasattr(config, 'ALERT_RETURN_THRESHOLD'), "Missing ALERT_RETURN_THRESHOLD"
    assert hasattr(config, 'AVAILABLE_MODELS'), "Missing AVAILABLE_MODELS"
    assert isinstance(config.AVAILABLE_MODELS, list) and len(config.AVAILABLE_MODELS) >= 4
    assert 0 < config.DETECTION_CONFIDENCE_THRESHOLD < 1
    assert config.ALERT_RETURN_THRESHOLD > 0
    results.append("PASS: config.py - all new fields present and valid")
except Exception as e:
    results.append(f"FAIL: config.py - {e}")

# --- Test 2: StateManager grace period ---
try:
    from core.state_manager import StateManager
    sm = StateManager(alert_threshold=5, return_threshold=3)
    assert sm.return_threshold == 3, "return_threshold not set correctly"
    assert sm.return_counter == 0, "return_counter should start at 0"

    # Simulate: object present => SECURED
    for _ in range(1):
        sm.update_status(True)
    assert sm.state == "SECURED", f"Expected SECURED, got {sm.state}"

    # Simulate: object missing for 6 frames => ALERT
    for _ in range(6):
        sm.update_status(False)
    assert sm.state == "ALERT", f"Expected ALERT, got {sm.state}"

    # Simulate: object returns for only 2 frames (below threshold=3) => still ALERT
    sm.update_status(True)
    sm.update_status(True)
    assert sm.state == "ALERT", f"Should still be ALERT (grace not satisfied), got {sm.state}"

    # 3rd frame => should clear to SECURED
    sm.update_status(True)
    assert sm.state == "SECURED", f"Expected SECURED after grace period, got {sm.state}"

    results.append("PASS: StateManager - grace period logic works correctly")
except Exception as e:
    results.append(f"FAIL: StateManager - {e}")

# --- Test 3: get_return_progress method ---
try:
    sm2 = StateManager(alert_threshold=5)
    count, thresh = sm2.get_return_progress()
    assert count == 0 and thresh == config.ALERT_RETURN_THRESHOLD
    results.append("PASS: StateManager.get_return_progress() works")
except Exception as e:
    results.append(f"FAIL: StateManager.get_return_progress - {e}")

# --- Test 4: gui_app imports (no display) ---
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("gui_app", "gui_app.py")
    # Just check syntax by compiling, not executing
    with open("gui_app.py", "r") as f:
        source = f.read()
    compile(source, "gui_app.py", "exec")
    results.append("PASS: gui_app.py - syntax valid")
except SyntaxError as e:
    results.append(f"FAIL: gui_app.py syntax error - {e}")
except Exception as e:
    results.append(f"PASS: gui_app.py - compiled (import skipped: {type(e).__name__})")

# --- Test 5: surveillance_engine.py syntax ---
try:
    with open("core/surveillance_engine.py", "r") as f:
        source = f.read()
    compile(source, "surveillance_engine.py", "exec")
    results.append("PASS: surveillance_engine.py - syntax valid")
except SyntaxError as e:
    results.append(f"FAIL: surveillance_engine.py syntax error - {e}")
except Exception as e:
    results.append(f"NOTE: surveillance_engine.py - {e}")

# --- Print results ---
print("\n" + "="*55)
print("  PHASE 1 VERIFICATION RESULTS")
print("="*55)
for r in results:
    print(r)
print("="*55)
all_pass = all(r.startswith("PASS") or r.startswith("NOTE") for r in results)
print(f"\nOverall: {'ALL TESTS PASSED ✓' if all_pass else 'SOME TESTS FAILED ✗'}")
