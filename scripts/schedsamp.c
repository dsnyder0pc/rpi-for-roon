// schedsamp: sample per-thread and per-CPU scheduler accounting at a fixed
// interval, to measure how *stable* the audio threads' CPU use is over time.
//
// It reads cumulative nanosecond counters the kernel already keeps, so it can
// sample slowly or late without losing anything: every nanosecond of run time
// lands in some window. What the sampler controls is only its own footprint,
// which is why it is C, pins itself to a housekeeping core, opens every file
// once, allocates all memory before the run, and does no I/O until the end.
//
//   /proc/<pid>/task/<tid>/schedstat   run_ns  wait_ns  timeslices
//   /proc/schedstat  cpuN ... rq_cpu_time run_delay pcount (fields 7-9)
//
// "wait" is time spent runnable but not running, i.e. queued behind another
// thread on the same core. On a Host, the Diretta sender (CpuSend) shares its
// core with the end0 IRQ thread by design, so a few microseconds per wakeup
// there are expected. A thread alone on its core should show none.
//
// The sampler's own cost lands on its core: about 6% of CPU0 at 1 ms and 3% at
// 2 ms, nearly all of it the kernel formatting /proc text. Threads are found
// once at startup, so start it after playback has begun.
//
// Unprivileged. Build on the Pi itself:
//   gcc -O2 -Wall -o schedsamp schedsamp.c
//   ./schedsamp -d 300 -i 2000 -o run.csv

#define _GNU_SOURCE
#include <ctype.h>
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <sched.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <time.h>
#include <unistd.h>

#define MAX_THREADS 32
#define MAX_CPUS 8

// Threads whose comm contains one of these are sampled: the USB and network
// IRQ threads, the Target's diretta_app_target, and the Host's syncAlsa.
static const char *MATCH[] = { "xhci_hcd", "end0", "diretta_app", "syncAlsa", NULL };

struct thr { int fd; int tid; char comm[32]; };

static struct thr thr[MAX_THREADS];
static int nthr;
static int ncpu;
static int sfd = -1;  // /proc/schedstat
static volatile sig_atomic_t stop;

static void on_sig(int s) { (void)s; stop = 1; }

static uint64_t now_ns(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ull + ts.tv_nsec;
}

static int matches(const char *comm)
{
    for (const char **m = MATCH; *m; m++)
        if (strstr(comm, *m)) return 1;
    return 0;
}

static void discover(void)
{
    DIR *pd = opendir("/proc");
    struct dirent *p;
    while (pd && (p = readdir(pd))) {
        if (!isdigit((unsigned char)p->d_name[0])) continue;
        char path[600];
        snprintf(path, sizeof path, "/proc/%s/task", p->d_name);
        DIR *td = opendir(path);
        struct dirent *t;
        while (td && (t = readdir(td))) {
            if (!isdigit((unsigned char)t->d_name[0]) || nthr == MAX_THREADS) continue;
            char comm[32] = "";
            snprintf(path, sizeof path, "/proc/%s/task/%s/comm", p->d_name, t->d_name);
            FILE *f = fopen(path, "r");
            if (!f) continue;
            if (fgets(comm, sizeof comm, f)) comm[strcspn(comm, "\n")] = 0;
            fclose(f);
            if (!matches(comm)) continue;
            snprintf(path, sizeof path, "/proc/%s/task/%s/schedstat", p->d_name, t->d_name);
            int fd = open(path, O_RDONLY);
            if (fd < 0) continue;
            thr[nthr].fd = fd;
            thr[nthr].tid = atoi(t->d_name);
            snprintf(thr[nthr].comm, sizeof thr[nthr].comm, "%s", comm);
            nthr++;
        }
        if (td) closedir(td);
    }
    if (pd) closedir(pd);
}

// Parse three unsigned integers from a thread's schedstat.
static void read_thr(int fd, uint64_t *out)
{
    char buf[128];
    ssize_t n = pread(fd, buf, sizeof buf - 1, 0);
    if (n <= 0) { out[0] = out[1] = out[2] = UINT64_MAX; return; }
    buf[n] = 0;
    char *s = buf;
    for (int i = 0; i < 3; i++) out[i] = strtoull(s, &s, 10);
}

