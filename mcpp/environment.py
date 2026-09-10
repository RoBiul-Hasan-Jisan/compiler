"""Scoped variable storage for the tree-walking interpreter."""


class Environment:
    """A single lexical scope, chained to its parent for name lookup."""

    def __init__(self, parent: "Environment" = None):
        self.parent = parent
        self.values = {}

    def declare(self, name: str, value):
        """Define a new variable in *this* scope."""
        self.values[name] = value

    def get(self, name: str):
        env = self._find(name)
        if env is None:
            raise NameError(name)
        return env.values[name]

    def set(self, name: str, value):
        """Assign to an existing variable, searching outward through scopes."""
        env = self._find(name)
        if env is None:
            raise NameError(name)
        env.values[name] = value

    def _find(self, name: str):
        env = self
        while env is not None:
            if name in env.values:
                return env
            env = env.parent
        return None

    def child(self) -> "Environment":
        return Environment(parent=self)
