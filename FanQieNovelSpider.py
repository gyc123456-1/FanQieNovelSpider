import json
import re
import typing
import typing_extensions
import requests
from lxml import etree


class Paragraphs(list):
    """
    段落列表对象
    """

    def join_paras(self: typing_extensions.Self, para_starts: str = "　　") -> str:
        """
        连接段落
        :param para_starts: 段落开头
        :return: 连接后的段落
        """
        text = ""
        for para in self:
            text += para_starts + para + "\n"
        return text[:-1]


class BookError(Exception): ...


class FanQieChapDecoder:
    """
    番茄免费小说章节字符解密器
    """

    CODE_ST: int = 0xE3E8
    CODE_ED: int = 0xE55B
    charset: typing.List[str] = [
        "D",
        "在",
        "主",
        "特",
        "家",
        "军",
        "然",
        "表",
        "场",
        "4",
        "要",
        "只",
        "v",
        "和",
        "?",
        "6",
        "别",
        "还",
        "g",
        "现",
        "儿",
        "岁",
        "?",
        "?",
        "此",
        "象",
        "月",
        "3",
        "出",
        "战",
        "工",
        "相",
        "o",
        "男",
        "首",
        "失",
        "世",
        "F",
        "都",
        "平",
        "文",
        "什",
        "V",
        "O",
        "将",
        "真",
        "T",
        "那",
        "当",
        "?",
        "会",
        "立",
        "些",
        "u",
        "是",
        "十",
        "张",
        "学",
        "气",
        "大",
        "爱",
        "两",
        "命",
        "全",
        "后",
        "东",
        "性",
        "通",
        "被",
        "1",
        "它",
        "乐",
        "接",
        "而",
        "感",
        "车",
        "山",
        "公",
        "了",
        "常",
        "以",
        "何",
        "可",
        "话",
        "先",
        "p",
        "i",
        "叫",
        "轻",
        "M",
        "士",
        "w",
        "着",
        "变",
        "尔",
        "快",
        "l",
        "个",
        "说",
        "少",
        "色",
        "里",
        "安",
        "花",
        "远",
        "7",
        "难",
        "师",
        "放",
        "t",
        "报",
        "认",
        "面",
        "道",
        "S",
        "?",
        "克",
        "地",
        "度",
        "I",
        "好",
        "机",
        "U",
        "民",
        "写",
        "把",
        "万",
        "同",
        "水",
        "新",
        "没",
        "书",
        "电",
        "吃",
        "像",
        "斯",
        "5",
        "为",
        "y",
        "白",
        "几",
        "日",
        "教",
        "看",
        "但",
        "第",
        "加",
        "候",
        "作",
        "上",
        "拉",
        "住",
        "有",
        "法",
        "r",
        "事",
        "应",
        "位",
        "利",
        "你",
        "声",
        "身",
        "国",
        "问",
        "马",
        "女",
        "他",
        "Y",
        "比",
        "父",
        "x",
        "A",
        "H",
        "N",
        "s",
        "X",
        "边",
        "美",
        "对",
        "所",
        "金",
        "活",
        "回",
        "意",
        "到",
        "z",
        "从",
        "j",
        "知",
        "又",
        "内",
        "因",
        "点",
        "Q",
        "三",
        "定",
        "8",
        "R",
        "b",
        "正",
        "或",
        "夫",
        "向",
        "德",
        "听",
        "更",
        "?",
        "得",
        "告",
        "并",
        "本",
        "q",
        "过",
        "记",
        "L",
        "让",
        "打",
        "f",
        "人",
        "就",
        "者",
        "去",
        "原",
        "满",
        "体",
        "做",
        "经",
        "K",
        "走",
        "如",
        "孩",
        "c",
        "G",
        "给",
        "使",
        "物",
        "?",
        "最",
        "笑",
        "部",
        "?",
        "员",
        "等",
        "受",
        "k",
        "行",
        "一",
        "条",
        "果",
        "动",
        "光",
        "门",
        "头",
        "见",
        "往",
        "自",
        "解",
        "成",
        "处",
        "天",
        "能",
        "于",
        "名",
        "其",
        "发",
        "总",
        "母",
        "的",
        "死",
        "手",
        "入",
        "路",
        "进",
        "心",
        "来",
        "h",
        "时",
        "力",
        "多",
        "开",
        "己",
        "许",
        "d",
        "至",
        "由",
        "很",
        "界",
        "n",
        "小",
        "与",
        "Z",
        "想",
        "代",
        "么",
        "分",
        "生",
        "口",
        "再",
        "妈",
        "望",
        "次",
        "西",
        "风",
        "种",
        "带",
        "J",
        "?",
        "实",
        "情",
        "才",
        "这",
        "?",
        "E",
        "我",
        "神",
        "格",
        "长",
        "觉",
        "间",
        "年",
        "眼",
        "无",
        "不",
        "亲",
        "关",
        "结",
        "0",
        "友",
        "信",
        "下",
        "却",
        "重",
        "己",
        "老",
        "2",
        "音",
        "字",
        "m",
        "呢",
        "明",
        "之",
        "前",
        "高",
        "P",
        "B",
        "目",
        "太",
        "e",
        "9",
        "起",
        "稜",
        "她",
        "也",
        "W",
        "用",
        "方",
        "子",
        "英",
        "每",
        "理",
        "便",
        "西",
        "数",
        "期",
        "中",
        "C",
        "外",
        "样",
        "a",
        "海",
        "们",
        "任",
    ]

    def interpreter(self: typing_extensions.Self, cc: int) -> str:
        """
        解密单个加密字符
        （原字符减去e338获取到另一套字体的该编码字符）
        :param cc: 原字符的 Unicode 码位
        :return: 解密后的内容
        """
        if self.CODE_ST <= cc <= self.CODE_ED:
            bias = cc - self.CODE_ST
            if self.charset[bias] == "?":  # 特殊处理
                return chr(cc)
            return self.charset[bias]
        return chr(cc)

    def decode(self: typing_extensions.Self, content: str) -> str:
        """
        解密加密字符串
        :param content: 要解密的字符串
        :return: 解密后的内容
        """
        para = ""
        for char in content:
            cc = ord(char)
            para += self.interpreter(cc)
        return para


