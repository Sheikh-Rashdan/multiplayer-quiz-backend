import secrets
from string import ascii_uppercase

room_code_set = set()


def get_unique_room_code() -> str:
    while True:
        code = ""
        for _ in range(5):
            code += secrets.choice(ascii_uppercase)
        if code not in room_code_set:
            break
    room_code_set.add(code)

    return code
