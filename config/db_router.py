"""
Database router for read replica support.

Routes read queries to replica databases and write queries to primary.
Optimizes database load distribution for better performance.
"""


class ReadReplicaRouter:
    """
    A router to control database operations for read replica support.

    - All write operations go to the primary database
    - Read operations are distributed across read replicas
    """

    def db_for_read(self, model, **hints):
        """
        Route read queries to read replicas.
        Uses round-robin or random selection if multiple replicas exist.
        """
        import random

        # List of available read replicas
        replicas = ["replica1", "replica2"]

        # Randomly select a replica (can be improved with round-robin)
        return random.choice(replicas)

    def db_for_write(self, model, **hints):
        """
        Route all write operations to the primary database.
        """
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations between objects in the same database.
        """
        db_set = {"default", "replica1", "replica2"}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Ensure migrations only run on the primary database.
        """
        return db == "default"
