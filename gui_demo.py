import tkinter as tk
import tkinter.ttk
import ttkbootstrap
import tkinter.messagebox
import tkinter.scrolledtext
import FanQieNovelSpider
import os
from PIL import Image, ImageTk
import requests
from io import BytesIO
import threading


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
}
stop = threading.Event()

window = ttkbootstrap.Window()
window.title("番茄免费小说客户端 by system-windows")
window.geometry("640x540")
window.resizable(False, True)

style = ttkbootstrap.Style("morph")

pager = tk.ttk.Notebook(window, width=640)
pager.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

cookie_frame = tk.ttk.Frame(pager)
tk.ttk.Label(cookie_frame, text="请输入 Cookie(不输入会影响阅读和下载功能):").pack(
    side=tk.TOP, fill=tk.BOTH
)
cookie_var = tk.StringVar()
cookie_entry = tk.ttk.Entry(cookie_frame, textvariable=cookie_var)
cookie_entry.pack(side=tk.TOP, fill=tk.BOTH)


def save_cookie():
    with open("./config", "w") as f:
        f.write(cookie_var.get())


tk.ttk.Button(cookie_frame, text="保存", command=save_cookie, bootstyle=ttkbootstrap.OUTLINE).pack(
    side=tk.TOP
)
pager.add(cookie_frame, text="Cookie 设置")

main_root_frame = tk.ttk.Frame(pager)
main_canvas = tk.Canvas(main_root_frame)
main_frame = tk.ttk.Frame(main_canvas)
main_scrollbar = tk.ttk.Scrollbar(main_root_frame, orient=tk.VERTICAL, command=main_canvas.yview)
book_covers = []
temp_cover = None
load_type = False
current_page = 0


def view_book(book_id):
    def view_book():
        global temp_cover
        book = FanQieNovelSpider.FanQieBook(book_id)
        book_info = book.get_infos()
        for widget in info_frame.winfo_children():
            widget.destroy()
        response = requests.get(url=book_info["cover"], headers=headers)
        image = Image.open(BytesIO(response.content))
        cover = ImageTk.PhotoImage(image)
        temp_cover = cover
        tk.ttk.Label(info_frame, image=cover).grid(row=0, column=0, rowspan=10)
        tk.ttk.Button(
            info_frame, text="开始阅读", command=read(book), bootstyle=ttkbootstrap.OUTLINE
        ).grid(row=0, column=4)
        tk.ttk.Button(
            info_frame, text="下载", command=download(book), bootstyle=ttkbootstrap.OUTLINE
        ).grid(row=0, column=5)
        scrolledtext = tk.scrolledtext.ScrolledText(info_frame, width=54)
        scrolledtext.grid(row=1, column=1, rowspan=9, columnspan=8)
        info_text = f"书名: {book_info['title']}\n作者: {book_info['author']}\n标签: {','.join(book_info['labels'])}\n字数: {book_info['word_count']}\n上次更新时间: {book_info['last_update_time']}\n简介: {book_info['intro']}"
        scrolledtext.insert("0.0", info_text)
        scrolledtext.config(state=tk.DISABLED)

        pager.select(4)

    return view_book


def download(book):
    def download():
        item_count = len(book.get_chap_ids())
        progressbar = tk.ttk.Progressbar(info_frame, maximum=item_count, length=450)
        progresstext = tk.ttk.Label(info_frame, text=f"0/{item_count}")
        progressbar.grid(row=10, column=0, columnspan=6)
        progresstext.grid(row=10, column=6, columnspan=2)
        title = book.get_infos()["title"]
        try:
            os.mkdir(title)
        except FileExistsError:
            pass
        vols = book.get_volumes()
        for i, j in enumerate(book.get_chap_ids(), start=1):
            chap = FanQieNovelSpider.FanQieChapter(j, cookie=cookie_var.get())
            progressbar["value"] = i + 1
            progressbar.update()
            progresstext.config(text=f"{i + 1}/{item_count}")
            progresstext.update()
            path = ""
            if vols:
                for k in vols:
                    if k[1] <= i <= k[2]:
                        path = os.path.join(title, k[0], chap.get_title() + ".txt")
                        try:
                            os.mkdir(os.path.join(title, k[0]))
                        except FileExistsError:
                            pass
            else:
                path = os.path.join(title, chap.get_title() + ".txt")
            with open(path, "w", encoding="utf-8") as f:
                f.write(chap.get_paras().join_paras())
        tk.messagebox.showinfo("书籍下载", "下载完成!")
        progressbar.destroy()
        progresstext.destroy()

    return download


