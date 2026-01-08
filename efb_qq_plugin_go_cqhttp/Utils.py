import logging
import re
import tempfile
import urllib.parse
from typing import IO, Optional, Union

import httpx
import pilk
import pydub
from ehforwarderbot import Message, coordinator

logger = logging.getLogger(__name__)

# created by JogleLew and jqqqqqqqqqq, optimized based on Tim's emoji support, updated by xzsk2 to mobileqq v8.8.11
qq_emoji_list = {
    0: "😮",
    1: "😣",
    2: "😍",
    3: "😳",
    4: "😎",
    5: "😭",
    6: "☺️",
    7: "😷",
    8: "😴",
    9: "😭",
    10: "😰",
    11: "😡",
    12: "😝",
    13: "😃",
    14: "🙂",
    15: "🙁",
    16: "🤓",
    17: "[Empty]",
    18: "😤",
    19: "😨",
    20: "😏",
    21: "😊",
    22: "🙄",
    23: "😕",
    24: "🤤",
    25: "😪",
    26: "😨",
    27: "😓",
    28: "😬",
    29: "🤑",
    30: "✊",
    31: "😤",
    32: "🤔",
    33: "🤐",
    34: "😵",
    35: "😩",
    36: "💣",
    37: "💀",
    38: "🔨",
    39: "👋",
    40: "[Empty]",
    41: "😮",
    42: "💑",
    43: "🕺",
    44: "[Empty]",
    45: "[Empty]",
    46: "🐷",
    47: "[Empty]",
    48: "[Empty]",
    49: "🤷",
    50: "[Empty]",
    51: "[Empty]",
    52: "[Empty]",
    53: "🎂",
    54: "⚡",
    55: "💣",
    56: "🔪",
    57: "⚽️",
    58: "[Empty]",
    59: "💩",
    60: "☕️",
    61: "🍚",
    62: "[Empty]",
    63: "🌹",
    64: "🥀",
    65: "[Empty]",
    66: "❤️",
    67: "💔️",
    68: "[Empty]",
    69: "🎁",
    70: "[Empty]",
    71: "[Empty]",
    72: "[Empty]",
    73: "[Empty]",
    74: "🌞️",
    75: "🌃",
    76: "👍",
    77: "👎",
    78: "🤝",
    79: "✌️",
    80: "[Empty]",
    81: "[Empty]",
    82: "[Empty]",
    83: "[Empty]",
    84: "[Empty]",
    85: "🥰",
    86: "[怄火]",
    87: "[Empty]",
    88: "[Empty]",
    89: "🍉",
    90: "[Empty]",
    91: "[Empty]",
    92: "[Empty]",
    93: "[Empty]",
    94: "[Empty]",
    95: "[Empty]",
    96: "😅",
    97: "[擦汗]",
    98: "[抠鼻]",
    99: "👏",
    100: "[糗大了]",
    101: "😏",
    102: "😏",
    103: "😏",
    104: "🥱",
    105: "[鄙视]",
    106: "😭",
    107: "😭",
    108: "[阴险]",
    109: "😚",
    110: "🙀",
    111: "[可怜]",
    112: "🔪",
    113: "🍺",
    114: "🏀",
    115: "🏓",
    116: "❤️",
    117: "🐞",
    118: "[抱拳]",
    119: "[勾引]",
    120: "✊",
    121: "[差劲]",
    122: "🤟",
    123: "🚫",
    124: "👌",
    125: "[转圈]",
    126: "[磕头]",
    127: "[回头]",
    128: "[跳绳]",
    129: "👋",
    130: "[激动]",
    131: "[街舞]",
    132: "😘",
    133: "[左太极]",
    134: "[右太极]",
    135: "[Empty]",
    136: "[双喜]",
    137: "🧨",
    138: "🏮",
    139: "💰",
    140: "[K歌]",
    141: "🛍️",
    142: "📧",
    143: "[帅]",
    144: "👏",
    145: "🙏",
    146: "[爆筋]",
    147: "🍭",
    148: "🍼",
    149: "[下面]",
    150: "🍌",
    151: "🛩",
    152: "🚗",
    153: "🚅",
    154: "[车厢]",
    155: "[高铁右车头]",
    156: "🌥",
    157: "下雨",
    158: "💵",
    159: "🐼",
    160: "💡",
    161: "[风车]",
    162: "⏰",
    163: "🌂",
    164: "[彩球]",
    165: "💍",
    166: "🛋",
    167: "[纸巾]",
    168: "💊",
    169: "🔫",
    170: "🐸",
    171: "🍵",
    172: "[眨眼睛]",
    173: "😭",
    174: "[无奈]",
    175: "[卖萌]",
    176: "[小纠结]",
    177: "[喷血]",
    178: "[斜眼笑]",
    179: "[doge]",
    180: "[惊喜]",
    181: "[骚扰]",
    182: "😹",
    183: "[我最美]",
    184: "🦀",
    185: "[羊驼]",
    186: "[Empty]",
    187: "👻",
    188: "🥚",
    189: "[Empty]",
    190: "🌼",
    191: "[Empty]",
    192: "🧧",
    193: "😄",
    194: "😞",
    195: "[Empty]",
    196: "[Empty]",
    197: "[冷漠]",
    198: "[呃]",
    199: "👍",
    200: "👋",
    201: "👍",
    202: "[无聊]",
    203: "[托脸]",
    204: "[吃]",
    205: "💐",
    206: "😨",
    207: "[花痴]",
    208: "[小样儿]",
    209: "[Empty]",
    210: "😭",
    211: "[我不看]",
    212: "[托腮]",
    213: "[Empty]",
    214: "😙",
    215: "[糊脸]",
    216: "[拍头]",
    217: "[扯一扯]",
    218: "[舔一舔]",
    219: "[蹭一蹭]",
    220: "[拽炸天]",
    221: "[顶呱呱]",
    222: "🤗",
    223: "[暴击]",
    224: "🔫",
    225: "[撩一撩]",
    226: "[拍桌]",
    227: "👏",
    228: "[恭喜]",
    229: "🍻",
    230: "[嘲讽]",
    231: "[哼]",
    232: "[佛系]",
    233: "[掐一掐]",
    234: "😮",
    235: "[颤抖]",
    236: "[啃头]",
    237: "[偷看]",
    238: "[扇脸]",
    239: "[原谅]",
    240: "[喷脸]",
    241: "🎂",
    242: "[头撞击]",
    243: "[甩头]",
    244: "[扔狗]",
    245: "[加油必胜]",
    246: "[加油抱抱]",
    247: "[口罩护体]",
    248: "[Empty]",
    249: "[Empty]",
    250: "[Empty]",
    251: "[Empty]",
    252: "[Empty]",
    253: "[Empty]",
    254: "[Empty]",
    255: "[Empty]",
    256: "😲",
    257: "😟",
    258: "😍",
    259: "😳",
    260: "[搬砖中]",
    261: "[忙到飞起]",
    262: "[脑阔疼]",
    263: "[沧桑]",
    264: "[捂脸]",
    265: "[辣眼睛]",
    266: "[哦哟]",
    267: "[头秃]",
    268: "[问号脸]",
    269: "[暗中观察]",
    270: "[emm]",
    271: "[吃瓜]",
    272: "[呵呵哒]",
    273: "[我酸了]",
    274: "[太南了]",
    275: "[Empty]",
    276: "[辣椒酱]",
    277: "[汪汪]",
    278: "[汗]",
    279: "[打脸]",
    280: "[击掌]",
    281: "[无眼笑]",
    282: "[敬礼]",
    283: "[狂笑]",
    284: "[面无表情]",
    285: "[摸鱼]",
    286: "[魔鬼笑]",
    287: "[哦]",
    288: "[请]",
    289: "[睁眼]",
    290: "[敲开心]",
    291: "[震惊]",
    292: "[让我康康]",
    293: "[摸锦鲤]",
    294: "[期待]",
    295: "[拿到红包]",
    296: "[真好]",
    297: "[拜谢]",
    298: "[元宝]",
    299: "[牛啊]",
    300: "[胖三斤]",
    301: "[好闪]",
    302: "[左拜年]",
    303: "[右拜年]",
    304: "[红包包]",
    305: "[右亲亲]",
    306: "[牛气冲天]",
    307: "[喵喵]",
    308: "[求红包]",
    309: "[谢红包]",
    310: "[新年烟花]",
    311: "[打call]",
    312: "[变形]",
    313: "[嗑到了]",
    314: "[仔细分析]",
    315: "[加油]",
    316: "[我没事]",
    317: "[菜狗]",
    318: "[崇拜]",
    319: "[比心]",
    320: "[庆祝]",
    321: "[老色痞]",
    322: "[拒绝]",
    323: "[嫌弃]",
}