class FanQieChapter:
    """
    番茄免费小说章节相关爬虫
    """

    headers: typing.Dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        "Cookie": "",
    }

    def __init__(
        self: typing_extensions.Self, chap_id: typing.Union[int, str], cookie: str = ""
    ) -> None:
        """
        初始化章节对象
        :param chap_id: 章节 ID
        :param cookie: 账号 Cookie, 不填则只能爬取完整的前十章和后续章节的开头
        """
        self.chap_id: int = int(chap_id)
        self.chapter_url: str = "https://fanqienovel.com/reader/" + str(chap_id)
        self.headers["Cookie"] = cookie
        self.decoder = FanQieChapDecoder()

    def get_api_data(self):
        """
        用于获取和原来 api 格式一样的数据
        :return: api 数据
        """
        response = requests.get(url=self.chapter_url, headers=self.headers)
        tree = etree.HTML(response.text)
        js = tree.xpath("//html/body/script[1]/text()")[0]
        api_data = re.search(r"window\.__INITIAL_STATE__\s*=\s*(\{.*?});", js, re.DOTALL).group(1)
        api_data = {"data": json.loads(api_data)["reader"]}
        return api_data

    def get_title(self: typing_extensions.Self) -> str:
        """
        获取章节标题
        :return: 章节标题
        """
        json_obj = self.get_api_data()
        title = json_obj["data"]["chapterData"]["title"]
        return title

    def get_first_time(self: typing_extensions.Self) -> int:
        """
        获取章节首次发布时间
        :return: 章节首次发布时间
        """
        response = requests.get(url=self.chapter_url, headers=self.headers)
        tree = etree.HTML(response.text)
        time = json.loads(tree.xpath("//html/head/script[2]/text()")[0])["upDate"]
        return time.replace("T", " ")

    def get_modified_time(self: typing_extensions.Self) -> int:
        """
        获取章节最后修改时间
        :return: 章节最后修改时间
        """
        response = requests.get(url=self.chapter_url, headers=self.headers)
        tree = etree.HTML(response.text)
        time = json.loads(tree.xpath("//html/head/script[1]/text()")[0])["dateModified"]
        return time.replace("T", " ")

    def get_paras(self: typing_extensions.Self) -> Paragraphs:
        """
        获取段落列表
        :return: 段落列表
        """
        json_obj = self.get_api_data()
        content = json_obj["data"]["chapterData"]["content"]
        tree = etree.HTML(content)
        content_tags = tree.xpath("//text()")
        content = []
        for content_tag in content_tags:
            content.append(self.decoder.decode(content_tag))
        return Paragraphs(content)

    def get_book(self: typing_extensions.Self) -> int:
        """
        获取章节所属书籍的 ID
        :return: 书籍 ID
        """
        json_obj = self.get_api_data()
        return int(json_obj["data"]["chapterData"]["bookId"])

    def get_word_number(self: typing_extensions.Self) -> int:
        """
        获取章节字数
        :return: 章节字数
        """
        json_obj = self.get_api_data()
        return int(json_obj["data"]["chapterData"]["chapterWordNumber"])


