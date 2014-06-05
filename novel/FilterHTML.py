#!/usr/bin/env python
# -*- coding:GBK

"""
Filter and format the html page of chinese novel
"""
# Author: He Wei
# Date: 2014-05-26 17:16


import re
import os


cur_linesep = os.linesep
cur_delimiter = str(chr(1))  # 存储文件的分隔符


def diff_chinese(raw_chapter_content, format_chapter_content):
    """
    比较格式化前后正文中中文字符个数是否相等
    若不相等，将其存于根目录下fmt_wrong文件夹中
    """
    #检测字符为非中文
    not_chinese_pattern = re.compile(u'[^\u4e00-\u9fa5]')

    raw_chinese = not_chinese_pattern.sub('', raw_chapter_content)
    fmt_chinese = not_chinese_pattern.sub('', format_chapter_content)
    #print "中文字符数：", len(raw_chinese), len(fmt_chinese)
    if len(raw_chinese) != len(fmt_chinese):
        print "格式化前后章节正文中文字符数目不相等"
        with open('fmt_wrong/raw', 'w') as raw_file:
            raw_file.write(raw_chinese.encode('gbk', 'ignore'))
        with open('fmt_wrong/fmt', 'w') as fmt_file:
            fmt_file.write(fmt_chinese.encode('gbk', 'ignore'))
    else:
        pass