def read(book):
    def read():
        for widget in contents_frame.winfo_children():
            widget.destroy()
        chap_list = book.get_chap_ids()
        chap_titles = book.get_chap_titles()
        tk.ttk.Label(contents_frame, text=f"共 {len(chap_list)} 章").pack(side=tk.TOP, fill=tk.BOTH)
        contents = tk.ttk.Frame(contents_frame)
        contents_tree = tk.ttk.Treeview(contents, selectmode=tk.BROWSE, show="tree")
        scrollbar = tk.ttk.Scrollbar(contents, orient=tk.VERTICAL, command=contents_tree.yview)
        vols = book.get_volumes()
        vols_tree = {}
        for i, j in enumerate(chap_list, start=1):
            if vols:
                for v, k in enumerate(vols):
                    if k[1] <= i <= k[2]:
                        if vols_tree.get(k[0]) is None:
                            vols_tree[k[0]] = contents_tree.insert(
                                "", v, k[0], text=k[0], values=(k[0],)
                            )
                        contents_tree.insert(
                            vols_tree[k[0]],
                            i - k[1],
                            j,
                            text=chap_titles[i - 1],
                            values=(j,),
                        )
            else:
                contents_tree.insert("", i - 1, j, text=chap_titles[i - 1], values=(j,))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        contents_tree.config(yscrollcommand=scrollbar.set)
        contents_tree.pack(side=tk.TOP, fill=tk.BOTH)
        contents.pack(side=tk.TOP, fill=tk.BOTH)

        def read():
            read_chap(contents_tree.selection()[0])

        read_button = tk.ttk.Button(contents_frame, text="阅读", command=read, state=tk.DISABLED)
        read_button.pack(side=tk.TOP, fill=tk.X)

        def select(e):
            if len(contents_tree.get_children(contents_tree.selection()[0])) == 0:
                read_button.config(state=tk.ACTIVE)
            else:
                read_button.config(state=tk.DISABLED)

        contents_tree.bind("<<TreeviewSelect>>", select)
        pager.select(5)

    return read


def read_chap(chap):
    for widget in text_frame.winfo_children():
        widget.destroy()
    chapter = FanQieNovelSpider.FanQieChapter(chap, cookie_var.get())
    tk.ttk.Label(text_frame, text=chapter.get_title()).pack(side=tk.TOP, fill=tk.BOTH)
    text = tk.scrolledtext.ScrolledText(text_frame)
    text.pack(side=tk.TOP, fill=tk.BOTH)
    text.insert("0.0", chapter.get_paras().join_paras())
    text.config(state=tk.DISABLED)

    def previous():
        chap_list = FanQieNovelSpider.FanQieBook(chapter.get_book()).get_chap_ids()
        i = chap_list.index(int(chap)) - 1
        if i == -1:
            return
        read_chap(chap_list[i])

    def next():
        chap_list = FanQieNovelSpider.FanQieBook(chapter.get_book()).get_chap_ids()
        i = chap_list.index(int(chap)) + 1
        if i == -1:
            return
        read_chap(chap_list[i])

    tk.ttk.Button(text_frame, text="上一章", command=previous, bootstyle=ttkbootstrap.OUTLINE).pack(
        side=tk.LEFT
    )
    tk.ttk.Button(text_frame, text="下一章", command=next, bootstyle=ttkbootstrap.OUTLINE).pack(
        side=tk.RIGHT
    )

    pager.select(6)


