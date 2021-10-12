

class Node:

    __slots__ = {"frequency", "value", "left", "right"}

    def __init__(self, frequency, value=None, left=None, right=None):
        self.frequency = frequency
        self.value = value
        self.left = left
        self.right = right

    def __cmp__(self, other):
        return self.frequency - other.frequency

    def __lt__(self, other):
        return self.frequency < other.frequency
