#!/usr/bin/env python
# -*- coding:GBK

import re


def count_chinese(unicode_str):
    """
    统计字符串中中文字符的个数
    """
    count = 0
    for char in unicode_str:
        if is_chinese(char):
            count += 1

    return count


def is_chinese(char):
    """
        判断char是否为中文，char为unicode
    """
    if u'\u4e00' <= char <= u'\u9fa5':
        return True
    else:
        return False


def is_number(char):
    """
        判断char是否为数字，char为unicode
    """
    if u'\u0030' <= char <= u'\u0039':
        return True
    else:
        return False


def is_alphabet(char):
    """
        判断char是否为字母，char为unicode
    """
    if u'\u0041' <= char <= u'\u005a':
        return True
    if u'\u0061' <= char <= u'\u007a':
        return True
    return False


def is_legal(char):
    """
        判断char是否为非汉字，字母，数字之外的其他字符，char为unicode
    """
    if is_alphabet(char) or is_chinese(char) or is_number(char):
        return True
    else:
        return False


def B2Q(char):
    """
        半角转全角，char为unicode
    """
    inside_code = ord(char)
    if inside_code < 0x0020 or inside_code > 0x7e:
        return char
    if inside_code == 0x0020:
        inside_code = 0x3000
    else:
        inside_code += 0xfee0
    return unichr(inside_code)


def Q2B(char):
    """
        全角转半角，char为unicode
    """
    inside_code = ord(char)
    if inside_code == 0x3000:
        inside_code = 0x0020
    else:
        inside_code -= 0xfee0
    if inside_code < 0x0020 or inside_code > 0x7e:
        return char
    return unichr(inside_code)


def string_Q2B(string):
    """
    """
    string = ''.join(Q2B(char) for char in string)
    return string


def string_filter(string):
    """
        过滤各种特殊符号
    """
    string = ''.join(is_legal(char) and char or '' for char in string)
    return string


def html_filter(content):
    """
        过滤正文中的html信息,过滤符号杂质
    """
    try:
        content = re.sub('<[^>]*>', '', content)
    except Exception, e:
        return ''
    return content


def string_format(string):
    """
    """
    string = string.replace(u'\u005c', u'')
    string = string.replace(u'\u0027', u'\u005c\u0027')
    string = string.encode("GBK", "ignore")
    return string


def url_format(url):
    """
    """
    url = url.replace("'", "")
    return url

if __name__ == '__main__':
    string = '我是abc**987&^%test我是全角'.decode('GBK', 'ignore')
    print(string)
    print(string_filter(string))

    print is_chinese(u'！')