def chapter_format(raw_chapter_content):
    """
    过滤并处理章节正文中的HTML，并返回处理后的章节正文。
    输入和输出的章节正文都是unicode编码。
    输出的章节正文只有<p>和</p>，而且不会有嵌套。

    具体要求如下：
    0，将段首尾空白字符去掉
    1，将有属性的<p...>和</p...>分别替换为<p>和</p>
    2，将所有的<div...>和</div...>分别替换为<p>和</p>
    3，将<br...>根据情况替换为</p><p>或<p>
    4，清除其它HTML标签
    5，将(<p>)+和(</p>)+替换为<p>和</p>，清除空段落<p></p>
    6，为<p>添加属性<p style="text-indent:2em;">
    7，保证<p>不会出现嵌套，即<p> txt <p> txt </p> txt </p>
    8，过滤<a>标签和它们之间的文本，<script>标签同样
    9，过滤包含隐藏属性的文本。
    注意；
    1，HTML标签的起始字符为[a-zA-Z!]，可以保证不会匹配<1><你好>之类的内容
    2，对于标签p、/p、div等要确保完全匹配，因为它们可能是其它标签的前缀
    3，通过使用unicode，\s可以匹配扩展的拉丁文（ISO 8859-1）中的不间断空格\xa0、"&nbsp;"和中文空格\u3000等空白字符
    """
    format_chapter_content = u''

    #下列正则表达式用于识别所有对应tag的形式
    left_space_pattern = re.compile(u'^(\s|&nbsp;)+', re.U)
    right_space_pattern = re.compile(u'(\s|&nbsp;)+$', re.U)
    tag_pattern = re.compile(u'</?[a-zA-Z!][^>]*>', re.U)

    tag_reg = u'<{0}(\s[^>]*)?>'
    p_pattern = re.compile(tag_reg.format('p'), re.U)
    back_p_pattern = re.compile(tag_reg.format('/p'), re.U)
    div_pattern = re.compile(tag_reg.format('div'), re.U)
    back_div_pattern = re.compile(tag_reg.format('/div'), re.U)
    link_pattern = re.compile(tag_reg.format('a'), re.U)
    back_link_pattern = re.compile(tag_reg.format('/a'), re.U)
    script_pattern = re.compile(tag_reg.format('script'), re.U)
    back_script_pattern = re.compile(tag_reg.format('/script'), re.U)

    br_pattern = re.compile(u'<br([\s/][^>]*)?>', re.U)
    empty_p_pattern = re.compile(u'<p style="text-indent:2em;"></p>', re.U)

    #完成格式化步骤0-8
    pre_end = 0  # 标志上一个tag的尾index + 1，故初始化为0
    sign_pre_tag = 0  # 标志html tag，用于过滤标签以及其中内容。0:默认状态 -1:<a> -2:<script>
    p_level = 0  # 遇到<p>加1，遇到</p>减1
    is_p_head = False  # 标记当前正文是否是段首
    need_remove = False  # 当遇到<a>或者需要隐藏的标签时，为True，去除首尾标签以及它们之间的正文
    for tag_match in tag_pattern.finditer(raw_chapter_content):
        tag = tag_match.group()
        first = tag_match.start()
        end = tag_match.end()

        #如果need_remove为True，表明当前tag和前一个tag之间的正文不需要输出。
        #如果当前的标签为</a>或</script>，根据之前设置need_remove为False。
        if need_remove:
            if sign_pre_tag == -1 and tag.startswith(u'</a') and back_link_pattern.match(tag):
                need_remove = False
                sign_pre_tag = 0
            elif sign_pre_tag == -2 and tag.startswith(u'</script') and back_script_pattern.match(tag):
                need_remove = False
                sign_pre_tag = 0
            #更新pre_end
            pre_end = end
            continue

        #is_p_head表明在段首，直到遇到非空的正文，否则相当于一直是段首
        if is_p_head:  # 段首
            if pre_end == first:
                between_content = u''
            else:
                between_content = left_space_pattern.sub('', raw_chapter_content[pre_end:first])

            if len(between_content) != 0:
                is_p_head = False
        else:
            between_content = raw_chapter_content[pre_end:first]

        #更新pre_end
        pre_end = end

        if (tag.startswith(u'<p') and p_pattern.match(tag)) \
                or (tag.startswith(u'<div') and div_pattern.match(tag)):
            #出现<p>的嵌套，在当前<p>前添加</p>，防止嵌套出现
            if p_level >= 1:
                between_content = right_space_pattern.sub('', between_content)
                format_chapter_content += between_content + u'</p><p style="text-indent:2em;">'
            else:
                between_content = left_space_pattern.sub('', between_content)
                between_content = right_space_pattern.sub('', between_content)
                format_chapter_content += u'<p style="text-indent:2em;">' + between_content \
                                          + u'</p><p style="text-indent:2em;">'

            p_level = 1
            is_p_head = True
        elif (tag.startswith(u'</p') and back_p_pattern.match(tag)) \
                or (tag.startswith(u'</div') and back_div_pattern.match(tag)):
            #通常进入该分支，p_level一定等于1。去掉段尾的空格。为了以防原文格式不正常，else予以处理
            if p_level == 1:
                between_content = right_space_pattern.sub('', between_content)
                format_chapter_content += between_content + u'</p>'
            else:
                between_content = left_space_pattern.sub('', between_content)
                between_content = right_space_pattern.sub('', between_content)
                format_chapter_content += u'<p style="text-indent:2em;">' + between_content + u'</p>'

            p_level = 0
            is_p_head = False
        elif tag.startswith(u'<br') and br_pattern.match(tag):
            # p_level大于0，即br在<p>和</p>之间时替换为</p><p>，否则为between_content添加<p></p>
            if p_level >= 1:
                between_content = right_space_pattern.sub('', between_content)
                format_chapter_content += between_content + u'</p><p style="text-indent:2em;">'
            else:
                between_content = left_space_pattern.sub('', between_content)
                between_content = right_space_pattern.sub('', between_content)
                format_chapter_content += u'<p style="text-indent:2em;">' + between_content \
                                          + u'</p><p style="text-indent:2em;">'

            p_level = 1
            is_p_head = True
        else:
            if tag.startswith(u'<a') and link_pattern.match(tag):
                need_remove = True
                sign_pre_tag = -1
            elif tag.startswith(u'<script') and script_pattern.match(tag):
                need_remove = True
                sign_pre_tag = -2

            if p_level == 0:
                between_content = left_space_pattern.sub('', between_content)
                format_chapter_content += u'<p style="text-indent:2em;">' + between_content

                p_level = 1
            else:
                format_chapter_content += between_content

    #处理上一个标签至末尾的文本，通常不需要
    format_chapter_content += right_space_pattern.sub('', raw_chapter_content[pre_end:len(raw_chapter_content)])

    #如果html不规范，有未闭合的<p>，在章节末尾添加
    if p_level != 0:
        format_chapter_content += u'</p>'

    #去除<p></p>
    format_chapter_content = empty_p_pattern.sub('', format_chapter_content)

    return format_chapter_content


def test_reg():
    """
    构造测试用例，测试chapter_format中正则表达式是否正确
    """
    raw_chapter_content = u"<div class='div_class'>" \
                          u"<p class='p_class'>&nbsp;&nbsp;  \u3000p1</p><pre></pre><br style='br_style'/>" \
                          u"after br" \
                          u"<p> <span>p2</span> <br/>p3</p>" \
                          u"<other style='other_style'>other</other>我们都是<第一章><1><>" \
                          u"<a>link_data</a>a_middle<a href>link_data2</a>" \
                          u"</div>"
    print raw_chapter_content.encode('gbk')
    print chapter_format(raw_chapter_content).encode('gbk')

if __name__ == "__main__":
    test_reg()

