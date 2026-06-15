"""FPLP Language - Environment (variable scope management)"""


class Environment:
    """Variable scope with optional outer (enclosing) scope for closures."""

    def __init__(self, outer=None):
        self.store = {}
        self.outer = outer

    def get(self, name):
        """Look up a variable. Walks up the scope chain."""
        if name in self.store:
            return self.store[name]
        if self.outer is not None:
            return self.outer.get(name)
        return None

    def set(self, name, value):
        """Set a variable in the current scope."""
        self.store[name] = value

    def assign(self, name, value):
        """Re-assign a variable, walking up the scope chain."""
        if name in self.store:
            self.store[name] = value
            return True
        if self.outer is not None:
            return self.outer.assign(name, value)
        return False

    def __repr__(self):
        return f"Env({list(self.store.keys())})"