# original text copied from Tim
qq_emoji_text_list = {
    0: "[惊讶]",
    1: "[撇嘴]",
    2: "[色]",
    3: "[发呆]",
    4: "[得意]",
    5: "[流泪]",
    6: "[害羞]",
    7: "[闭嘴]",
    8: "[睡]",
    9: "[大哭]",
    10: "[尴尬]",
    11: "[发怒]",
    12: "[调皮]",
    13: "[呲牙]",
    14: "[微笑]",
    15: "[难过]",
    16: "[酷]",
    17: "[Empty]",
    18: "[抓狂]",
    19: "[吐]",
    20: "[偷笑]",
    21: "[可爱]",
    22: "[白眼]",
    23: "[傲慢]",
    24: "[饥饿]",
    25: "[困]",
    26: "[惊恐]",
    27: "[流汗]",
    28: "[憨笑]",
    29: "[悠闲]",
    30: "[奋斗]",
    31: "[咒骂]",
    32: "[疑问]",
    33: "[嘘]",
    34: "[晕]",
    35: "[折磨]",
    36: "[衰]",
    37: "[骷髅]",
    38: "[敲打]",
    39: "[再见]",
    40: "[Empty]",
    41: "[发抖]",
    42: "[爱情]",
    43: "[跳跳]",
    44: "[Empty]",
    45: "[Empty]",
    46: "[猪头]",
    47: "[Empty]",
    48: "[Empty]",
    49: "[拥抱]",
    50: "[Empty]",
    51: "[Empty]",
    52: "[Empty]",
    53: "[蛋糕]",
    54: "[闪电]",
    55: "[炸弹]",
    56: "[刀]",
    57: "[足球]",
    58: "[Empty]",
    59: "[便便]",
    60: "[咖啡]",
    61: "[饭]",
    62: "[Empty]",
    63: "[玫瑰]",
    64: "[凋谢]",
    65: "[Empty]",
    66: "[爱心]",
    67: "[心碎]",
    68: "[Empty]",
    69: "[礼物]",
    70: "[Empty]",
    71: "[Empty]",
    72: "[Empty]",
    73: "[Empty]",
    74: "[太阳]",
    75: "[月亮]",
    76: "[赞]",
    77: "[踩]",
    78: "[握手]",
    79: "[胜利]",
    80: "[Empty]",
    81: "[Empty]",
    82: "[Empty]",
    83: "[Empty]",
    84: "[Empty]",
    85: "[飞吻]",
    86: "[怄火]",
    87: "[Empty]",
    88: "[Empty]",
    89: "[西瓜]",
    90: "[Empty]",
    91: "[Empty]",
    92: "[Empty]",
    93: "[Empty]",
    94: "[Empty]",
    95: "[Empty]",
    96: "[冷汗]",
    97: "[擦汗]",
    98: "[抠鼻]",
    99: "[鼓掌]",
    100: "[糗大了]",
    101: "[坏笑]",
    102: "[左哼哼]",
    103: "[右哼哼]",
    104: "[哈欠]",
    105: "[鄙视]",
    106: "[委屈]",
    107: "[快哭了]",
    108: "[阴险]",
    109: "[亲亲]",
    110: "[吓]",
    111: "[可怜]",
    112: "[菜刀]",
    113: "[啤酒]",
    114: "[篮球]",
    115: "[乒乓]",
    116: "[示爱]",
    117: "[瓢虫]",
    118: "[抱拳]",
    119: "[勾引]",
    120: "[拳头]",
    121: "[差劲]",
    122: "[爱你]",
    123: "[NO]",
    124: "[OK]",
    125: "[转圈]",
    126: "[磕头]",
    127: "[回头]",
    128: "[跳绳]",
    129: "[挥手]",
    130: "[激动]",
    131: "[街舞]",
    132: "[献吻]",
    133: "[左太极]",
    134: "[右太极]",
    135: "[Empty]",
    136: "[双喜]",
    137: "[鞭炮]",
    138: "[灯笼]",
    139: "[发财]",
    140: "[K歌]",
    141: "[购物]",
    142: "[邮件]",
    143: "[帅]",
    144: "[喝彩]",
    145: "[祈祷]",
    146: "[爆筋]",
    147: "[棒棒糖]",
    148: "[喝奶]",
    149: "[下面]",
    150: "[香蕉]",
    151: "[飞机]",
    152: "[开车]",
    153: "[高铁左车头]",
    154: "[车厢]",
    155: "[高铁右车头]",
    156: "[多云]",
    157: "[下雨]",
    158: "[钞票]",
    159: "[熊猫]",
    160: "[灯泡]",
    161: "[风车]",
    162: "[闹钟]",
    163: "[打伞]",
    164: "[彩球]",
    165: "[钻戒]",
    166: "[沙发]",
    167: "[纸巾]",
    168: "[药]",
    169: "[手枪]",
    170: "[青蛙]",
    171: "[茶]",
    172: "[眨眼睛]",
    173: "[泪奔]",
    174: "[无奈]",
    175: "[卖萌]",
    176: "[小纠结]",
    177: "[喷血]",
    178: "[斜眼笑]",
    179: "[doge]",
    180: "[惊喜]",
    181: "[骚扰]",
    182: "[笑哭]",
    183: "[我最美]",
    184: "[河蟹]",
    185: "[羊驼]",
    186: "[Empty]",
    187: "[幽灵]",
    188: "[蛋]",
    189: "[Empty]",
    190: "[菊花]",
    191: "[Empty]",
    192: "[红包]",
    193: "[大笑]",
    194: "[不开心]",
    195: "[Empty]",
    196: "[Empty]",
    197: "[冷漠]",
    198: "[呃]",
    199: "[好棒]",
    200: "[拜托]",
    201: "[点赞]",
    202: "[无聊]",
    203: "[托脸]",
    204: "[吃]",
    205: "[送花]",
    206: "[害怕]",
    207: "[花痴]",
    208: "[小样儿]",
    209: "[Empty]",
    210: "[飙泪]",
    211: "[我不看]",
    212: "[托腮]",
    213: "[Empty]",
    214: "[啵啵]",
    215: "[糊脸]",
    216: "[拍头]",
    217: "[扯一扯]",
    218: "[舔一舔]",
    219: "[蹭一蹭]",
    220: "[拽炸天]",
    221: "[顶呱呱]",
    222: "[抱抱]",
    223: "[暴击]",
    224: "[开枪]",
    225: "[撩一撩]",
    226: "[拍桌]",
    227: "[拍手]",
    228: "[恭喜]",
    229: "[干杯]",
    230: "[嘲讽]",
    231: "[哼]",
    232: "[佛系]",
    233: "[掐一掐]",
    234: "[惊呆]",
    235: "[颤抖]",
    236: "[啃头]",
    237: "[偷看]",
    238: "[扇脸]",
    239: "[原谅]",
    240: "[喷脸]",
    241: "[生日快乐]",
    242: "[Empty]",
    243: "[Empty]",
    244: "[Empty]",
    245: "[Empty]",
    246: "[Empty]",
    247: "[Empty]",
    248: "[Empty]",
    249: "[Empty]",
    250: "[Empty]",
    251: "[Empty]",
    252: "[Empty]",
    253: "[Empty]",
    254: "[Empty]",
    255: "[Empty]",
}

