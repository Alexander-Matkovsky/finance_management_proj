class User:
    def __init__(self, id, name, email, hashed_password):
        self.id = id
        self.name = name
        self.email = email
        self.hashed_password = hashed_password
        self.validate()

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "hashed_password": self.hashed_password
        }
    
    def validate(self):
        if not self.name:
            raise ValueError("User name cannot be empty")
        if not self.email:
            raise ValueError("User email cannot be empty")
        if not self.hashed_password:
            raise ValueError("User password cannot be empty")

    def __str__(self):
        return f"User(id={self.id}, name={self.name}, email={self.email})"

