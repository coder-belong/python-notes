# make_receipt.py：画一张小票图片，给 4.14 节看图的例子用（真实场景就是用户拍照上传）
from PIL import Image, ImageDraw, ImageFont

font = ImageFont.truetype("/System/Library/Fonts/Hiragino Sans GB.ttc", 26)   # macOS 自带的中文字体
small = ImageFont.truetype("/System/Library/Fonts/Hiragino Sans GB.ttc", 20)
img = Image.new("RGB", (480, 620), "white")
d = ImageDraw.Draw(img)
lines = [
    ("豆豆咖啡（科技园店）", font),
    ("2026-11-25 14:32  单号 A1024", small),
    ("-" * 40, small),
    ("拿铁（大杯）      x1    ¥28.00", font),
    ("美式（中杯）      x2    ¥36.00", font),
    ("桂花酒酿奶茶      x1    ¥18.00", font),
    ("-" * 40, small),
    ("合计                    ¥82.00", font),
    ("会员折扣（金卡 9 折）   -¥8.20", font),
    ("实付                    ¥73.80", font),
    ("-" * 40, small),
    ("支付方式：微信支付", small),
    ("本单获得积分：73", small),
]
y = 30
for text, f in lines:
    d.text((30, y), text, fill="black", font=f)
    y += 44
img.save("images/receipt.png")
print("saved images/receipt.png", img.size)