qq_sface_list = {
    1: "[拜拜]",
    2: "[鄙视]",
    3: "[菜刀]",
    4: "[沧桑]",
    5: "[馋了]",
    6: "[吃惊]",
    7: "[微笑]",
    8: "[得意]",
    9: "[嘚瑟]",
    10: "[瞪眼]",
    11: "[震惊]",
    12: "[鼓掌]",
    13: "[害羞]",
    14: "[好的]",
    15: "[惊呆了]",
    16: "[静静看]",
    17: "[可爱]",
    18: "[困]",
    19: "[脸红]",
    20: "[你懂的]",
    21: "[期待]",
    22: "[亲亲]",
    23: "[伤心]",
    24: "[生气]",
    25: "[摇摆]",
    26: "[帅]",
    27: "[思考]",
    28: "[震惊哭]",
    29: "[痛心]",
    30: "[偷笑]",
    31: "[挖鼻孔]",
    32: "[抓狂]",
    33: "[笑着哭]",
    34: "[无语]",
    35: "[捂脸]",
    36: "[喜欢]",
    37: "[笑哭]",
    38: "[疑惑]",
    39: "[赞]",
    40: "[眨眼]",
}


class DownloadTooLargeError(Exception):
    """Raised when a download exceeds the configured size limit."""


