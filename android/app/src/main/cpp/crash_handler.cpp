#include <jni.h>
#include <android/log.h>
#include <signal.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <ucontext.h>
#include <dlfcn.h>
#include <sys/stat.h>
#include <sys/types.h>

#define TAG "CS16NativeCrash"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, TAG, __VA_ARGS__)
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, TAG, __VA_ARGS__)

static struct sigaction old_sa[NSIG];
static char g_out_dir[512] = {0};
static char g_package[256] = {0};
static int g_installed = 0;

static void get_time_str(char *buf, size_t n) {
    time_t t = time(NULL);
    struct tm *tm = localtime(&t);
    strftime(buf, n, "%Y%m%d_%H%M%S", tm);
}

static const char *signal_name(int sig) {
    switch (sig) {
    case SIGSEGV: return "SIGSEGV";
    case SIGABRT: return "SIGABRT";
    case SIGFPE:  return "SIGFPE";
    case SIGILL:  return "SIGILL";
    case SIGBUS:  return "SIGBUS";
    case SIGTRAP: return "SIGTRAP";
    default: return "UNKNOWN";
    }
}

static void write_backtrace(int fd) {
    void *frames[64];
    int n = 0;
    char buf[512];
    Dl_info info;
#if defined(__aarch64__) || defined(__arm__)
    frames[0] = __builtin_return_address(0);
    frames[1] = __builtin_return_address(1);
    frames[2] = __builtin_return_address(2);
    frames[3] = __builtin_return_address(3);
    n = 4;
#endif
    write(fd, "\n=== Backtrace ===\n", 18);
    for (int i = 0; i < n; i++) {
        if (dladdr(frames[i], &info) && info.dli_fname) {
            int len = snprintf(buf, sizeof(buf), "#%02d pc %p  %s (%s+%ld)\n",
                i, frames[i], info.dli_fname,
                info.dli_sname ? info.dli_sname : "?",
                (long)((char*)frames[i] - (char*)info.dli_saddr));
            if (len > 0) write(fd, buf, len);
        } else {
            int len = snprintf(buf, sizeof(buf), "#%02d pc %p\n", i, frames[i]);
            if (len > 0) write(fd, buf, len);
        }
    }
}