// Parse rq_cpu_time, run_delay, pcount for each cpuN line of /proc/schedstat.
// Returns the number of CPUs seen.
static int read_cpus(uint64_t *out)
{
    static char buf[16384];
    ssize_t n = pread(sfd, buf, sizeof buf - 1, 0);
    if (n <= 0) return 0;
    buf[n] = 0;
    int c = 0;
    for (char *s = buf; s && *s && c < MAX_CPUS; s = strchr(s, '\n'), s = s ? s + 1 : s) {
        if (strncmp(s, "cpu", 3) || !isdigit((unsigned char)s[3])) continue;
        char *q = s + 3;
        strtoul(q, &q, 10);
        uint64_t f[9];
        for (int i = 0; i < 9; i++) f[i] = strtoull(q, &q, 10);
        out[c * 3 + 0] = f[6];
        out[c * 3 + 1] = f[7];
        out[c * 3 + 2] = f[8];
        c++;
    }
    return c;
}

static int cmp_u64(const void *a, const void *b)
{
    uint64_t x = *(const uint64_t *)a, y = *(const uint64_t *)b;
    return x < y ? -1 : x > y;
}

// Per-window summary of one counter column: run share (permille of the window)
// as p50/p99/max, plus wait totals.
static void summarize(const char *label, const uint64_t *buf, size_t ns, int cols,
                      int col, size_t stride, uint64_t *scratch)
{
    size_t nw = 0, wait_windows = 0;
    uint64_t wait_total = 0, wait_max = 0;
    for (size_t i = stride; i < ns; i += stride) {
        const uint64_t *a = buf + (i - stride) * cols, *b = buf + i * cols;
        if (a[col] == UINT64_MAX || b[col] == UINT64_MAX) continue;
        uint64_t dt = b[0] - a[0];
        uint64_t run = b[col] - a[col];
        uint64_t wait = b[col + 1] - a[col + 1];
        scratch[nw++] = run * 100000 / dt;  // thousandths of a percent
        wait_total += wait;
        if (wait > wait_max) wait_max = wait;
        if (wait) wait_windows++;
    }
    if (!nw) { printf("%-28s (no data)\n", label); return; }
    qsort(scratch, nw, sizeof *scratch, cmp_u64);
    printf("%-28s %7.3f %7.3f %7.3f %7.3f   %10.1f %9.1f %8zu/%zu\n", label,
           scratch[0] / 1000.0, scratch[nw / 2] / 1000.0,
           scratch[nw * 99 / 100] / 1000.0, scratch[nw - 1] / 1000.0,
           wait_total / 1000.0, wait_max / 1000.0, wait_windows, nw);
}

static void usage(const char *p)
{
    fprintf(stderr,
        "usage: %s [-d seconds] [-i interval_us] [-w window_ms] [-c cpu] [-o out.csv]\n"
        "  -d  run length (default 300)\n"
        "  -i  sample interval (default 1000)\n"
        "  -w  summary window (default 10)\n"
        "  -c  CPU to run the sampler on (default 0)\n"
        "  -o  write every raw sample as CSV\n", p);
    exit(2);
}

