import shlex


def parse_command(line):
    try:
        parts = shlex.split(line)
    except Exception:
        parts = line.split()
    if not parts:
        return None, []
    verb = parts[0].lower()
    args = parts[1:]
    return verb, args


def normalize_target(args):
    return ' '.join(args)
