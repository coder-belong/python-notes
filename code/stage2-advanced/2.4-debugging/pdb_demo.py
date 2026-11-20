# pdb_demo.py
def total_price(items: list[dict]) -> float:
    total = 0
    for item in items:
        breakpoint()                      # 程序停在这里，进入调试
        total += item["price"] * item["qty"]
    return total


print(total_price([{"price": 9.9, "qty": 2}, {"price": 5, "qty": 1}]))
