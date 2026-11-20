# debug_demo.py
def parse_age(text: str) -> int:
    return int(text)


def load_user(row: dict) -> dict:
    return {"name": row["name"], "age": parse_age(row["age"])}


load_user({"name": "Tom", "age": "十八"})
