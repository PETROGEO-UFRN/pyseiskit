import os

# cgroups (v2): the kernel groups processes and measures each group as a whole, children
# included. A cgroup is a directory under CGROUP_ROOT; its files hold the measurements.
# Creating cgroups needs one this user may write to: start the benchmark through
# `systemd-run --user --scope -p Delegate=yes ...`.
CGROUP_ROOT = "/sys/fs/cgroup"
PROCESS_CGROUP_PATH = "/proc/self/cgroup"  # "0::/path/of/this/process/cgroup"
CGROUP_PROCESSES_FILE = "cgroup.procs"  # one process id per line; writing one moves it here
CGROUP_SUBTREE_CONTROL_FILE = "cgroup.subtree_control"
ENABLE_MEMORY_CONTROLLER = "+memory"  # gives the cgroups below memory.peak and memory.current
ENGINE_CGROUP_NAME = "engine"  # where the starting processes move: a cgroup with processes
                               # can't enable controllers for the cgroups below it

MEMORY_PEAK_FILE = "memory.peak"  # bytes; resettable per open file (kernel 6.12+)
MEMORY_CURRENT_FILE = "memory.current"  # bytes
CPU_STAT_FILE = "cpu.stat"
CPU_USAGE_FIELD = "usage_usec"  # CPU time in CPU_STAT_FILE, microseconds
RESET_MEMORY_PEAK = b"reset"  # any text written to MEMORY_PEAK_FILE resets it to the current usage
NUMBER_READ_BYTES = 64  # enough for one number from a cgroup file


def readCgroupPath() -> str:
    # where the cgroup of this process lives under CGROUP_ROOT
    with open(PROCESS_CGROUP_PATH) as processCgroup:
        cgroup = processCgroup.read().strip().split("::", 1)[1]
    return CGROUP_ROOT + cgroup


def moveToCgroup(processId: int, cgroup: str) -> None:
    # processes the moved one starts afterwards are created in the same cgroup
    with open(os.path.join(cgroup, CGROUP_PROCESSES_FILE), "w") as cgroupProcesses:
        cgroupProcesses.write(str(processId))


def prepareParentCgroup() -> str:
    # Returns the cgroup to create new cgroups in. The first call moves every process of the
    # starting cgroup (this one, and e.g. uv) into ENGINE_CGROUP_NAME below it.
    ownCgroup = readCgroupPath()
    if os.path.basename(ownCgroup) == ENGINE_CGROUP_NAME:
        return os.path.dirname(ownCgroup)  # prepared by an earlier call
    try:
        engineCgroup = os.path.join(ownCgroup, ENGINE_CGROUP_NAME)
        os.makedirs(engineCgroup, exist_ok=True)
        with open(os.path.join(ownCgroup, CGROUP_PROCESSES_FILE)) as cgroupProcesses:
            processIds = cgroupProcesses.read().split()
        for processId in processIds:
            moveToCgroup(int(processId), engineCgroup)
        with open(os.path.join(ownCgroup, CGROUP_SUBTREE_CONTROL_FILE), "w") as subtreeControl:
            subtreeControl.write(ENABLE_MEMORY_CONTROLLER)
    except OSError as error:
        raise RuntimeError(
            f"can't create cgroups in {ownCgroup} ({error}); start the benchmark with "
            "`systemd-run --user --scope -p Delegate=yes ...`"
        ) from error
    return ownCgroup


def createCgroup(parentCgroup: str, name: str) -> str:
    cgroup = os.path.join(parentCgroup, name)
    os.makedirs(cgroup, exist_ok=True)
    return cgroup


def removeCgroup(cgroup: str) -> None:
    # the kernel only removes a cgroup with no processes left in it
    os.rmdir(cgroup)


def readMemoryCurrentBytes(cgroup: str) -> int:
    with open(os.path.join(cgroup, MEMORY_CURRENT_FILE)) as memoryCurrent:
        return int(memoryCurrent.read())


def readCPUMicroseconds(cgroup: str) -> int:
    with open(os.path.join(cgroup, CPU_STAT_FILE)) as cpuStat:
        for line in cpuStat:
            field, value = line.split()
            if field == CPU_USAGE_FIELD:
                return int(value)
    raise RuntimeError(f"no {CPU_USAGE_FIELD} in {cgroup}/{CPU_STAT_FILE}")


def openAndResetMemoryPeak(cgroup: str) -> int:
    # The peak restarts from the current usage, but only for reads through the returned file:
    # keep it open until readAndCloseMemoryPeak.
    memoryPeakFile = os.open(os.path.join(cgroup, MEMORY_PEAK_FILE), os.O_RDWR)
    os.write(memoryPeakFile, RESET_MEMORY_PEAK)
    return memoryPeakFile


def readAndCloseMemoryPeak(memoryPeakFile: int) -> int:
    # the peak since openAndResetMemoryPeak, in bytes
    memoryPeakBytes = int(os.pread(memoryPeakFile, NUMBER_READ_BYTES, 0))
    os.close(memoryPeakFile)
    return memoryPeakBytes