def load_books(row_count=6):
    global current_page
    current_page += 1
    searcher = FanQieNovelSpider.FanQieBookSearcher()
    search_results = searcher.filters(
        current_page - 1,
        gender.get(),
        category_ids[category.get()],
        creation_status.get(),
        word_count.get(),
        sort.get(),
    )
    stop.clear()
    for widget in main_frame.winfo_children():
        widget.destroy()
    book_covers.clear()
    for n, i in enumerate(search_results["book_list"]):
        if stop.isSet():
            stop.clear()
            return
        response = requests.get(url=i["thumb_url"], headers=headers)
        image = Image.open(BytesIO(response.content)).resize((100, 150))
        cover = ImageTk.PhotoImage(image)
        book_covers.append(cover)
        tk.Button(
            main_frame, image=cover, command=view_book(i["book_id"]), bd=0, highlightthickness=0
        ).grid(row=int(n / row_count), column=n % row_count)
        if search_results["has_more"]:
            main_canvas.config(scrollregion=(0, 0, 680, int(n / row_count) * 240 + 30))
        else:
            main_canvas.config(scrollregion=(0, 0, 680, int(n / row_count) * 240))

    def load():
        if load_type:
            threading.Thread(target=sload_books, daemon=True).start()
        else:
            threading.Thread(target=load_books, daemon=True).start()

    if search_results["has_more"]:
        tk.ttk.Button(
            main_frame,
            text=f"加载更多（当前第 {current_page} 页）",
            command=load,
            width=80,
        ).grid(
            row=int(len(search_results["book_list"]) - 1 / row_count) + 1,
            column=0,
            columnspan=row_count,
        )


def sload_books(row_count=6):
    global current_page
    current_page += 1
    searcher = FanQieNovelSpider.FanQieBookSearcher()
    search_results = searcher.search(
        query_word.get(),
        current_page - 1,
        ssort.get(),
        update_time.get(),
        sword_count.get(),
        screation_status.get(),
    )
    stop.clear()
    for widget in main_frame.winfo_children():
        widget.destroy()
    book_covers.clear()
    for n, i in enumerate(search_results["book_list"]):
        if stop.isSet():
            stop.clear()
            return
        response = requests.get(url=i["thumb_url"], headers=headers)
        image = Image.open(BytesIO(response.content)).resize((100, 150))
        cover = ImageTk.PhotoImage(image)
        book_covers.append(cover)
        tk.Button(
            main_frame, image=cover, command=view_book(i["book_id"]), bd=0, highlightthickness=0
        ).grid(row=int(n / row_count), column=n % row_count)
        if current_page / 10 < search_results["total_count"]:
            main_canvas.config(scrollregion=(0, 0, 680, int(n / row_count) * 240 + 30))
        else:
            main_canvas.config(scrollregion=(0, 0, 680, int(n / row_count) * 240))

    def load():
        if load_type:
            threading.Thread(target=sload_books, daemon=True).start()
        else:
            threading.Thread(target=load_books, daemon=True).start()

    if current_page / 10 < search_results["total_count"]:
        tk.ttk.Button(
            main_frame,
            text=f"加载更多（当前第 {current_page} 页）",
            command=load,
            width=80,
        ).grid(
            row=int(len(search_results["book_list"]) - 1 / row_count) + 1,
            column=0,
            columnspan=row_count,
        )