class FanQieBook:
    """
    番茄免费小说书籍相关爬虫
    """

    headers: typing.Dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
    }

    def __init__(self: typing_extensions.Self, book_id: typing.Union[int, str]) -> None:
        """
        初始化书籍
        :param book_id: 书籍 ID
        """
        self.book_id: int = int(book_id)
        self.book_url: str = "https://fanqienovel.com/page/" + str(book_id)

    def get_chap_ids(self: typing_extensions.Self) -> typing.List[int]:
        """
        获取书籍各章节的 ID
        :return: 章节 ID 列表
        """
        response = requests.get(url=self.book_url, headers=self.headers)
        tree = etree.HTML(response.text)
        try:
            chaps = tree.xpath('//div[@class="chapter-item"]/a[@class="chapter-item-title"]/@href')
        except AttributeError:
            raise BookError("过段时间后重试")
        chap_ids = [int(i.split("/")[-1]) for i in chaps]
        return chap_ids

    def get_chap_titles(self: typing_extensions.Self) -> typing.List[str]:
        """
        获取书籍各章节的标题
        :return: 章节标题列表
        """
        response = requests.get(url=self.book_url, headers=self.headers)
        tree = etree.HTML(response.text)
        try:
            chaps = tree.xpath('//div[@class="chapter-item"]/a[@class="chapter-item-title"]/text()')
        except AttributeError:
            raise BookError("过段时间后重试")
        return chaps

    def get_infos(self: typing_extensions.Self) -> dict:
        """
        获取书籍大致信息
        :return: 信息字典
        """
        info = {}
        response = requests.get(url=self.book_url, headers=self.headers)
        tree = etree.HTML(response.text)
        info["title"] = tree.xpath('//div[@class="info-name"]/h1/text()')[0]
        info["author"] = tree.xpath('//span[@class="author-name-text"]/text()')[0]
        info["cover"] = json.loads(tree.xpath("//html/head/script[1]/text()")[0])["image"][0]
        info["intro"] = tree.xpath('//div[@class="page-abstract-content"]/p/text()')[0]
        info["labels"] = tree.xpath('//div[@class="info-label"]/span/text()')
        info["word_count"] = " ".join(tree.xpath('//div[@class="info-count-word"]/span/text()'))
        info["last_update_time"] = tree.xpath('//span[@class="info-last-time"]/text()')[0]
        return info

    def get_volumes(self: typing_extensions.Self) -> typing.List[typing.Tuple[str, int, int]]:
        """
        获取分卷
        :return: [[分卷名, 分卷起始章节, 分卷结束章节], ...]
        """
        volumes = {}
        response = requests.get(url=self.book_url, headers=self.headers)
        tree = etree.HTML(response.text)
        volume_info = tree.xpath('//div[@class="volume volume_first"]/text()')
        volumes[volume_info[0]] = int(volume_info[2])
        volume_info = tree.xpath('//div[@class="volume"]/text()')
        temp_info = []
        for i, j in enumerate(volume_info):
            if i % 4 == 0:
                temp_info.append(j)
            elif i % 4 == 2:
                temp_info.append(int(j))
            elif i % 4 == 3:
                volumes[temp_info[0]] = temp_info[1]
                temp_info = []
        vols_list = []
        count = 0
        for i, j in zip(volumes.keys(), volumes.values()):
            vols_list.append((i, count + 1, count + j))
            count += j
        if len(vols_list) == 1 and vols_list[0][0] == "第一卷":
            return []
        return vols_list


