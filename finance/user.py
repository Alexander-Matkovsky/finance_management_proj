class User:
    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name
        self.validate()

    def validate(self):
        if not self.name:
            raise ValueError("User name cannot be empty")

    def __str__(self):
        return f"User(id={self.user_id}, name={self.name})"

