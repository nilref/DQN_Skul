import win32gui
import win32api
import win32process
import ctypes
import ctypes.wintypes

Psapi = ctypes.WinDLL('Psapi.dll')
Kernel32 = ctypes.WinDLL('kernel32.dll')
PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010


def EnumProcessModulesEx(hProcess):
    buf_count = 256
    while True:
        LIST_MODULES_ALL = 0x03
        buf = (ctypes.wintypes.HMODULE * buf_count)()
        buf_size = ctypes.sizeof(buf)
        needed = ctypes.wintypes.DWORD()
        if not Psapi.EnumProcessModulesEx(hProcess, ctypes.byref(buf), buf_size, ctypes.byref(needed), LIST_MODULES_ALL):
            raise OSError('EnumProcessModulesEx failed')
        if buf_size < needed.value:
            buf_count = needed.value // (buf_size // buf_count)
            continue
        count = needed.value // (buf_size // buf_count)
        return map(ctypes.wintypes.HMODULE, buf[:count])

def ReadProcessMemory(hProcess, lpBaseAddress):
    lpBaseAddress = lpBaseAddress
    ReadBuffer = ctypes.c_double()
    lpBuffer = ctypes.byref(ReadBuffer)
    nSize = ctypes.sizeof(ReadBuffer)
    lpNumberOfBytesRead = ctypes.c_ulong(0)

    ctypes.windll.kernel32.ReadProcessMemory(
                                            hProcess,
                                            lpBaseAddress,
                                            lpBuffer,
                                            nSize,
                                            lpNumberOfBytesRead
                                            )
    return ReadBuffer.value

hd = win32gui.FindWindow(None, "Skul")
print("hd: ",hd)
pid = win32process.GetWindowThreadProcessId(hd)[1]
print("pid: ",pid)
process_handle = win32api.OpenProcess(0x1F0FFF, False, pid)
print("process_handle: ",process_handle)
hProcess = Kernel32.OpenProcess(
        PROCESS_QUERY_INFORMATION | PROCESS_VM_READ,
        False, pid)
hModule  = EnumProcessModulesEx(hProcess)
kernal32 = ctypes.windll.LoadLibrary(r"C:\\Windows\\System32\\kernel32.dll")
for i in hModule:
    temp = win32process.GetModuleFileNameEx(process_handle,i.value)
    if temp[-15:] == "UnityPlayer.dll":
        UnityPlayer = i.value
    if temp[-18:] == "mono-2.0-bdwgc.dll":
        mono = i.value
print("UnityPlayer: ", UnityPlayer)
print("mono: ", mono)

base_address = UnityPlayer + 0x019EEC58
print("base_address: ", base_address)
offset_address = ctypes.c_longlong()
nSize = ctypes.sizeof(offset_address)
print("nSize: ", nSize)
offset_list = [0xA0, 0x40, 0x60, 0x50, 0x18, 0xC0, 0x20]
# ctypes.c_void_p()
kernal32.ReadProcessMemory(int(process_handle), ctypes.c_void_p(base_address), ctypes.byref(offset_address), nSize, None)
print("offset_address start: " , offset_address)
for offset in offset_list:
    print(hex(offset))
    kernal32.ReadProcessMemory(int(process_handle), ctypes.c_void_p(offset_address.value + offset), ctypes.byref(offset_address), nSize, None)

memory_value = ctypes.c_double()
vSize = ctypes.sizeof(memory_value)
last_offset = 0x80
kernal32.ReadProcessMemory(int(process_handle), ctypes.c_void_p(offset_address.value + last_offset), ctypes.byref(memory_value), vSize, None)
print("hp: %d" % memory_value.value)

#print("hp: ", ReadProcessMemory(int(process_handle), ctypes.c_void_p(offset_address.value)))


# print(ReadProcessMemory(int(process_handle), ctypes.c_void_p(base_address)))


print("-----------------------------------------------------------")