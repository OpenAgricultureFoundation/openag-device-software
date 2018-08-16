import threading

namespace_lock = threading.Lock()
namespace = {}
counters = {}


def aquire_lock(value):
    with namespace_lock:
        if value in namespace:
            counters[value] += 1
        else:
            namespace[value] = threading.Lock()
            counters[value] = 1

    namespace[value].acquire()


def release_lock(value):
    with namespace_lock:
        if counters[value] == 1:
            del counters[value]
            lock = namespace.pop(value)
        else:
            counters[value] -= 1
            lock = namespace[value]

    lock.release()


# # sample usage
# def foo(bar):
#     aquire_lock(bar)
#     # Code block ALPHA (two threads with equivalent bar should not be in here)
#     release_lock(bar)
