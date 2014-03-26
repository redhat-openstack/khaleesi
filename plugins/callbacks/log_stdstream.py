import os
import time
import json

TIME_FORMAT="%b %d %Y %H:%M:%S"
MARK_FORMAT="%(now)s ======== MARK ========\n"
MSG_FORMAT="%(now)s - %(category)s - %(data)s\n\n"
STDOUT_FORMAT="%(now)s - stdout:\n %(stdout)s\n\n"
STDERR_FORMAT="%(now)s - stderr:\n %(stderr)s\n\n"
RESULTS_START="%(now)s - results\n"
RESULTS_FORMAT="%(result)s\n"
RESULTS_END="\n"

LOG_PATH=os.getenv('KHALEESI_LOG_PATH', '/tmp/stdstream_logs')

if not os.path.exists(LOG_PATH):
    os.makedirs(LOG_PATH)

def log(host, category, data):
    stderr = stdout = results = None
    if type(data) == dict:
        if 'verbose_override' in data:
            data = 'omitted'
        else:
            data = data.copy()
            invocation = data.pop('invocation', None)
            stdout = data.pop('stdout', None)
            stderr = data.pop('stderr', None)
            results = data.pop('results', None)
            data = json.dumps(data)
            if invocation is not None:
                data = json.dumps(invocation) + " => %s " % data

    path = os.path.join(LOG_PATH, host)
    now = time.strftime(TIME_FORMAT, time.localtime())
    fd = open(path, "a")
    fd.write(MARK_FORMAT % dict(now=now))
    fd.write(MSG_FORMAT % dict(now=now, category=category, data=data))
    if stdout:
        fd.write(STDOUT_FORMAT % dict(now=now, stdout=stdout))
    if stderr:
        fd.write(STDERR_FORMAT % dict(now=now, stderr=stderr))
    if results:
        fd.write(RESULTS_START % dict(now=now))
        [fd.write(RESULTS_FORMAT % dict(result=result)) for result in results]
        fd.write(RESULTS_END)
    fd.close()

class CallbackModule(object):
    """
    logs playbook results, per host, in /tmp/ansible/stdstream_logs
    """

    def on_any(self, *args, **kwargs):
        pass

    def runner_on_failed(self, host, res, ignore_errors=False):
        log(host, 'FAILED', res)

    def runner_on_ok(self, host, res):
        log(host, 'OK', res)

    def runner_on_error(self, host, msg):
        log(host, 'ERROR', msg)

    def runner_on_skipped(self, host, item=None):
        log(host, 'SKIPPED', '...')

    def runner_on_unreachable(self, host, res):
        log(host, 'UNREACHABLE', res)

    def runner_on_no_hosts(self):
        pass

    def runner_on_async_poll(self, host, res, jid, clock):
        pass

    def runner_on_async_ok(self, host, res, jid):
        pass

    def runner_on_async_failed(self, host, res, jid):
        log(host, 'ASYNC_FAILED', res)

    def playbook_on_start(self):
        pass

    def playbook_on_notify(self, host, handler):
        pass

    def playbook_on_no_hosts_matched(self):
        pass

    def playbook_on_no_hosts_remaining(self):
        pass

    def playbook_on_task_start(self, name, is_conditional):
        pass

    def playbook_on_vars_prompt(self, varname, private=True, prompt=None, encrypt=None, confirm=False, salt_size=None, salt=None, default=None):
        pass

    def playbook_on_setup(self):
        pass

    def playbook_on_import_for_host(self, host, imported_file):
        log(host, 'IMPORTED', imported_file)

    def playbook_on_not_import_for_host(self, host, missing_file):
        log(host, 'NOTIMPORTED', missing_file)

    def playbook_on_play_start(self, pattern):
        pass

    def playbook_on_stats(self, stats):
        pass