def normalize_qq_download_url(url: str) -> str:
    """
    Normalize QQ download URLs by replacing IP addresses with multimedia.nt.qq.com.cn domain.
    This improves connectivity and fixes SSL certificate validation issues.

    Examples:
    - https://43.128.17.103/download?... -> https://multimedia.nt.qq.com.cn/download?...
    - https://c2cpicdw.qpic.cn/download?... -> https://multimedia.nt.qq.com.cn/download?...
    """
    # Replace IP addresses (with or without port) with NTQQ domain
    url = re.sub(r"https?://\d+\.\d+\.\d+\.\d+(:\d+)?/", "https://multimedia.nt.qq.com.cn/", url)

    # Also replace problematic qpic.cn domains with better NTQQ domain
    url = url.replace("c2cpicdw.qpic.cn", "multimedia.nt.qq.com.cn")
    url = url.replace("gchat.qpic.cn", "multimedia.nt.qq.com.cn")

    return url


async def async_get_file(url: str) -> IO:
    # Normalize URL to use NTQQ domain for better connectivity
    url = normalize_qq_download_url(url)

    temp_file = tempfile.NamedTemporaryFile()
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            temp_file.write(resp.content)
            if temp_file.seek(0, 2) <= 0:
                raise EOFError("File downloaded is Empty")
            temp_file.seek(0)
    except Exception as e:
        temp_file.close()
        raise e
    return temp_file


