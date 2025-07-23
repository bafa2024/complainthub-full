import sqlite3
import hashlib

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def get_all_users():
    conn = sqlite3.connect('voicebot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

def test_login(email, password):
    conn = sqlite3.connect('voicebot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        print(f"User found: {user}")
        print(f"Stored password hash: {user[4]}")
        print(f"Input password: {password}")
        print(f"Generated hash: {hash_password(password)}")
        print(f"Hash match: {user[4] == hash_password(password)}")
    else:
        print("User not found")

if __name__ == "__main__":
    print("All users in database:")
    users = get_all_users()
    for user in users:
        print(user)
    
    print("\nTesting login for test@example.com:")
    test_login("test@example.com", "testpass123")