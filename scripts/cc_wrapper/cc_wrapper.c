#include <string.h>
#include <stdio.h>
#include <stdbool.h>
#include <assert.h>

#include <sys/time.h>
#include <sys/wait.h>
#include <sys/stat.h>

#include <limits.h>
#include <unistd.h>
#include <fcntl.h>

#include <limits.h>

#if !defined(COMPILER_NAME) || !defined(COMPILER_PATH) || !defined(OUTPUT_FILE)
 #error "Compiler not specified. Please set COMPILER_NAME, COMPILER_PATH and "\
        "OUTPUT_FILE macros."
#endif

struct data_info
{
    const char* source;
    struct timeval t_start;
    struct timeval t_end;
};

static bool is_source_code(const char* arg)
{
    const char* ptr = arg;
    const char* last_dot = NULL;

    /* Walk through the string until we find its extension */
    for (ptr = arg; *ptr != '\0'; ptr++)
        if (*ptr == '.')
            last_dot = ptr;

    /* Hope it to be precise, as we also need to be fast.
     * Maybe we might need to replace it by a trie (data structure)*/
    if (last_dot && (last_dot[1] == 'c' || last_dot[1] == 'C'))
        return true;

    return false;
}

static struct data_info* parse_args(int argc, char* argv[],
                                    struct data_info* out)
{
    int i;
    for (i = 0; i < argc; i++)
    {
        if (is_source_code(argv[i]))
        {
            out->source = argv[i];
            return out;
        }
    }
    out->source = "(UNKNOWN)";
    return out;
}

static void write_data(const char* path, const struct data_info* out)
{
    static char buffer[PIPE_BUF];
    int fd = open(path, O_WRONLY | O_APPEND | O_CREAT, S_IRUSR | S_IWUSR);
    size_t n1, n2;
    assert(fd);

    n1 = snprintf(buffer, PIPE_BUF, "File: %s Start: %ld.%06ld End: %ld.%06ld\n",
            out->source,
            out->t_start.tv_sec,
            out->t_start.tv_usec,
            out->t_end.tv_sec,
            out->t_end.tv_usec);

    n2 = write(fd, buffer, n1);
    close(fd);
    assert(n1 == n2);
}

int main(int argc, char* argv[], char* const envp[])
{
    static struct data_info out;
    int pid;

    /* Lie to gcc. Tell that we are running from system */
    argv[0] = COMPILER_NAME;

    gettimeofday(&out.t_start, NULL);

    if ((pid = fork()) == 0)
    {
        /* Child */
        execve(COMPILER_PATH, argv, envp);
    }
    else
    {
        /* Parent */
        int return_stats;
        parse_args(argc, argv, &out);
        waitpid(pid, &return_stats, 0);

        gettimeofday(&out.t_end, NULL);

        write_data(OUTPUT_FILE, &out);
    }

    return 0;
}
