nums = [10, 20]
it = iter(nums)        # 从列表拿到迭代器
print(next(it))        # 10
print(next(it))        # 20
# next(it)             # 再取就报 StopIteration：没有了

# for n in nums: print(n) 在背后做的就是上面这些

# ---- 迭代器只能从头到尾走一遍 ----
it = iter([1, 2, 3])
print(list(it))        # [1, 2, 3]
print(list(it))        # []   已经取完了

# ---- zip / map / enumerate / 生成器返回的本身就是迭代器 ----
pairs = zip(["a", "b"], [1, 2])
print(dict(pairs))     # {'a': 1, 'b': 2}
print(dict(pairs))     # {}   第二次就空了；要用多次，先 list(...) 存起来


# ---- 自己写一个迭代器类 ----
class Countdown:
    def __init__(self, start: int) -> None:
        self.current = start

    def __iter__(self):            # for 开始时调用：返回迭代器自己
        return self

    def __next__(self) -> int:     # 每取一个值调用一次
        if self.current <= 0:
            raise StopIteration    # 告诉 for：没有了
        self.current -= 1
        return self.current + 1


for n in Countdown(3):
    print(n)                       # 3、2、1，每个一行
