from FanQieNovelSpider import FanQieEbook


def fallback(type, content):
    if content[0] == "metadata":
        print("写入元数据中...")
    elif content[0] == "ready":
        print("开始获取章节")
    elif content[0] == "chapter":
        print(f"获取第{content[2]}/{content[3]}章（{content[1]}）中...")
    elif content[0] == "volumes":
        print("分卷中...")
    elif content[0] == "write":
        print("写入中...")
    elif content[0] == "done":
        print("完成!")


with open("./config") as f:
    test = FanQieEbook(input("输入要下载的书籍ID"), cookie=f.read(), fallback=fallback)

test.epub("./test.epub")
