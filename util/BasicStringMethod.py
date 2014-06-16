#!/usr/bin/env python
# -*- coding:GBK

import re


def count_chinese(unicode_str):
    """
    ͳ���ַ����������ַ��ĸ���
    """
    count = 0
    for char in unicode_str:
        if is_chinese(char):
            count += 1

    return count


def is_chinese(char):
    """
        �ж�char�Ƿ�Ϊ���ģ�charΪunicode
    """
    if u'\u4e00' <= char <= u'\u9fa5':
        return True
    else:
        return False


def is_number(char):
    """
        �ж�char�Ƿ�Ϊ���֣�charΪunicode
    """
    if u'\u0030' <= char <= u'\u0039':
        return True
    else:
        return False


def is_alphabet(char):
    """
        �ж�char�Ƿ�Ϊ��ĸ��charΪunicode
    """
    if u'\u0041' <= char <= u'\u005a':
        return True
    if u'\u0061' <= char <= u'\u007a':
        return True
    return False


def is_legal(char):
    """
        �ж�char�Ƿ�Ϊ�Ǻ��֣���ĸ������֮��������ַ���charΪunicode
    """
    if is_alphabet(char) or is_chinese(char) or is_number(char):
        return True
    else:
        return False


def B2Q(char):
    """
        ���תȫ�ǣ�charΪunicode
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
        ȫ��ת��ǣ�charΪunicode
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
        ���˸����������
    """
    string = ''.join(is_legal(char) and char or '' for char in string)
    return string


def html_filter(content):
    """
        ���������е�html��Ϣ,���˷�������
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
    string = '����abc**987&^%test����ȫ��'.decode('GBK', 'ignore')
    print(string)
    print(string_filter(string))

    print is_chinese(u'��')







