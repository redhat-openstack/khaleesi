import os
import coverage
import signal
import time



os.environ.setdefault('COVERAGE_PROCESS_START', "/coverage/config")
cps = os.environ['COVERAGE_PROCESS_START']

if (os.environ.get('REPORT_MODE', False) or
        "bin/coverage" in os.environ.get('_', 'foo')):  # TODO check arg[0]
    os.environ.setdefault('COVERAGE_FILE', "/coverage/data")
else:
    os.environ.setdefault('COVERAGE_FILE', "/coverage/data.%x.%d" %
                                   (int(time.time()*10000) & 0xFFFFFFF,
                                    os.getuid()))  # looping in 7.45h

real_signal = signal.signal
real_os_exit = os._exit

cov = coverage.coverage(config_file=cps, auto_data=True)
cov.start()
cov._warn_no_data = False
cov._warn_unimported_source = False


# the name is not faked, in the traces the cheat should be visible
def decorate_fatal_method(meth):
    def fatal_coverage_decor(*arg, **kwargs):
        cov.save()  # let it die noisily
        return meth(*arg, **kwargs)
    return fatal_coverage_decor

os_monkey_list = ['abort', '_exit', 'execl', 'execle', 'execlp',
                  'execlpe', 'execv', 'execve', 'execvp', 'execvpe']

for meth in os_monkey_list:
    setattr(os, meth, decorate_fatal_method(getattr(os, meth)))


def coverage_save_signal_handler(signum, frame):
    #    try:
    cov.save()
    #    finally:  # let it die noisily
    real_signal(signum, signal.SIG_DFL)
    os.kill(os.getpid(), signum)


# The list is incomplte!
DEF_TERM_SIGNALS = set((signal.SIGHUP, signal.SIGINT, signal.SIGPIPE,
                        signal.SIGALRM, signal.SIGTERM, signal.SIGUSR1,
                        signal.SIGUSR2, signal.SIGVTALRM, signal.SIGPROF))
DEF_CORE_SIGNALS = set((signal.SIGQUIT, signal.SIGILL, signal.SIGABRT,
                        signal.SIGFPE, signal.SIGBUS, signal.SIGSEGV,
                        signal.SIGXCPU, signal.SIGXFSZ, signal.SIGSYS))

# python by default handles the SIGINT and ignores the SIGPIPE
# Looks like the mod_wsgi changes the signal handlers before this file

for signum in DEF_TERM_SIGNALS | DEF_CORE_SIGNALS:
    origin = signal.signal(signum, coverage_save_signal_handler)
    if origin != signal.SIG_DFL or origin != signal.SIG_IGN:
        signal.signal(signum, origin)


def coverage_fake_signal(signalnum, handler):
    if signalnum not in DEF_TERM_SIGNALS:
        return real_signal(signalnum, handler)
    if handler == signal.SIG_DFL:
        ret = real_signal(signalnum, coverage_save_signal_handler)
    else:
        ret = real_signal(signalnum, handler)
    if ret == coverage_save_signal_handler:
        return signal.SIG_DFL
    return ret


signal.signal = coverage_fake_signal  # monkey
