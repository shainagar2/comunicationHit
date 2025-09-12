from app.security import hash_password, verify_password, validate_password_policy, make_reset_token_pair

def run_tests():
    # בדיקת hash+verify
    h, s = hash_password("Abc!234567")
    print("Hash:", h)
    print("Salt:", s)
    print("Verify OK:", verify_password("Abc!234567", s, h))
    print("Verify Fail:", verify_password("WrongPass!", s, h))

    # בדיקת מדיניות סיסמאות
    print("Policy errors:", validate_password_policy("short"))

    # בדיקת טוקן reset
    raw, sha1h = make_reset_token_pair()
    print("Raw token:", raw)
    print("SHA1 to save:", sha1h)

# 👇 חשוב! בלעדיו הקובץ רץ ויוצא בלי כלום
if __name__ == "__main__":
    run_tests()
