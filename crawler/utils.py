class Counter:
    def __init__(self):
        self.val = 0

    def inc(self):
        self.val += 1

    def set(self, val):
        self.val = val

    def reset(self):
        self.val = 0

    def count(self):
        return self.val


class IdleCounter(Counter):
    def __init__(self):
        self.is_idle = False
        Counter.__init__(self)

    def inc(self):
        if self.is_idle:
            super(IdleCounter, self).inc()

    def set_idle(self):
        self.is_idle = True

    def unset_idle(self):
        self.is_idle = False
        self.reset()

    def idle(self):
        return self.is_idle
