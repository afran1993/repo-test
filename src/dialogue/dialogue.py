class DialogueNode:
    def __init__(self, id_, text, choices=None, actions=None):
        self.id = id_
        self.text = text
        self.choices = choices or []  # list of (text, next_id)
        self.actions = actions or []


def run_dialogue(node_map, start_id):
    cur = node_map.get(start_id)
    while cur:
        print('\n' + cur.text)
        if not cur.choices:
            return None
        for i, (txt, _) in enumerate(cur.choices, 1):
            print(f"{i}) {txt}")
        choice = input('-> ').strip()
        try:
            idx = int(choice) - 1
            _, next_id = cur.choices[idx]
            cur = node_map.get(next_id)
        except Exception:
            print('Invalid choice.')
