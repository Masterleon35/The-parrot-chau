import re
import codecs
import Levenshtein

# -*-coding:utf-8 -*-


def deal_attribute_content_to_array(attribute_content_file):
    """
    将百科名医爬取下来的疾病或者药品属性文件处理成数组属性的格式
    :param attribute_content_file: 从百科名医爬取的属性文件
    :return: 满足格式的列表输出
    """
    def check_and_modify_output_attribute_array_list(output_list):
        check_line_list = list()
        for line in output_list:
            line = line.strip()
            sub_1 = r'<->\|\|\|\|'
            sub_2 = r'\|\|\|\|$'
            line = re.sub(sub_1, '<->', line)
            line = re.sub(sub_2, '', line)

            if not line:
                continue

            if '||||' in line:
                line_list = line.split('||||')
                assert len(line_list) > 1

                for index, line_str in enumerate(line_list):
                    line_str_found_list = re.findall('\|\|', line_str)
                    if len(line_str_found_list) >= 2:
                        line_str_split_list = line_str.split('||')
                        first_part_str = line_str_split_list.pop(0)
                        line_str_new = first_part_str + '||' + ''.join(line_str_split_list)
                        line_list[index] = line_str_new
                    else:
                        pass
                line = '||||'.join(line_list)
            else:
                line_list_again = re.findall('\|\|', line)
                if len(line_list_again) >= 2:
                    # print(line_list_again)
                    line_str_split_list_2 = line.split('||')
                    first_part_str_2 = line_str_split_list_2.pop(0)
                    line = first_part_str_2 + '||' + ''.join(line_str_split_list_2)
                else:
                    pass
            check_line_list.append(line)
        return check_line_list

    def remove_dirty_words(line_list):
        clean_line_list = list()
        for line in line_list:
            line = line.strip()
            sub_pattern = r'<s.*?>|<img.*?>|<!.*?>|</div>|<a.*?>|</a.*?>|<p.*?>|</sup>|\&.*?;|' \
                          r'</strong>|<strong>|</p>|<p>|nbsp;|<br />|</span>|①|②|③|④|⑤|⑥|⑦|⑧|⑨|⑩|' \
                          r'<ins.*?>|</sub>|<sub>'

            line = re.sub(sub_pattern, '', line)
            clean_line_list.append(line)
        return clean_line_list

    sure_list, not_sure_list = get_sure_and_not_sure_list_from_attribute_content_file(attribute_content_file)
    automatic_checked_not_sure_list = automatic_check_not_sure_attribute_content(not_sure_list)
    sure_list.extend(automatic_checked_not_sure_list)
    output_attribute_array_list_checked = check_and_modify_output_attribute_array_list(sure_list)
    output_attribute_array_list_checked_clean = remove_dirty_words(output_attribute_array_list_checked)

    return output_attribute_array_list_checked_clean


