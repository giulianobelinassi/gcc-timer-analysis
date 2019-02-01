#include <string.h>
#include <stdio.h>
#include <stdbool.h>
#include <unistd.h>
#include <assert.h>

#include <sys/time.h>
#include <sys/wait.h>

#if !defined(COMPILER_NAME) || !defined(COMPILER_PATH)
 #error "Compiler not specified. Please set COMPILER_NAME and "
        "COMPILER_PATH macros"
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
    FILE* stream_out = fopen(path, "a+b");
    assert(stream_out);
    fprintf(stream_out, "File: %s: Start: %ld.%06ld End: %ld.%06ld\n",
            out->source,
            out->t_start.tv_sec,
            out->t_start.tv_usec,
            out->t_end.tv_sec,
            out->t_end.tv_usec);
    fclose(stream_out);
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

        write_data("/tmp/data_1.txt", &out);
    }

    return 0;
}
