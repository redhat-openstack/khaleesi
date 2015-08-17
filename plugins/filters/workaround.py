from ansible import utils

print('Imported workaround filter')


def workaround_enabled(workarounds, *bugs, **kw):
    if not isinstance(workarounds, dict):
        return False

    for bug_id in bugs:
        enabled = workarounds.get(bug_id, {}).get('enabled', False)
        if not utils.boolean(enabled):
            return False
    return True


class FilterModule(object):

    def filters(self):
        print('Loading workaround filter')
        return {
            'bug': workaround_enabled,
        }
