actors = "a","b","c","d","e"
locations = "p", "q", "r"

class Step:
    def __init__(self,actors = set(), location = None, start = 0, end = 100):
        self.actors = actors
        self.location = location
        self.start = start
        self.end = end

    def update_location(self,to):
        self.location = to

    def add_actor(self, a):
        self.actors.add(a)

    def remove_actor(self, a):
        self.actors.discard(a)

data = [
        {"actors":{"a","b"}, "location": "p", "start": 0, "end": 10},
        {"actors":{"c","d"}, "location": "q", "start": 0, "end": 15},
        {"actors":{"a","b","c"}, "location": "p", "start": 15, "end": 30}
        ]





