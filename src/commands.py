import shlex


def parse_command(line):
    # Enhanced parser: keep quoted phrases and detect prepositions
    text = line.strip()
    if not text:
        return None, []
    # simple replacements for common italian verbs
    text = text.replace('parla con', 'talk').replace('parla', 'talk')
    text = text.replace('chiedi', 'ask').replace('usa', 'use')
    # split respecting quotes
    try:
        parts = shlex.split(text)
    except Exception:
        parts = text.split()
    verb = parts[0].lower()
    args = parts[1:]
    # detect 'on' or 'against' or 'about'
    return verb, args


def normalize_target(args):
    return ' '.join(args)
