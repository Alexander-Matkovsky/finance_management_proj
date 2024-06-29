class User:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.validate()

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }
    def validate(self):
        if not self.name:
            raise ValueError("User name cannot be empty")

    def __str__(self):
        return f"User(id={self.id}, name={self.name})"

