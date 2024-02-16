import jwt
import secrets

from datetime import datetime, timezone, timedelta

"""
NOTE: THIS CODE IS CURRENTLY DEAD AND NOT USED AS WE ARE USING FLASK SESSIONS INSTEAD. KEEPING IT AROUND FOR NOW
      IF WE WANT TO USE IT LATER
"""

class Access:
    def __init__(self):
        self.secret = self.init_secret()

    def init_secret(self):
        """
        Generate a cryptographically secure random token string of 32 bytes.
        """
        return secrets.token_urlsafe(32)

    def generate_auth_cookie(self):
        return jwt.encode({"exp": datetime.now(timezone.utc) + timedelta(hours=24)}, self.secret)

    def validate_auth_cookie(self, cookie) -> bool:
        try:
            jwt.decode(cookie, self.secret, algorithms=["HS256"], require=["exp"])
            return True
        except:
            # jwt implements a ton of different exceptions this blanket catch is better than writing 20 excepts for every error
            return False

