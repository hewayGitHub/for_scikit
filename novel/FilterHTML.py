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
cur_delimiter = str(chr(1))  # �洢�ļ��ķָ���


def diff_chinese(raw_chapter_content, format_chapter_content):
    """
    �Ƚϸ�ʽ��ǰ�������������ַ������Ƿ����
    ������ȣ�������ڸ�Ŀ¼��fmt_wrong�ļ�����
    """
    #����ַ�Ϊ������
    not_chinese_pattern = re.compile(u'[^\u4e00-\u9fa5]')

    raw_chinese = not_chinese_pattern.sub('', raw_chapter_content)
    fmt_chinese = not_chinese_pattern.sub('', format_chapter_content)
    #print "�����ַ�����", len(raw_chinese), len(fmt_chinese)
    if len(raw_chinese) != len(fmt_chinese):
        print "��ʽ��ǰ���½����������ַ���Ŀ�����"
        with open('fmt_wrong/raw', 'w') as raw_file:
            raw_file.write(raw_chinese.encode('gbk', 'ignore'))
        with open('fmt_wrong/fmt', 'w') as fmt_file:
            fmt_file.write(fmt_chinese.encode('gbk', 'ignore'))
    else:
        pass


def chapter_format(raw_chapter_content):
    """
    ���˲������½������е�HTML�������ش������½����ġ�
    �����������½����Ķ���unicode���롣
    ������½�����ֻ��<p>��</p>�����Ҳ�����Ƕ�ס�

    ����Ҫ�����£�
    0��������β�հ��ַ�ȥ��
    1���������Ե�<p...>��</p...>�ֱ��滻Ϊ<p>��</p>
    2�������е�<div...>��</div...>�ֱ��滻Ϊ<p>��</p>
    3����<br...>��������滻Ϊ</p><p>��<p>
    4���������HTML��ǩ
    5����(<p>)+��(</p>)+�滻Ϊ<p>��</p>������ն���<p></p>
    6��Ϊ<p>�������<p style="text-indent:2em;">
    7����֤<p>�������Ƕ�ף���<p> txt <p> txt </p> txt </p>
    8������<a>��ǩ������֮����ı���<script>��ǩͬ��
    9�����˰����������Ե��ı���
    ע�⣻
    1��HTML��ǩ����ʼ�ַ�Ϊ[a-zA-Z!]�����Ա�֤����ƥ��<1><���>֮�������
    2�����ڱ�ǩp��/p��div��Ҫȷ����ȫƥ�䣬��Ϊ���ǿ�����������ǩ��ǰ׺
    3��ͨ��ʹ��unicode��\s����ƥ����չ�������ģ�ISO 8859-1���еĲ���Ͽո�\xa0��"&nbsp;"�����Ŀո�\u3000�ȿհ��ַ�
    """
    format_chapter_content = u''

    #����������ʽ����ʶ�����ж�Ӧtag����ʽ
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

    #��ɸ�ʽ������0-8
    pre_end = 0  # ��־��һ��tag��βindex + 1���ʳ�ʼ��Ϊ0
    sign_pre_tag = 0  # ��־html tag�����ڹ��˱�ǩ�Լ��������ݡ�0:Ĭ��״̬ -1:<a> -2:<script>
    p_level = 0  # ����<p>��1������</p>��1
    is_p_head = False  # ��ǵ�ǰ�����Ƿ��Ƕ���
    need_remove = False  # ������<a>������Ҫ���صı�ǩʱ��ΪTrue��ȥ����β��ǩ�Լ�����֮�������
    for tag_match in tag_pattern.finditer(raw_chapter_content):
        tag = tag_match.group()
        first = tag_match.start()
        end = tag_match.end()

        #���need_removeΪTrue��������ǰtag��ǰһ��tag֮������Ĳ���Ҫ�����
        #�����ǰ�ı�ǩΪ</a>��</script>������֮ǰ����need_removeΪFalse��
        if need_remove:
            if sign_pre_tag == -1 and tag.startswith(u'</a') and back_link_pattern.match(tag):
                need_remove = False
                sign_pre_tag = 0
            elif sign_pre_tag == -2 and tag.startswith(u'</script') and back_script_pattern.match(tag):
                need_remove = False
                sign_pre_tag = 0
            #����pre_end
            pre_end = end
            continue

        #is_p_head�����ڶ��ף�ֱ�������ǿյ����ģ������൱��һֱ�Ƕ���
        if is_p_head:  # ����
            if pre_end == first:
                between_content = u''
            else:
                between_content = left_space_pattern.sub('', raw_chapter_content[pre_end:first])

            if len(between_content) != 0:
                is_p_head = False
        else:
            between_content = raw_chapter_content[pre_end:first]

        #����pre_end
        pre_end = end

        if (tag.startswith(u'<p') and p_pattern.match(tag)) \
                or (tag.startswith(u'<div') and div_pattern.match(tag)):
            #����<p>��Ƕ�ף��ڵ�ǰ<p>ǰ���</p>����ֹǶ�׳���
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
            #ͨ������÷�֧��p_levelһ������1��ȥ����β�Ŀո�Ϊ���Է�ԭ�ĸ�ʽ��������else���Դ���
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
            # p_level����0����br��<p>��</p>֮��ʱ�滻Ϊ</p><p>������Ϊbetween_content���<p></p>
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

    #������һ����ǩ��ĩβ���ı���ͨ������Ҫ
    format_chapter_content += right_space_pattern.sub('', raw_chapter_content[pre_end:len(raw_chapter_content)])

    #���html���淶����δ�պϵ�<p>�����½�ĩβ���
    if p_level != 0:
        format_chapter_content += u'</p>'

    #ȥ��<p></p>
    format_chapter_content = empty_p_pattern.sub('', format_chapter_content)

    return format_chapter_content


def test_reg():
    """
    �����������������chapter_format��������ʽ�Ƿ���ȷ
    """
    raw_chapter_content = u"<div class='div_class'>" \
                          u"<p class='p_class'>&nbsp;&nbsp;  \u3000p1</p><pre></pre><br style='br_style'/>" \
                          u"after br" \
                          u"<p> <span>p2</span> <br/>p3</p>" \
                          u"<other style='other_style'>other</other>���Ƕ���<��һ��><1><>" \
                          u"<a>link_data</a>a_middle<a href>link_data2</a>" \
                          u"</div>"
    print raw_chapter_content.encode('gbk')
    print chapter_format(raw_chapter_content).encode('gbk')

if __name__ == "__main__":
    test_reg()