class FanQieBookSearcher:
    """
    番茄免费小说搜索书籍相关爬虫
    """

    headers: typing.Dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
    }

    def filters(
        self: typing_extensions.Self,
        page: int = 0,
        gender: int = -1,
        category_id: int = -1,
        creation_status: int = -1,
        word_count: int = -1,
        sort: int = -1,
    ) -> dict:
        """
        通过信息筛选书籍
        :param page: 结果第几页，从 0 开始
        :param gender: 读者, 全部-1 男生1 女生0
        :param category_id: 分类, 全部-1 对应分类 ID
        :param creation_status: 状态, 全部-1 已完结0 连载中1
        :param word_count: 字数, 全部-1 30万以下0 30-50万1 50-100万2 100-200万3 200万以上4
        :param sort: 排序, 最热0 最新1 字数2
        :return: 筛选结果
        """
        api_url = f"https://fanqienovel.com/api/author/library/book_list/v0/?page_count=18&page_index={page}&gender={gender}&category_id={category_id}&creation_status={creation_status}&word_count={word_count}&book_type=-1&sort={sort}"
        response = requests.get(url=api_url, headers=self.headers)
        data = response.json()["data"]
        return data

    def search(
        self: typing_extensions.Self,
        query_word: str,
        page: int = 0,
        query_type: int = 0,
        update_time: int = 127,
        word_count: int = 127,
        creation_status: int = 127,
    ) -> dict:
        """
        通过关键字搜索书籍（无法使用）
        :param query_word: 关键字
        :param page: 结果第几页，从 0 开始
        :param query_type: 排序, 相关0 最新1 最热2
        :param update_time: 更新时间, 全部127 过去三十分钟0 今天1 本周2 本月3 今年4
        :param word_count: 字数, 全部127 30万以下0 30-50万1 50-100万2 100-200万3 200万以上4
        :param creation_status: 状态, 全部127 已完结0 连载中1
        :return: 搜索结果
        """
        api_url = f"https://fanqienovel.com/api/author/search/search_book/v1?filter={update_time}%2C{word_count}%2C{creation_status}%2C127&page_count=10&page_index={page}&query_type={query_type}&query_word={query_word}"
        response = requests.get(url=api_url, headers=self.headers)
        data = {
            "book_list": response.json()["data"]["search_book_data_list"],
            "total_count": response.json()["data"]["total_count"],
        }
        return data

    def get_category_list(self: typing_extensions.Self, gender: int = -1) -> list:
        """
        获取章节信息列表
        :param gender:  读者, 全部-1 男生1 女生0
        :return: 章节信息列表（图标为 png 格式）
        """
        api_url = f"https://fanqienovel.com/api/author/book/category_list/v0/?gender={gender}"
        response = requests.get(url=api_url, headers=self.headers)
        return response.json()["data"]
