import bcrypt

class LoginHandler:
    def __init__(self):
        self.login_attempts= 0
        self.slow_mode = False

    def dummylogin(self,provided_password) -> bool:
        dummy_hash = b'$2b$12$LQv3c1yqBWVHxkd0LQ1bpu.vlQjF8WfCW8dXPg4VqBKVpQW.8i6cG'
        bcrypt.checkpw(provided_password.encode('utf-8'), dummy_hash)
        return False

    def verify_password(self, provided_password, stored_password) -> bool:
        # stored_hash.encode is a conversation from str to bytes because checkpw expects bytes
        return bcrypt.checkpw(
            provided_password.encode('utf-8'),
            stored_password.encode('utf-8') if isinstance(stored_password, str) else stored_password
        )