def get_sure_and_not_sure_list_from_attribute_content_file(attribute_filename):
    """
    将百科名医爬取的属性文件能确定的部分处理成数组属性格式，将不确定的不处理
    :param attribute_filename: 从百科名医爬取的属性文件
    :return:确定和不确定的列表
    """
    disease_with_diagnosis_sure_list = []
    disease_with_diagnosis_not_sure_list = []

    re_pattern_strong_sure = re.compile(
        "(<p>(.+?)</p>)(<p><strong>(.+?)</strong></p><p>(.+?)</p>)+<p><strong>"
        "(.+?)</strong></p><p>(.+?)"
    )
    re_pattern_strong_no_p_sure = re.compile(
        "(<p><strong>(.+?)</strong></p><p>(.+?)</p>)+<p><strong>(.+?)</strong></p><p>(.+?)"
    )
    re_pattern_no_strong_sure = re.compile(
        "(<p>(.+?)</p>)+<p>(.+?)"
    )
    re_pattern_only_one_p = re.compile('<p>(.+)(<br\s*/*>)?$')

    with codecs.open(attribute_filename, 'r', 'utf8') as f:
        for line in f:
            line = line.strip()
            line = line.replace('<p><strong></strong></p>', '')
            line = line.replace('<p></p>', '')

            split_pattern = re.compile(r"(<->.*?<->)")
            line_list = re.split(split_pattern, line)
            line_list = [c_str.strip() for c_str in line_list]
            attribute_head, attribute_category, attribute_content = line_list[:3]
            line_head = attribute_head + attribute_category
            line = attribute_content

            if re.search(re_pattern_strong_sure, line):
                is_sure = True
                str_to_write = ''
                line_rep = line.replace('<p>(.+?)</p>', '')
                while re.search('<p><strong>(.+?)</strong></p><p>(.+?)</p>(.*)', line_rep):
                    str_summary = re.search('<p><strong>(.+?)</strong></p><p>(.+?)</p>(.*)', line_rep).group(1)
                    str_content = re.search('<p><strong>(.+?)</strong></p><p>(.+?)</p>(.*)', line_rep).group(2)
                    # print('string summary is: ', str_summary)
                    # print('string content is: ', str_content)
                    str_to_write += str_summary
                    str_to_write += '||'
                    str_to_write += str_content
                    str_to_write += '||||'
                    line_rep = re.search('<p><strong>(.+?)</strong></p><p>(.+?)</p>(.*)', line_rep).group(3)
                    if not str_summary[0].isdigit():
                        is_sure = False
                        # print(line_rep)
                if not re.match('<p><strong>(.+?)</strong></p><p>(((?!strong).)+)(<br\s*/*>)?$', line_rep):
                    is_sure = False
                else:
                    str_summary = re.search('<p><strong>(.+?)'
                                            '</strong></p><p>(((?!strong).)+)(<br\s*/*>)?', line_rep).group(1)
                    str_content = re.search('<p><strong>(.+?)'
                                            '</strong></p><p>(((?!strong).)+)(<br\s*/*>)?', line_rep).group(2)
                    if not str_summary[0].isdigit():
                        is_sure = False
                    str_to_write += str_summary
                    str_to_write += '||'
                    str_to_write += str_content
                # print('string to write is: ', str_to_write)
                if is_sure:
                    str_to_write = line_head + str_to_write
                    if '<strong>' in str_to_write or '</strong>' in str_to_write:
                        disease_with_diagnosis_not_sure_list.append(line_head + line)
                    else:
                        # pass
                        disease_with_diagnosis_sure_list.append(str_to_write)
                else:
                    disease_with_diagnosis_not_sure_list.append(line_head + line)

            elif re.search(re_pattern_strong_no_p_sure, line):
                line_ori = line
                is_sure = True
                str_to_write = ''
                while re.search('<p><strong>(.+?)</strong></p><p>(.+?)</p>(.*)', line):
                    str_summary = re.search('<p><strong>(.+?)</strong></p><p>(.+?)</p>(.*)', line).group(1)
                    str_content = re.search('<p><strong>(.+?)</strong></p><p>(.+?)</p>(.*)', line).group(2)
                    str_to_write += str_summary
                    str_to_write += '||'
                    str_to_write += str_content
                    str_to_write += '||||'
                    line = re.search('<p><strong>(.+?)</strong></p><p>(.+?)</p>(.*)', line).group(3)

                    if not str_summary[0].isdigit():
                        is_sure = False

                if not re.match('<p><strong>(.+?)</strong></p><p>'
                                '(((?!strong).)+)(<br\s*/*>)?$', line):
                    is_sure = False
                else:
                    str_summary = re.search('<p><strong>(.+?)</strong></p><p>(((?!strong).)+)(<br\s*/*>)?',
                                            line).group(1)
                    str_content = re.search('<p><strong>(.+?)</strong></p><p>(((?!strong).)+)(<br\s*/*>)?',
                                            line).group(2)
                    if not str_summary[0].isdigit():
                        is_sure = False
                    str_to_write += str_summary
                    str_to_write += '||'
                    str_to_write += str_content

                if is_sure:
                    str_to_write = line_head + str_to_write
                    if '<strong>' in str_to_write or '</strong>' in str_to_write:
                        disease_with_diagnosis_not_sure_list.append(line_head + line_ori)
                    else:
                        # pass
                        disease_with_diagnosis_sure_list.append(str_to_write)
                else:
                    disease_with_diagnosis_not_sure_list.append(line_head + line_ori)

            elif re.search(re_pattern_no_strong_sure, line):
                line_ori = line
                str_to_write = ''
                is_sure = True
                while re.search('<p>(((?!strong).)+?)</p>(.*)', line):
                    str_content = re.search('<p>(((?!strong).)+?)</p>(.*)', line).group(1)
                    line = re.search('<p>(((?!strong).)+?)</p>(.*)', line).group(3)
                    str_to_write += str_content
                    # print(str_content)
                    # print('line is: ', line)
                    str_to_write += '||||'

                if not re.match('<p>(((?!strong).)+)(<br\s*/*>)?$', line):
                    is_sure = False
                else:
                    str_content = re.search('<p>(((?!strong).)+)(<br\s*/*>)?$', line).group(1)
                    str_to_write += str_content

                if is_sure:
                    str_to_write = line_head + str_to_write
                    if '<strong>' in str_to_write or '</strong>' in str_to_write:
                        disease_with_diagnosis_not_sure_list.append(line_head + line_ori)
                    else:
                        # pass
                        disease_with_diagnosis_sure_list.append(str_to_write)
                else:
                    disease_with_diagnosis_not_sure_list.append(line_head + line_ori)

            elif re.match(re_pattern_only_one_p, line):
                str_to_write = re.match(re_pattern_only_one_p, line).group(1)
                disease_with_diagnosis_sure_list.append(line_head + str_to_write)

            else:
                disease_with_diagnosis_not_sure_list.append(line_head + line)

    return disease_with_diagnosis_sure_list, disease_with_diagnosis_not_sure_list


