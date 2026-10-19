"""Pydantic schemas: the API's request/response shapes (the public contract).

Kept separate from the ORM models (the database shape) so the two can evolve
independently, e.g. adding an internal column without exposing it.
"""