async def async_get_file_with_limit(url: str, max_bytes: Optional[int] = None, errcount: int = 0) -> IO:
    """
    Stream download a file with an optional byte ceiling.
    Raises DownloadTooLargeError if Content-Length > max_bytes or streamed bytes exceed max_bytes.

    Retry strategy:
    1. Normalize URL (replace IPs and poor domains with multimedia.nt.qq.com.cn)
    2. Try normalized URL (up to 2 retries)
    3. If 400 error, try alternative appid (1406 <-> 1407)
    """
    url = normalize_qq_download_url(url)

    temp_file = tempfile.NamedTemporaryFile()
    if errcount > 2:
        logger.error(f"Max retries exceeded for {url}")
        temp_file.close()
        raise httpx.HTTPError("Max retries exceeded")
    try:
        timeout = httpx.Timeout(30.0, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream("GET", url) as resp:
                resp.raise_for_status()
                cl = resp.headers.get("Content-Length")
                if max_bytes is not None and cl is not None:
                    try:
                        if int(cl) > max_bytes:
                            raise DownloadTooLargeError(f"Content-Length {cl} exceeds limit {max_bytes}")
                    except ValueError:
                        pass  # malformed header; ignore and stream-check

                total = 0
                async for chunk in resp.aiter_bytes(chunk_size=65536):
                    if not chunk:
                        continue
                    total += len(chunk)
                    if max_bytes is not None and total > max_bytes:
                        raise DownloadTooLargeError(f"Downloaded {total} exceeds limit {max_bytes}")
                    temp_file.write(chunk)

                if temp_file.seek(0, 2) <= 0:
                    raise EOFError("File downloaded is Empty")
                temp_file.seek(0)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            logger.warning(f"Appid mismatch for {url}, attempting retry with alternative appid.")
            # Extract appid from the URL
            parsed_url = urllib.parse.urlparse(url)
            query_params = urllib.parse.parse_qs(parsed_url.query)

            original_appid = query_params.get("appid", [None])[0]

            # Determine the alternative appid
            alternative_appid = None
            if original_appid == "1407":
                alternative_appid = "1406"
            elif original_appid == "1406":
                alternative_appid = "1407"

            if alternative_appid:
                current_query_params = query_params.copy()
                current_query_params["appid"] = [alternative_appid]

                # Reconstruct the URL with the alternative appid
                new_query_string = urllib.parse.urlencode(current_query_params, doseq=True)
                new_image_link = parsed_url._replace(query=new_query_string).geturl()

                try:
                    temp_file = await async_get_file_with_limit(
                        new_image_link, max_bytes=max_bytes, errcount=errcount + 1
                    )
                    return temp_file
                except Exception as e:
                    logger.error(f"Failed to download image with alternative appid: {e}")
        # For other HTTP errors, fall through to retry logic below
        temp_file.close()
        temp_file = await async_get_file_with_limit(url, max_bytes=max_bytes, errcount=errcount + 1)
    except Exception as e:
        logger.error(f"Unexpected error for {url}: {e}")
        temp_file.close()
        # Retry with incremented error count
        temp_file = await async_get_file_with_limit(url, max_bytes=max_bytes, errcount=errcount + 1)
    return temp_file


def sync_get_file(url: str) -> IO:
    url = normalize_qq_download_url(url)

    temp_file = tempfile.NamedTemporaryFile()
    try:
        resp = httpx.get(url)
        temp_file.write(resp.content)
        if temp_file.seek(0, 2) <= 0:
            raise EOFError("File downloaded is Empty")
        temp_file.seek(0)
    except Exception as e:
        temp_file.close()
        raise e
    return temp_file


async def cq_get_image(image_link: str, max_bytes: Optional[int] = None) -> Optional[IO]:
    """
    Download image from QQ with optional size limit.
    """

    try:
        if max_bytes is None:
            return await async_get_file(image_link)
        return await async_get_file_with_limit(image_link, max_bytes=max_bytes)
    except DownloadTooLargeError:
        # Caller will handle over-limit by sending a placeholder message
        raise
    except Exception as e:
        logger.warning("File download failed.")
        logger.warning(str(e))
        logger.warning(f"URL: {image_link}")
        return None


def async_send_messages_to_master(msg: Message):
    """
    Send message to master, if the message contains a file, the file will
    be closed after sending NO MATTER WHAT.
    """

    try:
        coordinator.send_message(msg)
    finally:
        if msg.file:
            msg.file.close()


def fix_cq_image_url_in_reply(text: str) -> str:
    """
    Fix &amp; in CQ image URLs
    """
    pattern = "\\[CQ:image(.*?)url\\=(.*?),(.*?)\\]"

    for match in re.finditer(pattern, text):
        full_match = match.group(0)
        url = match.group(2)
        fixed_url = " " + url.replace("&amp;", "&") + " "
        fixed_cq_code = full_match.replace(url, fixed_url)
        text = text.replace(full_match, fixed_cq_code)

    return text


def process_quote_text(text, max_length):
    """
    Simple wrapper for processing quoted text
    """

    qt_txt = "%s" % text
    if max_length > 0:
        tgt_text = qt_txt[:max_length]
        if len(qt_txt) >= max_length:
            tgt_text += "…"
        tgt_text = "「%s」" % tgt_text
    elif max_length < 0:
        tgt_text = "「%s」" % qt_txt
    else:
        tgt_text = ""
    return tgt_text


def coolq_text_encode(text: str):
    """
    Escape special characters for CQ Code text
    """

    expr = (("&", "&amp;"), ("[", "&#91;"), ("]", "&#93;"))
    for r in expr:
        text = text.replace(*r)
    return text


def coolq_para_encode(text: str):
    """
    Escape special characters for CQ Code parameters
    """

    expr = (("&", "&amp;"), ("[", "&#91;"), ("]", "&#93;"), (",", "&#44;"))
    for r in expr:
        text = text.replace(*r)
    return text


def param_spliter(str_param):
    """
    UNUSED, split parameters: key=value;key=value;key=value
    """

    params = str_param.split(";")
    param = {}
    for _k in params:
        key, value = _k.strip().split("=")
        param[key] = value
    return param


async def download_file(download_url: str) -> Union[IO, str]:
    try:
        return await async_get_file(download_url)
    except Exception as e:
        logger.warning("Error occurs when downloading files: " + str(e))
        return "Error occurs when downloading files: " + str(e)


async def download_file_with_limit(download_url: str, max_bytes: int) -> IO:
    """
    Download with size ceiling; raises DownloadTooLargeError on exceed, or other exceptions on error.
    """
    return await async_get_file_with_limit(download_url, max_bytes=max_bytes)


def download_user_avatar(uid: str):
    url = "https://q1.qlogo.cn/g?b=qq&nk={}&s=0".format(uid)
    try:
        return sync_get_file(url)
    except Exception as e:
        logger.warning("Error occurs when downloading files: " + str(e))
        raise


def download_group_avatar(uid: str):
    url = "https://p.qlogo.cn/gh/{}/{}/".format(uid, uid)
    try:
        return sync_get_file(url)
    except Exception as e:
        logger.warning("Error occurs when downloading files: " + str(e))
        raise


async def download_voice(voice_url: str):
    origin_file, audio_file = None, None
    try:
        origin_file = await async_get_file(voice_url)
        silk_header = origin_file.read(10)
        origin_file.seek(0)
        if b"#!SILK_V3" in silk_header:
            with tempfile.NamedTemporaryFile() as pcm_file:
                pilk.decode(origin_file.name, pcm_file.name)
                audio_file = tempfile.NamedTemporaryFile()
                pydub.AudioSegment.from_raw(file=pcm_file, sample_width=2, frame_rate=24000, channels=1).export(
                    audio_file, format="ogg", codec="libopus", parameters=["-vbr", "on"]
                )
        else:
            audio_file = origin_file
    except Exception as e:
        if origin_file:
            origin_file.close()
        if audio_file:
            audio_file.close()
        logger.warning("Error occurs when downloading files: " + str(e))
        raise
    return audio_file


def strf_time(seconds: int) -> str:
    """
    Convert seconds to human readable string format: 1d2h3m4s
    """

    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    text = ""
    text += f"{days}d" if days else ""
    text += f"{hours}h" if hours else ""
    text += f"{minutes}m" if minutes else ""
    text += f"{seconds}s" if seconds else ""
    return text