def automatic_check_not_sure_attribute_content(not_sure_list):
    """
    处理不确定的疾病的内容
    :param not_sure_list: 不确定内容列表
    :return: 自动处理后的列表
    author: 小易写的代码，be careful!
    """
    checked_output_list = list()

    for line in not_sure_list:
        # 第一步洗清数据
        line = line.strip()
        sub_nbsp = r'&nbsp;|参考资料.*?|<span.*?">|<o:p>|</o:p>|<!--.*?>|&lt;|&gt;'
        sub_style = r'<p style.*?">'
        sub_a = r'<a.*?>|</a>|</span>|<sub>﻿|</sub>﻿'
        line = re.sub(sub_style, '<p>', line)
        line = re.sub(sub_nbsp, '', line)
        line = re.sub(sub_a, '', line)
        # 将中文点替换为英文点
        line = re.sub(r'．', '.', line)
        line = re.sub(r';', '', line)
        line = re.sub(r'</p><p>﻿﻿﻿﻿﻿﻿﻿﻿2\.', '</p><p>2.', line)
        # print(line)
        # 各种语句类型的条件
        m = "</p><p><strong>2"
        b = "</p><p>2."
        n = r"</strong></p><p>"
        k = '（一）'
        v = '<br /><strong>2.'
        c = '﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿</p><p></p><p>﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿2.'
        x = '<br />2.'
        z = '||||1.'

        # 对语句类型的判断及处理
        if k in line:
            title = ['（一）', '（二）', '（四）', '（五）', '（六）', '（七）', '（八）', '（九）', '（十）', '（十一）', ]
            for j in title:
                line = re.sub(j, '||||' + j, line)
        else:
            if m in line:
                sub_1 = re.findall(r'((</p><p><strong>)(\d)\.)', line)
                for composition in sub_1:
                    first, second, third = composition
                    line = re.sub(first, '||||' + str(third) + '.', line)
                if n in line:
                    line = re.sub(n, '||', line)
            else:
                if b in line:
                    # line = re.sub(r'</p><p>', '||||', line)
                    sub_2 = re.findall(r'((</p ><p>)(\d)\.)', line)
                    for composition in sub_2:
                        first, second, third = composition
                        line = re.sub(first, '||||' + str(third) + '.', line)
                else:
                    if v in line:
                        line = re.sub(v, '||||2.', line)
                        line = re.sub('</p><p><strong>', '||||', line)
                        line = re.sub('</strong></p><p>', '||', line)
                    else:
                        if c in line:
                            line = re.sub('﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿</p><p></p><p>﻿﻿﻿﻿﻿﻿﻿﻿﻿﻿', '||||', line)
                        else:
                            if x in line:
                                sub_1 = re.findall(r'((<br />)(\d)\.)', line)
                                for composition in sub_1:
                                    first, second, third = composition
                                    line = re.sub(first, '||||' + str(third) + '.', line)
            # 删除总结性语句以及错误||||
            # line = re.sub(r'<->临床表现<->.*?1\.', '<->临床表现<->1.', line)

            if r'||||1.' in line:
                line_list = line.split(r'||||1.')
                split_pattern = re.compile(r"(<->.*?<->)")
                head_list = re.split(split_pattern, line_list[0].strip())
                assert len(head_list) >= 2, line
                line = head_list[0] + head_list[1] + r'1.' + line_list[1]

        if r'||||（一）' in line:
            line_list = line.split(r'||||（一）')
            split_pattern = re.compile(r"(<->.*?<->)")
            head_list = re.split(split_pattern, line_list[0].strip())
            assert len(head_list) >= 2, line
            line = head_list[0] + head_list[1] + r'1.' + line_list[1]

        # line = re.sub(r'(?<=<->临床表现<->).*(?=（一）)', '', line)
        line = re.sub(r'\|\|\|\|\|\|\|\|\|\|\|\|', '||||', line)
        line = re.sub(r'\|\|\|\|\|\|\|\|', '||||', line)

        checked_output_list.append(line)

    return checked_output_list


def remove_dirty_words_in_file(filename):
    clean_line_list = list()
    with codecs.open(filename, 'r', 'utf8') as f:
        for line in f:
            line = line.strip()
            sub_pattern = r'<s.*?>|<img.*?>|<!.*?>|</div>|<a.*?>|</a.*?>|<p.*?>|</sup>|\&.*?;|' \
                          r'</strong>|<strong>|</p>|<p>|nbsp;|<br />|</span>|①|②|③|④|⑤|⑥|⑦|⑧|⑨|⑩|' \
                          r'<ins.*?>|</sub>|<sub>'

            line = re.sub(sub_pattern, '', line)
            clean_line_list.append(line)
    return clean_line_list


def check_test_symptom_diagnosis_manual_label_rule(filename):
    check_line_list = list()
    with codecs.open(filename, 'r', 'utf8') as f:
        for line in f:
            line = line.strip()
            sub_1 = r'<->\|\|\|\|'
            sub_2 = r'\|\|\|\|$'
            line = re.sub(sub_1, '<->', line)
            line = re.sub(sub_2, '', line)

            if not line:
                continue

            if '||||' in line:
                line_list = line.split('||||')
                assert len(line_list) > 1

                for index, line_str in enumerate(line_list):
                    line_str_found_list = re.findall('\|\|', line_str)
                    if len(line_str_found_list) >= 2:
                        line_str_split_list = line_str.split('||')
                        first_part_str = line_str_split_list.pop(0)
                        line_str_new = first_part_str + '||' + ''.join(line_str_split_list)
                        line_list[index] = line_str_new
                    else:
                        pass
                line = '||||'.join(line_list)
            else:
                line_list_again = re.findall('\|\|', line)
                if len(line_list_again) >= 2:
                    # print(line_list_again)
                    line_str_split_list_2 = line.split('||')
                    first_part_str_2 = line_str_split_list_2.pop(0)
                    line = first_part_str_2 + '||' + ''.join(line_str_split_list_2)
                else:
                    pass

            check_line_list.append(line)

    return check_line_list