main_canvas.create_window(
    (
        0,
        0,
    ),
    window=main_frame,
    anchor="nw",
    tags="frame",
)
main_canvas.config(highlightthickness=0)
main_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
main_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
main_canvas.config(yscrollcommand=main_scrollbar.set)
pager.add(main_root_frame, text="主页")
filler_frame = tk.ttk.Frame(pager)
gender = tk.IntVar(value=-1)
category = tk.StringVar(value="全部")
category_ids = dict(
    zip(
        ["全部"] + [i["name"] for i in FanQieNovelSpider.FanQieBookSearcher().get_category_list()],
        [-1]
        + [i["category_id"] for i in FanQieNovelSpider.FanQieBookSearcher().get_category_list()],
    )
)
creation_status = tk.IntVar(value=-1)
word_count = tk.IntVar(value=-1)
sort = tk.IntVar(value=0)
book_id_var = tk.IntVar()
chapter_id_var = tk.IntVar()
tk.ttk.Label(filler_frame, text="读者：").grid(row=0, column=0)
tk.ttk.Radiobutton(filler_frame, variable=gender, text="全部", value=-1).grid(row=0, column=1)
tk.ttk.Radiobutton(filler_frame, variable=gender, text="男生", value=1).grid(row=0, column=2)
tk.ttk.Radiobutton(filler_frame, variable=gender, text="女生", value=0).grid(row=0, column=3)
tk.ttk.Label(filler_frame, text="分类：").grid(row=1, column=0)
category_select = tk.ttk.Combobox(filler_frame, textvariable=category, state="readonly")
category_select["values"] = list(category_ids.keys())
category_select.grid(row=1, column=1, columnspan=3)
tk.ttk.Label(filler_frame, text="状态：").grid(row=2, column=0)
tk.ttk.Radiobutton(filler_frame, variable=creation_status, text="全部", value=-1).grid(
    row=2, column=1
)
tk.ttk.Radiobutton(filler_frame, variable=creation_status, text="已完结", value=0).grid(
    row=2, column=2
)
tk.ttk.Radiobutton(filler_frame, variable=creation_status, text="连载中", value=1).grid(
    row=2, column=3
)
tk.ttk.Label(filler_frame, text="字数：").grid(row=3, column=0)
tk.ttk.Radiobutton(filler_frame, variable=word_count, text="全部", value=-1).grid(row=3, column=1)
tk.ttk.Radiobutton(filler_frame, variable=word_count, text="30万以下", value=0).grid(
    row=3, column=2
)
tk.ttk.Radiobutton(filler_frame, variable=word_count, text="30-50万", value=1).grid(row=3, column=3)
tk.ttk.Radiobutton(filler_frame, variable=word_count, text="50-100万", value=2).grid(
    row=3, column=4
)
tk.ttk.Radiobutton(filler_frame, variable=word_count, text="100-200万", value=3).grid(
    row=3, column=5
)
tk.ttk.Radiobutton(filler_frame, variable=word_count, text="200万以上", value=4).grid(
    row=3, column=6
)
tk.ttk.Label(filler_frame, text="排序：").grid(row=4, column=0)
tk.ttk.Radiobutton(filler_frame, variable=sort, text="最热", value=0).grid(row=4, column=1)
tk.ttk.Radiobutton(filler_frame, variable=sort, text="最新", value=1).grid(row=4, column=2)
tk.ttk.Radiobutton(filler_frame, variable=sort, text="字数", value=2).grid(row=4, column=3)


def apply():
    global current_page
    global load_type
    load_type = False
    stop.set()
    current_page = 0
    threading.Thread(target=load_books, daemon=True).start()
    pager.select(1)


def sapply():
    global current_page
    global load_type
    if query_word.get().strip() == "":
        return
    load_type = True
    stop.set()
    current_page = 0
    threading.Thread(target=sload_books, daemon=True).start()
    pager.select(1)


