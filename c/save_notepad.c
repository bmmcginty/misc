#include <stdbool.h>
#include <stdio.h>
#include <windows.h>
#include <time.h>

typedef struct Windows {
int ctr;
DWORD pid;
HWND proc;
HWND window;
bool no_kill;
struct Windows *next;
} Windows;

void add_window(Windows *ptr, HWND hwnd);
void win_free(PVOID *ptr);
PVOID win_malloc(int length);
WINBOOL enum_windows_callback(HWND hwnd, LPARAM ptr);

void win_free(PVOID *ptr) {
VirtualFree(ptr, 0, MEM_RELEASE);
}

PVOID win_malloc(int length) {
return VirtualAlloc((LPVOID) NULL, 
    (DWORD) length,
MEM_COMMIT, 
    PAGE_READWRITE); 
}

WINBOOL enum_windows_callback(HWND hwnd, LPARAM ptr) {
int length;
length=GetWindowTextLength(hwnd);
if(!length) {
return TRUE;
}
PSTR title=win_malloc(length+1);
int ret=GetWindowText(hwnd, title, length+1);
if(strstr(title, "Untitled - Notepad") != NULL) {
printf("%s\n", title);
add_window((Windows *) ptr, hwnd);
}
win_free(title);
return TRUE;
}

void add_window(Windows *ptr, HWND hwnd) {
while(ptr->next) {
ptr=ptr->next;
}
ptr->no_kill=false;
ptr->pid=0;
ptr->next=(Windows*) win_malloc(sizeof(Windows));
ptr->next->pid=0;
ptr->window=hwnd;
        GetWindowThreadProcessId(ptr->window, &ptr->pid);
ptr->proc=OpenProcess( PROCESS_TERMINATE, FALSE, ptr->pid);
}

int main() {
time_t rawtime;
struct tm * timeinfo;
char fn[255];
time (&rawtime);
timeinfo = localtime(&rawtime);
  strftime(fn,sizeof(fn),"c:\\users\\bmmcginty\\documents\\save-%Y-%m-%d_%H-%M-%S.txt",timeinfo);
FILE *fh;
fh=fopen(fn,"wb");
Windows *ptr;
HWND w, te;
PSTR body;
int length;
ptr=win_malloc(sizeof(Windows));
if(!EnumWindows(enum_windows_callback, ptr)) {
} else {
}
Windows *tmp,*ptr_tmp;
bool no_kill=false;
ptr_tmp=ptr;
while(1) {
if(!ptr_tmp) {
break;
}
if(ptr_tmp->pid==0) {
ptr_tmp=ptr_tmp->next;
continue;
}
w = ptr_tmp->window;
te = FindWindowEx(w, NULL, "Edit", NULL);
length=SendMessage(te, WM_GETTEXTLENGTH, NULL, NULL);
printf("pid=%d, %Ld\n", ptr_tmp->pid, length);
body=win_malloc(length+1);
SendMessage(te, WM_GETTEXT, length+1, body);
int written=fprintf(fh, "%s\n-----\n", body);
fflush(fh);
if (written-7 != length ) {
printf("written %d body %d\n",written,length);
}
if(!ptr_tmp->proc) {
ptr_tmp->no_kill=true;
no_kill=true;
}
ptr_tmp=ptr_tmp->next;
}
if(no_kill) {
printf("failed to open at least one notepad handle for termination so not terminating any windows\n");
}
ptr_tmp=ptr;
while(ptr_tmp) {
if(ptr_tmp->pid!=0) {
//last window entry is an empty entry due to add_window call, so it's pid is set to 0
if(no_kill==false) {
printf("terminating pid %d\n", ptr_tmp->pid);
TerminateProcess(ptr_tmp->proc, 0);
CloseHandle(ptr_tmp->proc);
}
if(ptr_tmp->no_kill==true) {
printf("unable to terminate process %d\n", ptr_tmp->pid);
}
}
tmp=ptr_tmp->next;
win_free(ptr_tmp);
ptr_tmp=tmp;
}
fclose(fh);
printf("done\n");
return 0;
}