def sort_disease_attribute_according_to_disease(disease_attribute_manual_check_completed_clean_file,
                                                new_disease_file, change_disease_file, attribute_label):

    disease_list = list()
    disease_change_name_dic = dict()
    disease_attribute_dic = dict()

    disease_attribute_output_list = list()
    disease_not_found_test_list = list()

    with codecs.open(new_disease_file, 'r', 'utf8') as f:
        for line in f:
            line = line.strip()
            disease_list.append(line)

    with codecs.open(change_disease_file, 'r', 'utf8') as f:
        for line in f:
            line = line.strip()
            line_list = line.split('<->')
            assert len(line_list) == 2, line
            old_name, new_name = line_list[:2]
            disease_change_name_dic[new_name] = old_name

    cnt_line = 0
    with codecs.open(disease_attribute_manual_check_completed_clean_file, 'r', 'utf8') as f:
        for line in f:
            cnt_line += 1
            line = line.strip()
            line_list = line.split(attribute_label)
            assert len(line_list) == 2, cnt_line
            disease_name, disease_diagnosis = line_list[:2]
            if disease_name in disease_attribute_dic:
                continue
            # assert disease_name not in disease_test_dic, disease_name
            else:
                disease_attribute_dic[disease_name] = disease_diagnosis

    for disease_name in disease_list:
        if disease_name in disease_attribute_dic:
            write_str = disease_name + attribute_label + disease_attribute_dic[disease_name]
            disease_attribute_output_list.append(write_str)
        elif disease_name in disease_change_name_dic:
            if disease_change_name_dic[disease_name] in disease_attribute_dic:
                write_str = disease_name + attribute_label + disease_attribute_dic[disease_change_name_dic[disease_name]]
                disease_attribute_output_list.append(write_str)
            else:
                pass
        else:
            disease_not_found_test_list.append(disease_name)

    return disease_attribute_output_list, disease_not_found_test_list


def write_list_to_file(list_to_write, f_out):
    total_num = len(list_to_write)
    with codecs.open(f_out, 'w', 'utf8') as f:
        cnt_line = 0
        for str_name in list_to_write:
            cnt_line += 1
            if cnt_line != total_num:
                f.write(str_name + '\n')
            else:
                f.write(str_name)


def update_disease_name_acc_to_change_disease_file(original_disease_x_attribute_file,
                                                   change_disease_file,
                                                   updated_disease_x_attribute_file,
                                                   disease_is_ahead=True):
    disease_change_name_dic = dict()
    split_pattern = re.compile(r"(<->.*?<->)")
    updated_line_list = list()

    with codecs.open(change_disease_file, 'r', 'utf8') as f:
        for line in f:
            line = line.strip()
            line_list = line.split('<->')
            assert len(line_list) == 2, line
            old_name, new_name = line_list[:2]
            disease_change_name_dic[old_name] = new_name

    with codecs.open(original_disease_x_attribute_file, 'r', 'utf8') as f:
        for line in f:
            line = line.strip()
            line_list = re.split(split_pattern, line)
            assert len(line_list) == 3, line
            disease_name = line_list[0] if disease_is_ahead else line_list[2]
            if disease_name in disease_change_name_dic:
                disease_name = disease_change_name_dic[disease_name]

            if disease_is_ahead:
                updated_line = disease_name + line_list[1] + line_list[2]
            else:
                updated_line = line_list[0] + line_list[1] + disease_name

            updated_line_list.append(updated_line)

    write_list_to_file(updated_line_list, updated_disease_x_attribute_file)


# def compare_two_list_according_edit_distance(drug_list_standard, drug_list_to_compare):
#     drug_list_standard_sort = sorted(drug_list_standard, key=len, reverse=True)
#     max_len = len(drug_list_standard_sort[0])
#
#     drug_list_to_check = []
#
#     for edit_distance_threshold in range(max_len):
#         if edit_distance_threshold == 0:
#             set_to_remove = set()
#             for drug_str in drug_list_standard_sort:
#                 for drug_to_compare in drug_list_to_compare:
#                     if Levenshtein.distance(drug_str, drug_to_compare) == edit_distance_threshold:
#                         drug_list_to_check.append(drug_str+'------'+drug_to_compare)
#                         set_to_remove.add(drug_to_compare)
#             drug_list_to_compare = list(set(drug_list_to_compare) - set_to_remove)
#
#         else:
#             for drug_str in drug_list_standard_sort:
#                 if len(drug_str) >= 2 + edit_distance_threshold:
#                     set_to_remove = set()
#                     for drug_to_compare in drug_list_to_compare:
#                         if Levenshtein.distance(drug_to_compare, drug_str) == edit_distance_threshold:
#                             drug_list_to_check.append(drug_str+'------'+drug_to_compare)
#                             set_to_remove.add(drug_to_compare)
#                     drug_list_to_compare = list(set(drug_list_to_compare) - set_to_remove)
#
#     for drug_name in drug_list_to_compare:
#         drug_list_to_check.append(drug_name)
#
#     return drug_list_to_check


