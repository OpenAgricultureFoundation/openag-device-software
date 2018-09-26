# Import standard python libraries
import os, sys, pytest, logging, time

# Set system path
sys.path.append(os.environ["OPENAG_BRAIN_ROOT"])

# Import state machine elements
from device.utilities.statemachine.manager import StateMachineManager
from device.utilities.statemachine.events import RESET_EVENT, SHUTDOWN_EVENT
from device.utilities.statemachine.modes import (
    INIT_MODE,
    NORMAL_MODE,
    RESET_MODE,
    SHUTDOWN_MODE,
    ERROR_MODE,
    INVALID_MODE,
)


def test_init() -> None:
    manager = StateMachineManager()


def test_valid_transition_true() -> None:
    manager = StateMachineManager()
    assert manager.valid_transition(INIT_MODE, NORMAL_MODE) == True


def test_valid_transition_false() -> None:
    manager = StateMachineManager()
    assert manager.valid_transition(INIT_MODE, RESET_MODE) == False


def test_valid_transition_invalid_mode_name() -> None:
    manager = StateMachineManager()
    assert manager.valid_transition("Junk From", "Junk To") == False


def test_new_transition_current_mode() -> None:
    manager = StateMachineManager()
    assert manager.new_transition(INIT_MODE) == False


def test_new_transition_valid_mode() -> None:
    manager = StateMachineManager()
    assert manager.new_transition(NORMAL_MODE) == True


def test_new_transition_invalid_mode() -> None:
    manager = StateMachineManager()
    manager.mode = NORMAL_MODE
    assert manager.new_transition(RESET_MODE) == True
    assert manager.mode == ERROR_MODE


def test_run_init_to_normal_mode() -> None:
    manager = StateMachineManager()
    assert manager.mode == INIT_MODE
    manager.run_init_mode()
    assert manager.mode == NORMAL_MODE


def test_run_normal_to_shutdown_mode() -> None:
    manager = StateMachineManager()
    manager.mode = SHUTDOWN_MODE
    manager.run_normal_mode()
    assert manager.mode == SHUTDOWN_MODE


def test_run_reset_to_init_mode() -> None:
    manager = StateMachineManager()
    manager.mode = NORMAL_MODE
    manager.run_reset_mode()
    assert manager.mode == INIT_MODE


def test_run_error_mode_breaks_on_reset() -> None:
    manager = StateMachineManager()
    manager.mode = RESET_MODE
    manager.run_error_mode()
    assert manager.mode == RESET_MODE


def test_spawn_shutdown() -> None:
    manager = StateMachineManager()

    # Spawn manager and ensure transitions to normal mode
    manager.spawn()
    start_time = time.time()
    while True:
        time.sleep(0.1)
        if manager.mode == NORMAL_MODE:
            break

    # Ensure thread shutsdown
    message, status = manager.shutdown()
    assert status == 200
    start_time = time.time()
    while True:
        time.sleep(0.1)
        if manager.is_shutdown:
            break


def test_spawn_error_shutdown() -> None:
    manager = StateMachineManager()

    # Set manager into reset mode
    manager.mode = ERROR_MODE

    # Spawn manager and ensure transitions to error mode
    manager.spawn()
    start_time = time.time()
    while True:
        time.sleep(0.1)
        if manager.mode == ERROR_MODE:
            break

    # Ensure thread shutsdown
    message, status = manager.shutdown()
    assert status == 200
    start_time = time.time()
    while True:
        time.sleep(0.1)
        if manager.is_shutdown:
            break


def test_spawn_invalid_shutdown() -> None:
    manager = StateMachineManager()

    # Set manager into reset mode
    manager.mode = "Junk"

    # Spawn manager and ensure shutdowns
    manager.spawn()
    start_time = time.time()
    while True:
        time.sleep(0.1)
        if manager.is_shutdown:
            break
    assert manager.mode == INVALID_MODE


def test_create_reset_event() -> None:
    manager = StateMachineManager()

    # Spawn manager and ensure transitions to normal mode
    manager.spawn()
    start_time = time.time()
    while True:
        time.sleep(0.1)
        if manager.mode == NORMAL_MODE:
            break

    # Create reset event
    request = {"type": RESET_EVENT}
    message, status = manager.create_event(request)
    assert status == 200

    # Shutdown manager an ensure thread shutsdown
    message, status = manager.shutdown()
    assert status == 200
    start_time = time.time()
    while True:
        time.sleep(0.1)
        if manager.is_shutdown:
            break


def test_create_shutdown_event() -> None:
    manager = StateMachineManager()

    # Spawn manager and ensure transitions to normal mode
    manager.spawn()
    start_time = time.time()
    while True:
        time.sleep(0.1)
        if manager.mode == NORMAL_MODE:
            break

    # Create shutdown event
    request = {"type": SHUTDOWN_EVENT}
    message, status = manager.create_event(request)
    assert status == 200

    # Ensure thread shutsdown
    start_time = time.time()
    while True:
        time.sleep(0.1)
        if manager.is_shutdown:
            break


def test_create_invalid_event() -> None:
    manager = StateMachineManager()
    request = {"type": "Junk"}
    message, status = manager.create_event(request)
    assert status == 400


def test_check_event_misspelled_type() -> None:
    manager = StateMachineManager()
    request = {"misspelled_type": "Junk"}
    manager.event_queue.put(request)
    manager.check_events()
    # Just checking doesn't break anything (throw exception)


def test_check_event_invalid_type() -> None:
    manager = StateMachineManager()
    request = {"type": "Junk"}
    manager.event_queue.put(request)
    manager.check_events()
    # Just checking doesn't break anything (throw exception)


def test_preprocess_reset_invalid_mode() -> None:
    manager = StateMachineManager()
    assert manager.mode == INIT_MODE
    message, status = manager.reset()
    assert status == 400


def test_process_reset_invalid_mode() -> None:
    manager = StateMachineManager()
    assert manager.mode == INIT_MODE
    manager._reset()
    assert manager.mode != RESET_MODE