static void handler(int sig, siginfo_t *si, void *ctx) {
    char ts[32];
    char path[768];
    char buf[1024];
    get_time_str(ts, sizeof(ts));
    const char *dir = g_out_dir[0] ? g_out_dir : "/sdcard/CS16Crash";
    snprintf(path, sizeof(path), "%s/native_crash_%s.log", dir, ts);
    int fd = open(path, O_WRONLY | O_CREAT | O_APPEND, 0644);
    if (fd < 0) {
        strcpy(path, "/data/local/tmp/CS16Crash");
        mkdir(path, 0777);
        snprintf(path, sizeof(path), "/data/local/tmp/CS16Crash/native_crash_%s.log", ts);
        fd = open(path, O_WRONLY | O_CREAT | O_APPEND, 0644);
        if (fd < 0) {
            if (old_sa[sig].sa_sigaction) old_sa[sig].sa_sigaction(sig, si, ctx);
            return;
        }
    }
    int len = snprintf(buf, sizeof(buf),
        "=== CS16 Native Crash Report ===\n"
        "time: %s\n"
        "package: %s\n"
        "signal: %d (%s)\n"
        "code: %d\n"
        "fault addr: %p\n"
        "pid: %d, tid: %d\n",
        ts, g_package, sig, signal_name(sig),
        si ? si->si_code : 0, si ? si->si_addr : 0,
        getpid(), gettid());
    write(fd, buf, len);
    if (ctx) {
        ucontext_t *uc = (ucontext_t*)ctx;
#if defined(__aarch64__)
        len = snprintf(buf, sizeof(buf),
            "\n=== Registers ===\n"
            "pc: %p\nsp: %p\n"
            "x0 : %p  x1 : %p  x2 : %p  x3 : %p\n"
            "x4 : %p  x5 : %p  x6 : %p  x7 : %p\n"
            "x8 : %p  x9 : %p  x10: %p  x11: %p\n"
            "x12: %p  x13: %p  x14: %p  x15: %p\n"
            "x16: %p  x17: %p  x18: %p  x19: %p\n"
            "x20: %p  x21: %p  x22: %p  x23: %p\n"
            "x24: %p  x25: %p  x26: %p  x27: %p\n"
            "x28: %p  x29: %p  x30: %p\n",
            (void*)uc->uc_mcontext.pc, (void*)uc->uc_mcontext.sp,
            (void*)uc->uc_mcontext.regs[0], (void*)uc->uc_mcontext.regs[1],
            (void*)uc->uc_mcontext.regs[2], (void*)uc->uc_mcontext.regs[3],
            (void*)uc->uc_mcontext.regs[4], (void*)uc->uc_mcontext.regs[5],
            (void*)uc->uc_mcontext.regs[6], (void*)uc->uc_mcontext.regs[7],
            (void*)uc->uc_mcontext.regs[8], (void*)uc->uc_mcontext.regs[9],
            (void*)uc->uc_mcontext.regs[10], (void*)uc->uc_mcontext.regs[11],
            (void*)uc->uc_mcontext.regs[12], (void*)uc->uc_mcontext.regs[13],
            (void*)uc->uc_mcontext.regs[14], (void*)uc->uc_mcontext.regs[15],
            (void*)uc->uc_mcontext.regs[16], (void*)uc->uc_mcontext.regs[17],
            (void*)uc->uc_mcontext.regs[18], (void*)uc->uc_mcontext.regs[19],
            (void*)uc->uc_mcontext.regs[20], (void*)uc->uc_mcontext.regs[21],
            (void*)uc->uc_mcontext.regs[22], (void*)uc->uc_mcontext.regs[23],
            (void*)uc->uc_mcontext.regs[24], (void*)uc->uc_mcontext.regs[25],
            (void*)uc->uc_mcontext.regs[26], (void*)uc->uc_mcontext.regs[27],
            (void*)uc->uc_mcontext.regs[28], (void*)uc->uc_mcontext.regs[29],
            (void*)uc->uc_mcontext.regs[30]);
        write(fd, buf, len);
#endif
    }
    write_backtrace(fd);
    write(fd, "\n=== End ===\n", 12);
    close(fd);
    LOGE("native crash written to %s", path);
    if (old_sa[sig].sa_sigaction) old_sa[sig].sa_sigaction(sig, si, ctx);
}

static void install_one(int sig) {
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_sigaction = handler;
    sa.sa_flags = SA_SIGINFO | SA_ONSTACK;
    sigemptyset(&sa.sa_mask);
    sigaction(sig, &sa, &old_sa[sig]);
}

extern "C" JNIEXPORT void JNICALL
Java_su_xash_cs16client_CS16CrashHandler_installNative(JNIEnv *env, jclass clazz, jstring dir, jstring pkg) {
    if (g_installed) return;
    if (dir) {
        const char *d = env->GetStringUTFChars(dir, NULL);
        if (d) {
            strncpy(g_out_dir, d, sizeof(g_out_dir) - 1);
            env->ReleaseStringUTFChars(dir, d);
            mkdir(g_out_dir, 0777);
        }
    }
    if (pkg) {
        const char *p = env->GetStringUTFChars(pkg, NULL);
        if (p) {
            strncpy(g_package, p, sizeof(g_package) - 1);
            env->ReleaseStringUTFChars(pkg, p);
        }
    }
    install_one(SIGSEGV);
    install_one(SIGABRT);
    install_one(SIGFPE);
    install_one(SIGILL);
    install_one(SIGBUS);
    install_one(SIGTRAP);
    g_installed = 1;
    LOGI("native crash handlers installed, dir=%s", g_out_dir);
}

extern "C" JNIEXPORT void JNICALL
Java_su_xash_cs16client_CS16CrashHandler_testNativeCrash(JNIEnv *env, jclass clazz) {
    volatile int *p = (int*)0x1;
    *p = 42;
}