def compare_two_entity_list_with_edit_distance(stand_source_file,
                                               second_source_file,
                                               synonym_file=None,
                                               threshold=2):
    """
    根据同义词文件、编辑距离比较同一实体两个不同来源数据的异同
    :param stand_source_file: 标准实体名称文件，每行一个实体名称
    :param second_source_file: 另外来源的实体名称文件，每行一个实体名称
    :param synonym_file: 同义词文件，格式为“实体名1 实体名2 实体名3 ...... 实体名n”
    :param threshold: 编辑距离的阈值
    :return: 比较结果的输出列表
    """

    output_list = list()

    stand_entity_list = list()
    second_source_list = list()
    with codecs.open(stand_source_file, 'r', 'utf8') as f:
        for line in f:
            line = line.strip()
            stand_entity_list.append(line)

    with codecs.open(second_source_file, 'r', 'utf8') as f:
        for line in f:
            line = line.strip()
            second_source_list.append(line)

    entity_to_remove = set()
    for entity in second_source_list:
        if entity in stand_entity_list:
            entity_to_remove.add(entity)
            entity_synonym_str = entity+'<->'+entity
            output_list.append(entity_synonym_str)

    # 去除与标准列表中完全相同的实体名称
    second_source_list = list(set(second_source_list) - entity_to_remove)

    if synonym_file is not None:
        # 如果有同义词表，根据同义词表去掉意义完全相同的实体名称
        with codecs.open(synonym_file, 'r', 'utf8') as f:
            for line in f:
                line = line.strip()
                line_list = line.split('<->')
                line_list = [content.strip() for content in line_list]

                for entity_name in line_list:
                    if entity_name in second_source_list:
                        for stand_entity_name in line_list:
                            if stand_entity_name in stand_entity_list:
                                entity_synonym_str = stand_entity_name + '<->' + entity_name
                                output_list.append(entity_synonym_str)
                                second_source_list.remove(entity_name)
                                break
                    else:
                        pass

                # entity_left, entity_right = line_list[:2]
                # if entity_left in second_source_list:
                #     if entity_right in stand_entity_list:
                #         entity_synonym_str = entity_right + '<->' + entity_left
                #         output_list.append(entity_synonym_str)
                #         second_source_list.remove(entity_left)
                # elif entity_right in second_source_list:
                #     if entity_left in stand_entity_list:
                #         entity_synonym_str = entity_left + '<->' + entity_right
                #         output_list.append(entity_synonym_str)
                #         second_source_list.remove(entity_right)
                # else:
                #     pass

    # 剩下的不能找到同义词的实体名称根据编辑距离来寻找相似实体
    stand_entity_list = sorted(stand_entity_list, key=len, reverse=True)
    max_len = len(stand_entity_list[0])
    for edit_distance_threshold in range(1, max_len):
        for entity_str in stand_entity_list:
            if len(entity_str) >= threshold + edit_distance_threshold:
                set_to_remove = set()
                for entity_to_compare in second_source_list:
                    if Levenshtein.distance(entity_to_compare, entity_str) <= edit_distance_threshold:
                        entity_similar_str = entity_str + '||||||' + entity_to_compare
                        output_list.append(entity_similar_str)
                        set_to_remove.add(entity_to_compare)

                second_source_list = list(set(second_source_list) - set_to_remove)

    # 如果还剩下没有匹配上的，直接输出
    for entity in second_source_list:
        output_list.append(entity)

    return output_list


def sort_stop_words(stop_word_file):
    output_list = set()
    with codecs.open(stop_word_file, 'r', 'utf8') as f:
        for line in f:
            line = line.strip()
            if line == '':
                continue
            output_list.add(line)

    output_list = sorted(list(output_list), key=len)
    return output_list


def get_yixuexingfuci(all_symptom_file, all_disease_file):
    output_list = list()

    def get_line_list(file_in, cnt_start=1):
        """
        :param file_in: 数据文件，一行一个数据
        :param cnt_start: 从第几行开始读取
        :return:
        """
        out_list = list()
        cnt = 0
        with codecs.open(file_in, 'r', 'utf8') as f:
            for line in f:
                cnt += 1
                if cnt < cnt_start:
                    continue
                line = line.strip()
                if line == '':
                    continue
                out_list.append(line)
        return out_list

    symptom_list = get_line_list(all_symptom_file)
    diseae_list = get_line_list(all_disease_file)

    re_pattern = re.compile('(.+性).+')
    for symptom in symptom_list:
        if re.match(re_pattern, symptom):
            tmp_word = re.match(re_pattern, symptom).group(1)
            if len(tmp_word) < 10:
                output_list.append(tmp_word)
                if tmp_word.find('性') != len(tmp_word) - 1:
                    tmp_word_list = tmp_word.split('性')
                    tmp_word_list = tmp_word_list[:-1]
                    for tmp_word_item in tmp_word_list:
                        print(tmp_word_item + '性'+'----'+tmp_word)

                        output_list.append(tmp_word_item+'性')

    for disease in diseae_list:
        if re.match(re_pattern, disease):
            tmp_word = re.match(re_pattern, disease).group(1)
            if len(tmp_word) < 10:
                output_list.append(tmp_word)

                if tmp_word.find('性') != len(tmp_word) - 1:
                    tmp_word_list = tmp_word.split('性')
                    tmp_word_list = tmp_word_list[:-1]
                    for tmp_word_item in tmp_word_list:
                        output_list.append(tmp_word_item+'性')

    return list(set(output_list))