tk.ttk.Button(filler_frame, text="应用", command=apply, bootstyle=ttkbootstrap.OUTLINE).grid(
    row=5, column=2
)
pager.add(filler_frame, text="筛选设置")
search_frame = tk.ttk.Frame(pager)
ssort = tk.IntVar(value=0)
sword_count = tk.IntVar(value=127)
update_time = tk.IntVar(value=127)
screation_status = tk.IntVar(value=127)
query_word = tk.StringVar()
tk.ttk.Label(search_frame, text="排序：").grid(row=0, column=0)
tk.ttk.Radiobutton(search_frame, variable=ssort, text="相关", value=0).grid(row=0, column=1)
tk.ttk.Radiobutton(search_frame, variable=ssort, text="最热", value=1).grid(row=0, column=2)
tk.ttk.Radiobutton(search_frame, variable=ssort, text="最新", value=2).grid(row=0, column=3)
tk.ttk.Label(search_frame, text="更新时间：").grid(row=1, column=0)
tk.ttk.Radiobutton(search_frame, variable=update_time, text="全部", value=127).grid(row=1, column=1)
tk.ttk.Radiobutton(search_frame, variable=update_time, text="过去三十分钟", value=0).grid(
    row=1, column=2
)
tk.ttk.Radiobutton(search_frame, variable=update_time, text="今天", value=1).grid(row=1, column=3)
tk.ttk.Radiobutton(search_frame, variable=update_time, text="本周", value=2).grid(row=1, column=4)
tk.ttk.Radiobutton(search_frame, variable=update_time, text="本月", value=3).grid(row=1, column=5)
tk.ttk.Radiobutton(search_frame, variable=update_time, text="今年", value=4).grid(row=1, column=6)
tk.ttk.Label(search_frame, text="字数：").grid(row=2, column=0)
tk.ttk.Radiobutton(search_frame, variable=sword_count, text="全部", value=127).grid(row=2, column=1)
tk.ttk.Radiobutton(search_frame, variable=sword_count, text="30万以下", value=0).grid(
    row=2, column=2
)
tk.ttk.Radiobutton(search_frame, variable=sword_count, text="30-50万", value=1).grid(
    row=2, column=3
)
tk.ttk.Radiobutton(search_frame, variable=sword_count, text="50-100万", value=2).grid(
    row=2, column=4
)
tk.ttk.Radiobutton(search_frame, variable=sword_count, text="100-200万", value=3).grid(
    row=2, column=5
)
tk.ttk.Radiobutton(search_frame, variable=sword_count, text="200万以上", value=4).grid(
    row=2, column=6
)
tk.ttk.Label(search_frame, text="状态：").grid(row=3, column=0)
tk.ttk.Radiobutton(search_frame, variable=screation_status, text="全部", value=127).grid(
    row=3, column=1
)
tk.ttk.Radiobutton(search_frame, variable=screation_status, text="已完结", value=0).grid(
    row=3, column=2
)
tk.ttk.Radiobutton(search_frame, variable=screation_status, text="连载中", value=1).grid(
    row=3, column=3
)
tk.ttk.Label(search_frame, text="关键词：").grid(row=4, column=0)
tk.ttk.Entry(search_frame, textvariable=query_word, width=30).grid(row=4, column=1, columnspan=3)
tk.ttk.Button(search_frame, text="应用", command=sapply, bootstyle=ttkbootstrap.OUTLINE).grid(
    row=5, column=2
)
pager.add(search_frame, text="搜索设置（无法使用）")
info_frame = tk.ttk.Frame(pager)
tk.ttk.Label(
    info_frame, text="你还没有选择书籍o((>ω< ))o", font=("Microsoft YaHei UI", 30, "bold")
).pack(side=tk.TOP)
pager.add(info_frame, text="书籍信息")
contents_frame = tk.ttk.Frame(pager)
tk.ttk.Label(
    contents_frame, text="你还没有选择阅读书籍o((>ω< ))o", font=("Microsoft YaHei UI", 30, "bold")
).pack(side=tk.TOP)
pager.add(contents_frame, text="书籍目录")
text_frame = tk.ttk.Frame(pager)
tk.ttk.Label(
    text_frame, text="你还没有选择阅读章节o((>ω< ))o", font=("Microsoft YaHei UI", 30, "bold")
).pack(side=tk.TOP)
pager.add(text_frame, text="阅读书籍")
jump_frame = tk.ttk.Frame(pager)
book_id_frame = tk.ttk.Frame(jump_frame)
tk.ttk.Label(book_id_frame, text="书籍 ID：").pack(side=tk.LEFT)
tk.ttk.Spinbox(book_id_frame,textvariable=book_id_var).pack(side=tk.LEFT)
tk.ttk.Button(book_id_frame,text="跳转",command=lambda:view_book(book_id_var.get())()).pack(side=tk.LEFT)
book_id_frame.pack()
chapter_id_frame = tk.ttk.Frame(jump_frame)
tk.ttk.Label(chapter_id_frame, text="章节 ID：").pack(side=tk.LEFT)
tk.ttk.Spinbox(chapter_id_frame,textvariable=chapter_id_var).pack(side=tk.LEFT)
tk.ttk.Button(chapter_id_frame,text="跳转",command=lambda:read_chap(chapter_id_var.get())).pack(side=tk.LEFT)
chapter_id_frame.pack()
pager.add(jump_frame, text="跳转")

pager.select(1)

if os.path.isfile("./config"):
    with open("./config") as f:
        cookie = f.read()
        if cookie == "":
            pager.select(0)
        cookie_var.set(cookie)
else:
    pager.select(0)

threading.Thread(target=load_books, daemon=True).start()
window.mainloop()
