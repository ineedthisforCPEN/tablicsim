"""
game/exceptions.py

This file defines the different exceptions that can cause a simulation
to fail.
"""

class IllegalMoveException(ValueError): ...


class IllegalStateException(ValueError): ...


class IllegalStrategyException(Exception): ...