def find_synonym_entity_one_file(entity_name_file,
                                 medical_stop_words_file,
                                 medical_position_words_file,
                                 medical_level_file,
                                 medical_file,
                                 synonym_file,
                                 organ_attribute_file):
    """
    从一个实体文件中找到同义词、近义词
    :param entity_name_file: 实体名称列表
    :param medical_stop_words_file: 医学停用词表
    :param medical_position_words_file: 医学方位副词表
    :param medical_level_file: 医学程度副词表
    :param medical_file: 医学性副词表
    :param synonym_file: 同义词、近义词表
    :param organ_attribute_file: 器官名称列表
    :return: None
    """

    def get_line_list(file_in, cnt_start=1):
        """
        :param file_in: 数据文件，一行一个数据
        :param cnt_start: 从第几行开始读取
        :return:
        """
        out_list = list()
        cnt = 0
        with codecs.open(file_in, 'r', 'utf8') as f:
            for line in f:
                cnt += 1
                if cnt < cnt_start:
                    continue
                line = line.strip()
                if line == '':
                    continue
                out_list.append(line)
        return list(set(out_list))

    # 停用词表
    stop_words_list = get_line_list(medical_stop_words_file)
    stop_words_list = sorted(stop_words_list, key=len, reverse=True)

    # 医学方位副词表
    position_words_list = get_line_list(medical_position_words_file)
    position_words_list = sorted(position_words_list, key=len, reverse=True)

    # 医学程度副词表
    level_words_list = get_line_list(medical_level_file)
    level_words_list = sorted(level_words_list, key=len, reverse=True)

    # 医学性副词表
    medical_words_list = get_line_list(medical_file)
    medical_words_list = sorted(medical_words_list, key=len, reverse=True)

    # 器官列表
    organ_list = get_line_list(organ_attribute_file, 4)
    organ_list = sorted(organ_list, key=len, reverse=True)

    # 实体列表
    entity_name_list = get_line_list(entity_name_file)
    entity_name_list = sorted(entity_name_list, key=len, reverse=True)

    # 处理停用词
    entity_no_stop_dic = dict()
    for entity_name in entity_name_list:
        no_stop_entity = entity_name
        for stop_word in stop_words_list:
            if stop_word in no_stop_entity:
                no_stop_entity = no_stop_entity.replace(stop_word, '')
        # print(no_stop_entity)
        entity_no_stop_dic[entity_name] = no_stop_entity

    # 得到去掉停用词以后完全相同的词语，我们认为停用词去除后完全相同则意义完全相同
    same_mean_list_list = list()
    sorted_items = sorted(entity_no_stop_dic.items(), key=lambda x: x[1], reverse=True)
    # for item in sorted_items:
    #     print(item)

    pre_value = None
    pre_list = list()
    for item in sorted_items:
        if not pre_value:
            pre_value = item[1]
            pre_list.append(item[0])
        else:
            if item[1] == pre_value:
                pre_list.append(item[0])
                entity_no_stop_dic.pop(item[0])
            else:
                pre_value = item[1]
                if len(pre_list) > 1:
                    same_mean_list_list.append(pre_list)
                pre_list = list()
                pre_list.append(item[0])

    # 处理医学方位副词、程度副词以及医学性副词
    for (key, value) in entity_no_stop_dic.items():
        new_value = value
        for position_word in position_words_list:
            if position_word in new_value:
                new_value = new_value.replace(position_word, '')
                break

        for level_word in level_words_list:
            if level_word in new_value:
                new_value = new_value.replace(level_word, '')
                break

        for medical_word in medical_words_list:
            if medical_word in new_value:
                new_value = new_value.replace(medical_word, '')
                break

        entity_no_stop_dic[key] = new_value

    # 得到去掉方位副词、程度副词以及医学性副词后完全相同的词语，我们认为此时相同的词语意义相近
    synonym_list_list = list()
    sorted_items = sorted(entity_no_stop_dic.items(), key=lambda x: x[1], reverse=True)
    pre_value = None
    pre_list = list()
    for item in sorted_items:
        if not pre_value:
            pre_value = item[1]
            pre_list.append(item[0])
        else:
            if item[1] == pre_value:
                pre_list.append(item[0])
                entity_no_stop_dic.pop(item[0])
            else:
                pre_value = item[1]
                if len(pre_list) > 1:
                    synonym_list_list.append(pre_list)
                pre_list = list()
                pre_list.append(item[0])

    # 剩下的按照编辑距离进行相似性计算，这部分需要人工check
    synonym_words_list_to_check = list()
    entity_name_list = list(entity_no_stop_dic.keys())
    entity_name_no_stop_words_list = list(entity_no_stop_dic.values())

    entity_name_list_cp = entity_name_list.copy()
    entity_name_no_stop_words_list_cp = entity_name_no_stop_words_list.copy()

    def find_organs(entity_str, organ_str_list):
        organs_found = list()
        for organ_str in organ_str_list:
            if entity_str == '':
                break
            if organ_str in entity_str:
                organs_found.append(organ_str)
                entity_str.replace(organ_str, '')
        return organs_found

    for entity_name, entity_name_no_stop_word in zip(entity_name_list, entity_name_no_stop_words_list):
        entity_name_organ_found = find_organs(entity_name, organ_list)
        for entity_name_cp, entity_name_no_stop_word_cp in zip(entity_name_list_cp,
                                                               entity_name_no_stop_words_list_cp):

            entity_name_cp_organ_found = find_organs(entity_name_cp, organ_list)
            if len(entity_name_organ_found) == 0 and len(entity_name_cp_organ_found) == 0 or \
                    entity_name_organ_found == entity_name_cp_organ_found:
                if Levenshtein.jaro_winkler(entity_name_no_stop_word, entity_name_no_stop_word_cp) > 0.6667 and \
                                Levenshtein.distance(entity_name_no_stop_word, entity_name_no_stop_word_cp) < \
                                min(len(entity_name_no_stop_word), len(entity_name_no_stop_word_cp)) - 2 and \
                                Levenshtein.ratio(entity_name_no_stop_word, entity_name_no_stop_word_cp) > 0.5:
                    if entity_name == entity_name_cp:
                        continue
                    else:
                        if entity_name in entity_name_list_cp:
                            entity_name_list_cp.remove(entity_name)
                            entity_name_no_stop_words_list_cp.remove(entity_name_no_stop_word)
                        final_index = Levenshtein.jaro_winkler(entity_name_no_stop_word,
                                                               entity_name_no_stop_word_cp) * 0.5 + \
                                      Levenshtein.ratio(entity_name_no_stop_word, entity_name_no_stop_word_cp) * 0.5
                        synonym_words_list_to_check.append((entity_name, entity_name_cp, final_index))
                        break

    synonym_words_list_to_check = sorted(synonym_words_list_to_check, key=lambda x: x[2], reverse=True)

    entity_found_set = set()

    for entity_tuple in synonym_words_list_to_check:
        entity_found_set.add(entity_tuple[0])
        entity_found_set.add(entity_tuple[1])

    entity_not_found_list = list(set(entity_name_list) - entity_found_set)

    synonym_words_list_to_check = ['||||'.join([item[0], item[1], str(item[2])]) for item in synonym_words_list_to_check]

    with codecs.open(synonym_file, 'w', 'utf8') as f:
        for line in same_mean_list_list:
            f.write('=='.join(line) + '\n')
        for line in synonym_list_list:
            f.write('<->'.join(line) + '\n')
        for line in synonym_words_list_to_check:
            f.write(line + '\n')
        for line in entity_not_found_list:
            f.write(line + '\n')


