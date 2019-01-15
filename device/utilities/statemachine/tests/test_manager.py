# Import standard python libraries
import os, sys, pytest, logging, time

# Set system path
sys.path.append(os.environ["PROJECT_ROOT"])

# Import state machine elements
from device.utilities.statemachine.manager import StateMachineManager
from device.utilities.statemachine import modes, events


def test_init() -> None:
    manager = StateMachineManager()


def test_valid_transition_true() -> None:
    manager = StateMachineManager()
    assert manager.valid_transition(modes.INIT, modes.NORMAL) == True


def test_valid_transition_false() -> None:
    manager = StateMachineManager()
    assert manager.valid_transition(modes.INIT, modes.RESET) == False


def test_valid_transition_invalid_mode_name() -> None:
    manager = StateMachineManager()
    assert manager.valid_transition("Junk From", "Junk To") == False


def test_new_transition_current_mode() -> None:
    manager = StateMachineManager()
    assert manager.new_transition(modes.INIT) == False


def test_new_transition_valid_mode() -> None:
    manager = StateMachineManager()
    assert manager.new_transition(modes.NORMAL) == True


def test_new_transition_invalid_mode() -> None:
    manager = StateMachineManager()
    manager._mode = modes.NORMAL
    assert manager.new_transition(modes.RESET) == True
    assert manager._mode == modes.ERROR


def test_run_init_to_normal_mode() -> None:
    manager = StateMachineManager()
    assert manager._mode == modes.INIT
    manager.run_init_mode()
    assert manager._mode == modes.NORMAL


def test_run_normal_to_shutdown_mode() -> None:
    manager = StateMachineManager()
    manager._mode = modes.SHUTDOWN
    manager.run_normal_mode()
    assert manager._mode == modes.SHUTDOWN


def test_run_reset_to_init_mode() -> None:
    manager = StateMachineManager()
    manager._mode = modes.NORMAL
    manager.run_reset_mode()
    assert manager._mode == modes.INIT


def test_run_error_mode_breaks_on_reset() -> None:
    manager = StateMachineManager()
    manager._mode = modes.RESET
    manager.run_error_mode()
    assert manager._mode == modes.RESET


def test_spawn_shutdown() -> None:
    manager = StateMachineManager()

    # Spawn manager and ensure transitions to normal mode
    manager.spawn()
    start_time = time.time()
    while True:
        time.sleep(0.1)
        if manager._mode == modes.NORMAL:
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
    manager._mode = modes.ERROR

    # Spawn manager and ensure transitions to error mode
    manager.spawn()
    start_time = time.time()
    while True:
        time.sleep(0.1)
        if manager._mode == modes.ERROR:
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
    manager._mode = "Junk"

    # Spawn manager and ensure shutdowns
    manager.spawn()
    start_time = time.time()
    while True:
        time.sleep(0.1)
        if manager.is_shutdown:
            break
    assert manager._mode == modes.INVALID


def test_create_reset_event() -> None:
    manager = StateMachineManager()

    # Spawn manager and ensure transitions to normal mode
    manager.spawn()
    start_time = time.time()
    while True:
        time.sleep(0.1)
        if manager._mode == modes.NORMAL:
            break

    # Create reset event
    request = {"type": events.RESET}
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
        if manager._mode == modes.NORMAL:
            break

    # Create shutdown event
    request = {"type": events.SHUTDOWN}
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
    assert manager._mode == modes.INIT
    message, status = manager.reset()
    assert status == 400


def test_process_reset_invalid_mode() -> None:
    manager = StateMachineManager()
    assert manager._mode == modes.INIT
    manager._reset()
    assert manager._mode != modes.RESET
