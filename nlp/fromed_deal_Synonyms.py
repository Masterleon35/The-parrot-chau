import re
import codecs
import Levenshtein

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

    for index in range(0,len(entity_name_no_stop_words_list))
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

if __name__ == '__main__':
    find_synonym_entity_two_files('/pycharm/result file/reason_list.txt','/pycharm/text file/new_cause_attribute.txt',
                                  '/pycharm/text file/stop_words.txt','/pycharm/text file/prefix_stopwords.txt',
                                  '/pycharm/text file/suffix_stopwords.txt','/pycharm/result file/match_plus_plus.txt'
                                  )