int main(int argc, char **argv)
{
    int secs = 300, interval_us = 1000, window_ms = 10, cpu = 0, opt;
    const char *out = NULL;
    while ((opt = getopt(argc, argv, "d:i:w:c:o:h")) != -1) {
        switch (opt) {
        case 'd': secs = atoi(optarg); break;
        case 'i': interval_us = atoi(optarg); break;
        case 'w': window_ms = atoi(optarg); break;
        case 'c': cpu = atoi(optarg); break;
        case 'o': out = optarg; break;
        default: usage(argv[0]);
        }
    }
    if (secs <= 0 || interval_us <= 0 || window_ms * 1000 < interval_us) usage(argv[0]);

    cpu_set_t set;
    CPU_ZERO(&set);
    CPU_SET(cpu, &set);
    if (sched_setaffinity(0, sizeof set, &set))
        perror("warning: could not pin the sampler");

    discover();
    sfd = open("/proc/schedstat", O_RDONLY);
    uint64_t cpubuf[MAX_CPUS * 3];
    ncpu = sfd >= 0 ? read_cpus(cpubuf) : 0;
    if (!nthr && !ncpu) { fprintf(stderr, "Nothing to sample.\n"); return 1; }

    int cols = 1 + 3 * nthr + 3 * ncpu;
    size_t nsamp = (size_t)secs * 1000000 / interval_us + 1;
    size_t bytes = nsamp * cols * sizeof(uint64_t);
    uint64_t *buf = malloc(bytes);
    uint64_t *scratch = malloc(nsamp * sizeof(uint64_t));
    if (!buf || !scratch) { fprintf(stderr, "Out of memory (%zu MB).\n", bytes >> 20); return 1; }
    // Fault every page in now, so the loop never takes a page fault.
    memset(buf, 0, bytes);
    memset(scratch, 0, nsamp * sizeof(uint64_t));
    mlockall(MCL_CURRENT);

    fprintf(stderr, "Sampling %d threads and %d CPUs every %d us for %d s on CPU%d (%zu MB)...\n",
            nthr, ncpu, interval_us, secs, cpu, bytes >> 20);
    for (int i = 0; i < nthr; i++)
        fprintf(stderr, "  %6d  %s\n", thr[i].tid, thr[i].comm);

    signal(SIGINT, on_sig);
    signal(SIGTERM, on_sig);

    struct timespec next;
    clock_gettime(CLOCK_MONOTONIC, &next);
    size_t ns = 0;
    uint64_t max_gap = 0, late = 0;
    while (ns < nsamp && !stop) {
        uint64_t *row = buf + ns * cols;
        row[0] = now_ns();
        for (int i = 0; i < nthr; i++)
            read_thr(thr[i].fd, row + 1 + 3 * i);
        if (ncpu) {
            read_cpus(cpubuf);
            memcpy(row + 1 + 3 * nthr, cpubuf, 3 * ncpu * sizeof(uint64_t));
        }
        if (ns) {
            uint64_t gap = row[0] - row[-cols];
            if (gap > max_gap) max_gap = gap;
            if (gap > 2ull * interval_us * 1000) late++;
        }
        ns++;
        next.tv_nsec += interval_us * 1000L;
        while (next.tv_nsec >= 1000000000L) { next.tv_nsec -= 1000000000L; next.tv_sec++; }
        while (clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &next, NULL) == EINTR && !stop)
            ;
    }

    printf("\n%zu samples over %.1f s; max gap %.0f us; %llu gaps over 2x interval\n",
           ns, ns > 1 ? (buf[(ns - 1) * cols] - buf[0]) / 1e9 : 0.0,
           max_gap / 1e3, (unsigned long long)late);
    printf("\nCPU share per %d ms window (%% of one core); wait = runnable but not running\n\n",
           window_ms);
    printf("%-28s %7s %7s %7s %7s   %10s %9s %s\n", "", "min", "p50", "p99", "max",
           "wait us", "max/win", "windows w/ wait");
    size_t stride = (size_t)window_ms * 1000 / interval_us;
    char label[64];
    for (int i = 0; i < nthr; i++) {
        snprintf(label, sizeof label, "%s [%d]", thr[i].comm, thr[i].tid);
        summarize(label, buf, ns, cols, 1 + 3 * i, stride, scratch);
    }
    for (int c = 0; c < ncpu; c++) {
        snprintf(label, sizeof label, "cpu%d (all tasks)", c);
        summarize(label, buf, ns, cols, 1 + 3 * nthr + 3 * c, stride, scratch);
    }

    if (out) {
        FILE *f = fopen(out, "w");
        if (!f) { perror(out); return 1; }
        fprintf(f, "t_ns");
        for (int i = 0; i < nthr; i++)
            fprintf(f, ",%s_%d_run,%s_%d_wait,%s_%d_slices", thr[i].comm, thr[i].tid,
                    thr[i].comm, thr[i].tid, thr[i].comm, thr[i].tid);
        for (int c = 0; c < ncpu; c++)
            fprintf(f, ",cpu%d_run,cpu%d_wait,cpu%d_slices", c, c, c);
        fputc('\n', f);
        for (size_t i = 0; i < ns; i++) {
            const uint64_t *row = buf + i * cols;
            for (int j = 0; j < cols; j++)
                fprintf(f, j ? ",%llu" : "%llu", (unsigned long long)row[j]);
            fputc('\n', f);
        }
        fclose(f);
        fprintf(stderr, "Wrote %s\n", out);
    }
    return 0;
}