def find_synonym_entity_two_files(entity_name_file,entity_name_file_with_class,stop_words_file,prefix_stop_words_file,suffix_stop_words_file,synonym_file):
    """
    根据停用词表和编辑距离，找出同/近义词实体
    :param entity_name_file: 实体列表文件(没有对应分类)
    :param entity_name_file_with_class: 实体列表文件(有对应分类)
    :param stop_words_file: 停用词文件
    :param prefix_stop_words_file: 前缀停用词表
    :param suffix_stop_words_file: 后缀停用词表
    :return: 近义词候选列表
    """
    def get_line_list(file_in, cnt_start=1):
        """
        :param file_in: 数据文件，一行一个数据
        :param cnt_start: 从第几行开始读取
        :return:
        """
        out_list = list()
        cnt = 0
        with codecs.open(file_in, 'r', 'utf8') as f:
            for line in f:
                cnt += 1
                if cnt < cnt_start:
                    continue
                line = line.strip()
                if line == '':
                    continue
                out_list.append(line)
        return out_list
        # 停用词表

    stop_words_list = get_line_list(stop_words_file)
    stop_words_list = sorted(stop_words_list, key = len, reverse = True)

    # 前缀停用词表
    prefix_stop_words_list = get_line_list(prefix_stop_words_file)
    prefix_stop_words_list = sorted(prefix_stop_words_list, key = len, reverse = True)

    # 后缀停用词表
    suffix_stop_words_list = get_line_list(suffix_stop_words_file)
    suffix_stop_words_list = sorted(suffix_stop_words_list, key = len, reverse = True)

    entity_name_list = get_line_list(entity_name_file)
    entity_name_list = sorted(entity_name_list, key = len, reverse = True)
    entity_name_with_class_list = get_line_list(entity_name_file_with_class)
    entity_name_with_class_list = sorted(entity_name_with_class_list, key = len, reverse = True)

    very_sure_synonym_words = list()
    # l = entity_name_with_class_list.copy()
    # for y in set(entity_name_with_class_list):
    #     l.remove(y)
    # print(l)
    entity_name_with_class_list = list(set(entity_name_with_class_list))
    for entity_name in entity_name_list.copy():
        for entity_name_has_class in entity_name_with_class_list.copy():
            if entity_name == entity_name_has_class:
                very_sure_synonym_words.append((entity_name,entity_name_has_class))
                if entity_name in entity_name_list:
                    entity_name_list.remove(entity_name)

    # 获取去除前缀停用词、后缀停用词、停用词后的实体列表
    entity_name_no_stop_words_list = list()
    entity_name_file_with_class_no_stop_words_list = list()
    for entity_name in entity_name_list:
        # 处理前缀停用词
        for prefix_stop_word in prefix_stop_words_list:
            if re.match(prefix_stop_word, entity_name):
                entity_name = entity_name.replace(prefix_stop_word, '', 1)
                break

        # 处理后缀停用词
        for suffix_stop_word in suffix_stop_words_list:
            if entity_name.endswith(suffix_stop_word):
                entity_name = re.sub(suffix_stop_word + '$', '', entity_name)
                break

        # 处理停用词
        for stop_word in stop_words_list:
            if stop_word in entity_name:
                entity_name = entity_name.replace(stop_word, '')

        entity_name_no_stop_words_list.append(entity_name)
    assert len(entity_name_list) == len(entity_name_no_stop_words_list)

    for entity_name in entity_name_with_class_list:
        # 处理前缀停用词
        for prefix_stop_word in prefix_stop_words_list:
            if re.match(prefix_stop_word, entity_name):
                entity_name = entity_name.replace(prefix_stop_word, '', 1)
                break

        # 处理后缀停用词
        for suffix_stop_word in suffix_stop_words_list:
            if entity_name.endswith(suffix_stop_word):
                entity_name = re.sub(suffix_stop_word + '$', '', entity_name)
                break

        # 处理停用词
        for stop_word in stop_words_list:
            if stop_word in entity_name:
                entity_name = entity_name.replace(stop_word, '')

        entity_name_file_with_class_no_stop_words_list.append(entity_name)
    assert len(entity_name_with_class_list) == len(entity_name_file_with_class_no_stop_words_list)

    sure_synonym_words = list()
    synonym_words_list_to_check = list()
    middle_list_1 = list()
    middle_list_2 = list()

    for index in range(0,len(entity_name_no_stop_words_list)):
        for index1 in range(0,len(entity_name_file_with_class_no_stop_words_list)):
            entity_name = entity_name_no_stop_words_list[index]
            entity_name_has_class = entity_name_file_with_class_no_stop_words_list[index1]
            final_index = Levenshtein.jaro_winkler(entity_name, entity_name_has_class) * 0.5 + \
                          Levenshtein.ratio(entity_name, entity_name_has_class) * 0.5
            if entity_name == entity_name_has_class:
                sure_synonym_words.append((entity_name_list[index],entity_name_with_class_list[index1]))
                middle_list_1.append(entity_name_list[index])
                break

            elif Levenshtein.jaro_winkler(entity_name, entity_name_has_class) > 0.6667 and \
                    Levenshtein.distance(entity_name, entity_name_has_class) < 3 and \
                    Levenshtein.ratio(entity_name,entity_name_has_class) > 0.5 and final_index> 0.795:
                synonym_words_list_to_check.append((entity_name_list[index],entity_name_with_class_list[index1], final_index))
                middle_list_2.append(entity_name_list[index])
    # assert len(middle_list_2) == len(set(middle_list_2))
    synonym_words_list_to_check = sorted(synonym_words_list_to_check, key=lambda x: x[2], reverse=True)
    synonym_words_list_to_check = ['<->'.join([item[0], item[1], str(item[2])]) for item in synonym_words_list_to_check]
    sure_synonym_words = ['<->'.join([item[0], item[1]]) for item in sure_synonym_words]
    very_sure_synonym_words = ['=='.join([item[0], item[1]]) for item in very_sure_synonym_words]

    with codecs.open(synonym_file, 'w', 'utf8') as f:
        for line in very_sure_synonym_words:
            f.write(line+'\n')
        for line in sure_synonym_words:
            f.write(line + '\n')
        for line in synonym_words_list_to_check:
            f.write(line + '\n')
        for entity_name in entity_name_list:
            if entity_name not in middle_list_1 and entity_name not in middle_list_2:
                f.write(entity_name+'\n')


