def to_int(text: str) -> int | None:
    try:
        return int(text)               # 可能出错的代码放 try 里
    except ValueError as e:            # 出了 ValueError 就到这里，e 是错误对象
        print("转换失败：", e)
        return None
    finally:
        print("不管成功失败都会执行")   # 常用来关文件、释放资源


print(to_int("42"))     # 不管成功失败都会执行 / 42
print(to_int("abc"))    # 转换失败： invalid literal for int() with base 10: 'abc' / 不管成功失败都会执行 / None


# ---- 接住不同的错误 ----
def parse(d: dict, key: str) -> int | str:
    try:
        return 100 // int(d[key])
    except KeyError:                               # 字典里没这个键
        return "没有这个键"
    except (ValueError, ZeroDivisionError) as e:   # 元组：这两种都到这里
        return f"值不对：{type(e).__name__}"


data = {"a": "abc", "b": "0", "c": "5"}
print(parse(data, "x"))   # 没有这个键
print(parse(data, "a"))   # 值不对：ValueError          int("abc") 出错
print(parse(data, "b"))   # 值不对：ZeroDivisionError   100 // 0 出错
print(parse(data, "c"))   # 20

# ---- else：try 里没出错才执行 ----
text = "42"
try:
    n = int(text)
except ValueError:
    print("不是数字")
else:
    print("转换成功：", n)    # 没出错才走到这里
finally:
    print("一定执行")
# 转换成功： 42
# 一定执行


# ---- 主动抛错 raise ----
def check(age: int) -> str:
    print("开始检查")
    if age < 0:
        raise ValueError(f"年龄不能是负数：{age}")
    print("检查通过")              # age < 0 时不会执行
    return "ok"


try:
    check(-1)
    print("这行也不会执行")          # check 里抛了错，try 里剩下的代码跳过
except ValueError as e:
    print("接住了：", e)
print("程序继续往下走")
# 开始检查
# 接住了： 年龄不能是负数：-1
# 程序继续往下走


# ---- 自定义异常 ----
class BalanceError(Exception):
    def __init__(self, message: str, need: int) -> None:
        super().__init__(message)   # 让 print(e) 显示的是 message
        self.need = need


def pay(balance: int, price: int) -> int:
    if balance < price:
        raise BalanceError("余额不足", need=price - balance)
    return balance - price


try:
    pay(10, 30)
except BalanceError as e:
    print(e, e.need)        # 余额不足 20
