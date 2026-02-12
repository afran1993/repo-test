class Quest:
    def __init__(self, id_, title, description, stages=None, reward=None):
        self.id = id_
        self.title = title
        self.description = description
        self.stages = stages or []
        self.current = 0
        self.completed = False
        self.reward = reward or {}

    def advance(self):
        if self.completed:
            return
        self.current += 1
        if self.current >= len(self.stages):
            self.completed = True
            return True
        return False

    def status(self):
        if self.completed:
            return f"{self.title} (Completed)"
        return f"{self.title} - Stage {self.current+1}/{max(1,len(self.stages))}: {self.stages[self.current]}"