def entity_del_replace_acc_to_check_file(check_file, entity_file, relation_str):
    """
    根据人工处理的文件，对实体文件进行删除或者替换
    :param check_file: 人工check的结果文件，包含删除和替换的信息
    :param entity_file: 实体文件
    :param relation_str: 实体关系字符串
    :return: 输出列表
    """
    del_list = list()
    replace_dic = dict()
    with codecs.open(check_file, 'r', 'utf8') as f:
        for line in f:
            line = line.strip()
            if line == '':
                continue
            if '<->' in line:
                line_list = line.split('<->', 1)
                line_list = [line_str.strip() for line_str in line_list]
                replace_dic[line_list[0]] = line_list[1]
            else:
                del_list.append(line)

    output_list = list()
    with codecs.open(entity_file, 'r', 'utf8') as f:
        for line in f:
            line = line.strip()
            if line == '':
                continue
            if relation_str in line:
                line_list = line.split(relation_str, 1)
                line_list = [line_str.strip() for line_str in line_list]
                assert len(line_list) == 2
                symptom_name = line_list[1]
                if symptom_name in del_list:
                    continue
                elif symptom_name in replace_dic:
                    output_str = line_list[0] + relation_str + replace_dic[symptom_name]
                else:
                    output_str = line

                output_list.append(output_str)

    output_list = sorted(list(set(output_list)))
    return output_list


if __name__ == '__main__':
    symptom_entity_file = r'.\data\all_symptoms\final_total_symptom_name.txt'
    medical_file = r'.\data\all_symptoms\骨科\医学性副词表.txt'
    medical_level_file = r'.\data\all_symptoms\骨科\医学程度副词表.txt'
    medical_position_file = r'.\data\all_symptoms\骨科\医学方位副词表.txt'
    medical_stop_word_file = r'.\data\all_symptoms\骨科\医学停用词表.txt'
    organ_attribute_file = r'.\data\all_symptoms\骨科\organ_attribute.txt'
    synonym_file = r'.\data\all_symptoms\entity_synonym.txt'
    find_synonym_entity_one_file(symptom_entity_file, medical_stop_word_file, medical_position_file, medical_level_file,
                                 medical_file, synonym_file, organ_attribute_file)

    # disease_symptom_relation_f = r'.\data\disease_sympoton_relation\final_disease_symptom_relation.txt'
    # disease_symptom_relation_str = '<->disease_with_symptom<->'
    # human_check_result_f = r'.\data\all_symptoms\human_check_total_result.txt'
    # final_disease_symptom_relation_f = r'.\data\disease_sympoton_relation\final_disease_symptom_relation_updated.txt'
    # symptom_symptom_relation_f = r'.\data\all_symptoms\final_symptom_symptom_relation.txt'
    # symptom_symptom_relation_str = '<->part_of_symptom_category<->'
    # final_symptom_symptom_f = r'.\data\all_symptoms\final_symptom_symptom_relation_update.txt'
    # output_list = entity_del_replace_acc_to_check_file(human_check_result_f,
    #                                                    symptom_symptom_relation_f,
    #                                                    symptom_symptom_relation_str)
    # write_list_to_file(output_list, final_symptom_symptom_f)





