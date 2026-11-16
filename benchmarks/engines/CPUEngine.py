import multiprocessing
import os
from multiprocessing.connection import Connection
from multiprocessing.process import BaseProcess
from typing import Callable

from ..perf.cgroupServices import createCgroup, moveToCgroup, prepareParentCgroup, removeCgroup

# Hardware threads as Linux numbers them (0-15 here): two per performance core, e.g. 10+11
ThreadGroupType = set[int]

CALLING_THREAD = 0  # os.sched_*affinity applies to the thread making the call
# fork copies this process, so the case run (a lambda) needs no pickling
FORK_START_METHOD = "fork"

# each thread group runs in its own cgroup, so the telemetry measures it alone
THREAD_GROUP_CGROUP_PREFIX = "pyseiskit-benchmark-"

def __validateThreadGroups(threadGroups: list[ThreadGroupType]) -> None:
    # Groups may overlap on purpose, e.g. to measure contention; nothing checks for that.
    if not threadGroups:
        raise ValueError("no thread groups given")
    allowedThreads = os.sched_getaffinity(CALLING_THREAD)
    for threadGroup in threadGroups:
        if not threadGroup:
            raise ValueError("empty thread group")
        if not threadGroup <= allowedThreads:
            raise ValueError(f"threads {sorted(threadGroup)} are not all available: {sorted(allowedThreads)}")


def __countRunsPerThreadGroup(repetitions: int, threadGroupCount: int) -> list[int]:
    # how many runs each group does, handed out one at a time: 7 over 3 groups -> [3, 2, 2]
    runsPerThreadGroup: list[int] = []
    for _ in range(threadGroupCount):
        runsPerThreadGroup.append(0)
    for repetition in range(repetitions):
        runsPerThreadGroup[repetition % threadGroupCount] += 1
    return runsPerThreadGroup


def __runThreadGroup(
    runCase: Callable[[], object],
    threadGroup: ThreadGroupType,
    threadGroupCgroup: str,
    threadGroupRepetitions: int,
    errorSender: Connection
) -> None:
    # Runs in a forked process, which starts with only this thread: pinning it pins the whole
    # process, and threads that libraries start later, and SU programs, inherit the group.
    # What runCase returns is dropped at once: measurements go to its telemetry, and
    # keeping results would grow the memory of later runs.
    os.sched_setaffinity(CALLING_THREAD, threadGroup)
    try:
        moveToCgroup(os.getpid(), threadGroupCgroup)  # SU programs started later join it too
        for _ in range(threadGroupRepetitions):
            runCase()
        errorSender.send(None)
    except Exception as error:
        errorSender.send(error)
    errorSender.close()


def runCaseOnThreadGroups(
    threadGroups: list[ThreadGroupType],
    repetitions: int,
    runCase: Callable[[], object]
) -> None:
    # Call runCase `repetitions` times, spread over thread groups: one process per group,
    # pinned to it. Groups of one thread give single-thread runs, one big group gives runs
    # that use all of it, and several groups run in parallel. Runs finish in any order.
    # If runs fail in several groups, the first group's error is raised.
    __validateThreadGroups(threadGroups)
    if repetitions < 1:
        raise ValueError(f"repetitions must be at least 1, got {repetitions}")

    parentCgroup = prepareParentCgroup()

    forkContext = multiprocessing.get_context(FORK_START_METHOD)
    startedThreadGroups: list[tuple[BaseProcess, Connection, str]] = []
    threadGroupIndex = 0
    runsPerThreadGroup = __countRunsPerThreadGroup(repetitions, len(threadGroups))
    for threadGroup, threadGroupRepetitions in zip(threadGroups, runsPerThreadGroup):
        if threadGroupRepetitions == 0:
            continue  # fewer runs than groups: this group has nothing to do
        threadGroupCgroup = createCgroup(parentCgroup, f"{THREAD_GROUP_CGROUP_PREFIX}{threadGroupIndex}")
        threadGroupIndex += 1
        errorReceiver, errorSender = forkContext.Pipe(duplex=False)
        process = forkContext.Process(
            target=__runThreadGroup,
            args=(runCase, threadGroup, threadGroupCgroup, threadGroupRepetitions, errorSender)
        )
        process.start()
        errorSender.close()
        startedThreadGroups.append((process, errorReceiver, threadGroupCgroup))

    errors: list[Exception] = []
    for process, errorReceiver, threadGroupCgroup in startedThreadGroups:
        try:
            threadGroupError = errorReceiver.recv()  # None, or the error the group raised
        except EOFError:  # the process died without sending anything
            threadGroupError = RuntimeError(f"run process died ({process.exitcode})")
        process.join()
        removeCgroup(threadGroupCgroup)  # empty now: its process and the SU programs it started ended
        if threadGroupError is not None:
            errors.append(threadGroupError)
    if errors:
        raise errors[0]
