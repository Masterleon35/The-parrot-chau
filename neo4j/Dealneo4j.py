from py2neo import Graph, Relationship, NodeSelector
import codecs
import pdb
import sys
import re
import collections
import getpass
from pandas import DataFrame


# -*-coding:utf-8 -*-


def init_database(address, username, password):
    """
    todo: to initialize the graph database
    :param address: address for the database
    :param username: username for login
    :param password: password for the username
    :return: the initialized database
    """
    graph_db = Graph(
         address,
         username=username,
         password=password
     )
    return graph_db


def clear_database(graph_name: Graph):
    """
    todo: clear all of the contents in the graph database
    :param graph_name: the initialized graph database
    :return: None
    """
    yes_or_no = input('do you really want to clear the database')
    if yes_or_no == 'yes' or yes_or_no == 'y':
        graph_name.delete_all()
        print('the graph database has been cleared')
    else:
        pass
        print('the graph database has not been cleared')

    return None


def create_node(graph_name: Graph, label: str, **kwargs):
    """
    todo: crate a node with some properties in the graph database
    :param graph_name: the initialized graph database
    :param label: the label for the node
    :param kwargs: properties for the node
    :return: the created node
    """
    create_str = "Create (n:" + label
    if len(kwargs) == 0:
        create_str += ')'

    else:
        create_str += ' {'
        properties_list = []
        for (key, value) in kwargs.items():
            if "||||" not in value:
                # normal string attribute
                property_str = key + " :'" + value + "'"
            else:
                # array attribute
                value_list = value.split('||||')
                property_str = key + " :["
                value_item_list = []
                for value_item in value_list:
                    value_item_list.append("'" + value_item + "'")

                property_str += ','.join(value_item_list)
                property_str += "]"

            properties_list.append(property_str)
        create_str += ','.join(properties_list)
        create_str += '})'

    return graph_name.run(create_str)


def update_nodes(graph_name: Graph, label: str, **kwargs):
    """
    todo: update the ndoes with some properties
    :param graph_name: the initialized graph database
    :param label: the label for the node
    :param kwargs: properties for the node
    :return: the updated node
    """
    node_name = kwargs['name']

    properties_list = []
    update_str = "Match (n:" + label + " {name:'" + node_name + "'}) SET n={"

    for (key, value) in kwargs.items():
        property_str = key + " :'" + value + "'"
        properties_list.append(property_str)

    update_str += ','.join(properties_list)
    update_str += '}'

    return graph_name.run(update_str)


def select_nodes(graph_db: Graph):
    selector = NodeSelector(graph_db)
    diseases = selector.select('Disease').first()
    print(diseases)


def match_node_in_label_with_properties(graph_name: Graph, label: str, **kwargs):
    """
    todo: match some nodes under the label with some properties
    :param graph_name: the initialized graph database
    :param label: the label the nodes belong to for matching
    :param kwargs: properties for matching
    :return: the matched nodes
    """
    match_str = "Match (n:" + label
    if len(kwargs) == 0:
        match_str += ') Return n'
    else:
        match_str += ' {'
        properties_list = []
        for (key, value) in kwargs.items():
            property_str = key + " :'" + value + "'"
            properties_list.append(property_str)
        match_str += ','.join(properties_list)
        match_str += '}) Return n'
    # print(match_str)
    matched_node = graph_name.run(match_str).data()
    if matched_node:
        return matched_node[0]['n']
    else:
        return None


def match_node_with_properties(graph_name: Graph, **kwargs):
    """
    todo: match some nodes with some properties
    :param graph_name: the initialized graph database
    :param kwargs: properties for matching
    :return: the matched nodes
    """
    match_str = "Match (n:"

    if len(kwargs) == 0:
        match_str += ') Return n'
    else:
        match_str += ' {'
        properties_list = []
        for (key, value) in kwargs.items():
            property_str = key + " :'" + value + "'"
            properties_list.append(property_str)
        match_str += ','.join(properties_list)
        match_str += '}) Return n'
    return graph_name.run(match_str).data()[0]['n']


def match_all_graph(graph_name: Graph):
    """
    todo: match all nodes in the graph database
    :param graph_name: the initialized graph database
    :return: matched nodes
    """
    match_str = "Match (n) return n"
    return graph_name.run(match_str).data()


def create_relation(graph_name: Graph, node_1_matched, node_2_matched, relation, **kwargs):
    """
    todo: create relations with some properties within two nodes
    :param graph_name: the initialized graph database
    :param node_1: the first node within the relation
    :param node_2: the second node within the relation
    :param relation: the label for the relation
    :param kwargs: some perperties for the realation
    :return: created relation
    """
    # create_str = "Create " + node_1 + "-[r:"+relation+']->'+node_2
    relation_create = Relationship(node_1_matched, relation, node_2_matched)
    return graph_name.create(relation_create)


def match_relation_nodes_to_label(graph_name: Graph, label):
    """
    todo: match the nodes which have relations to the label
    :param graph_name:
    :param label:
    :return: the matched nodes
    """
    match_str = "match(n)--(m:"+label+")"
    return graph_name.run(match_str).data()[0]['n']


def create_nodes_from_file(graph_db: Graph, attribute_file: str):
    """
    todo: create the nodes from the file
    :param graph_db: the initialized graph
    :param attribute_file: attributes file for the node
    :return: number for the nodes created
    """
    with codecs.open(attribute_file, 'r', 'utf8') as f:
        attribute_line_list = f.readlines()
        node_label, english_header, chinese_header = attribute_line_list[:3]
        english_attributes = english_header.split('#@@#')
        english_attributes_list = [attr.strip() for attr in english_attributes]
        node_name_set = set()

        replace_list = ["'", "\\", "]", "["]
        for line in attribute_line_list[3:]:
            for replace_item in replace_list:
                if replace_item in line:
                    line = line.replace(replace_item, '')

            node_attr_list = line.strip().split('#@@#')
            node_attr_list = [node_attr.strip() for node_attr in node_attr_list]

            assert len(node_attr_list) == len(english_attributes_list), line
            node_name = node_attr_list[0]
            if node_name in node_name_set:
                continue
            else:
                node_name_set.add(node_name)
                tmp_dic = collections.OrderedDict()
                for key, value in zip(english_attributes_list, node_attr_list):
                    tmp_dic[key] = value
                create_node(graph_db, node_label, **tmp_dic)

    graph_db.run("CREATE CONSTRAINT on (n :" + node_label + ") ASSERT n.name IS UNIQUE")
    return len(node_name_set)


def update_nodes_from_file(graph_db: Graph, update_attribute_file: str):
    """
    todo: update the attributes of nodes
    :param graph_db: the initialized graph database
    :param update_attribute_file: the update_attribute_file
    :return: the  number of nodes updated
    """
    with codecs.open(update_attribute_file, 'r', 'utf8') as f:
        attribute_line_list = f.readlines()
        node_label, english_header, chinese_header = attribute_line_list[:3]
        english_attributes = english_header.split('#@@#')
        english_attributes_list = [attr.strip() for attr in english_attributes]
        node_name_set = set()

        for line in attribute_line_list[3:]:
            node_attr_list = line.strip().split('#@@#')
            node_attr_list = [node_attr.strip() for node_attr in node_attr_list]
            assert len(node_attr_list) == len(english_attributes_list), line
            node_name = node_attr_list[0]
            if node_name in node_name_set:
                continue
            else:
                node_name_set.add(node_name)
                tmp_dic = collections.OrderedDict()
                for key, value in zip(english_attributes_list, node_attr_list):
                    tmp_dic[key] = value

                node_matched = match_node_in_label_with_properties(graph_db, node_label, name=node_name)

                if node_matched:
                    update_nodes(graph_db, node_label, **tmp_dic)
                else:
                    create_node(graph_db, node_label, **tmp_dic)

    return len(node_name_set)


def create_entity_relation_from_file(graph_db: Graph, cross_entity_relation_file: str,
                                     relation_label, head_node_label, tail_node_label):

    """
    todo: create the relation between two entities
    :param graph_db: the initialized graph database
    :param cross_entity_relation_file: the relation file fro two cross entities
    :param relation_label: relation label between two entities
    :param head_node_label: node label for first entity
    :param tail_node_label: node label fro second entity
    :return: number of relations created
    """
    cnt_relation = 0
    with codecs.open(cross_entity_relation_file, 'r', 'utf8') as f:
        for line in f:
            line_list = line.strip().split('<->'+relation_label+'<->')
            head_node_name, tail_node_name = line_list[0].strip(), line_list[1].strip()
            node_head = match_node_in_label_with_properties(graph_db, head_node_label, name=head_node_name)
            node_tail = match_node_in_label_with_properties(graph_db, tail_node_label, name=tail_node_name)
            if node_head and node_tail:
                cnt_relation += 1
                create_relation(graph_db, node_head, node_tail, relation_label)
            elif not node_head and node_tail:
                pass
                # print('head node %s not found, and only found tail node %s' % (head_node_name, tail_node_name))
            elif not node_tail and node_head:
                pass
                # print('tail node %s not found, and only found tail node %s' % (tail_node_name, head_node_name))
            else:
                pass
                # print('head node %s and tail node %s both not found' % (head_node_name, tail_node_name))

    return cnt_relation


def create_node_csv(path_read, path_write):
    """
    :param path_read: 节点的原属性文件
    :param path_write: 构造的节点文件的路径。csv格式
    """
    label_translate = {'Drug': u'药品', 'Disease': u'疾病', 'Office': u'科室', 'Organ': u'器官', 'Cause': u'病因',
                       'Symptom': u'症状', 'Test': u'检查'}

    def get_index_need_array(file_path):
        """
        :param file_path: 原始节点文件路径
        :return: 一个列表包含了哪些属性需要设置为string_array。ps:存储着的是索引值
        """
        index_list = []
        with codecs.open(file_path, 'r', 'utf8')as f:
            for line in f:
                line = line.strip()
                if line == '':
                    continue
                list1 = line.split('#@@#')
                for item in list1:
                    if '||||' in item and list1.index(item) not in index_list:
                        index_list.append(list1.index(item))
        return sorted(index_list)

    f_out = codecs.open(path_write, 'w', 'utf8')

    with codecs.open(path_read, 'r', 'utf8') as f:
        need_array_attribute_list = get_index_need_array(path_read)
        count = -1
        synonym_name_index = -1
        for line in f:
            line = line.strip()
            if line == '':
                continue

            count += 1
            if count == 0:
                class_node = line
            elif count == 1:
                english_header = line
                columns_list = english_header.split('#@@#')
                if 'SynonymNames' in columns_list:
                    synonym_name_index = columns_list.index('SynonymNames')

                for index in need_array_attribute_list:
                    columns_list[index] += ':string_array'
                columns_string = '\t'.join(columns_list)
                f_out.write('class:label\t' + 'id_' + class_node.lower() + ':string:' + class_node.title()
                            + 'id' + '\t'+columns_string+'\n')
            elif count > 2:
                attribute_list = line.split('#@@#')
                attribute_list = [attribute_item.replace('#', '') for attribute_item in attribute_list]
                attribute_list = [attribute_item.replace('||||', '#') for attribute_item in attribute_list]
                if synonym_name_index > 0:
                    # 处理别名属性中用"、"作为分隔符的情况
                    attribute_list[synonym_name_index] = attribute_list[synonym_name_index].replace('、', '#')

                # 将英文引号替换成中文引号，解决csv文件因为引号而中断导入的问题
                attribute_list = [attribute_item.replace("\"", "“") for attribute_item in
                                  attribute_list]

                attribute_list.insert(0, label_translate[class_node])
                attribute_list.insert(1, str(count-2))
                attribute_string = '\t'.join(attribute_list)
                f_out.write(attribute_string+'\n')
            else:
                # chinese_header
                pass
    f_out.close()


def create_relation_csv(node_first_csv, node_second_csv, raw_relation_file, relation_csv_file):
    """
    将关系文件转化成csv文件格式
    :param node_first_csv: 第一个节点对应的csv文件格式
    :param node_second_csv: 第二个节点对应的csv文件格式
    :param raw_relation_file: 原始的关系文件
    :param relation_csv_file: 输出的关系csv文件
    :return: None
    """

    def get_node_info_from_file(node_csv_file):
        count = 0
        index_name = None
        node_info_list = list()
        with codecs.open(node_csv_file, 'r', 'utf8')as f:
            for line in f:
                line = line.strip()
                if line == '':
                    continue
                if count == 0:
                    has_synonym_names = False
                    line_list = line.split('\t')
                    index_name = line_list[1]
                    if 'SynonymNames' in line:
                        has_synonym_names = True
                        index_synonym_names = line_list.index('SynonymNames:string_array')
                else:
                    line_list = line.split('\t')
                    if has_synonym_names:
                        if '#' in line_list[index_synonym_names]:
                            node_info = line_list[1:3] + line_list[index_synonym_names].split('#')
                        elif '、' in line_list[index_synonym_names]:
                            # 处理药品别名
                            node_info = line_list[1:3] + line_list[index_synonym_names].split('、')
                        else:
                            node_info = line_list[1:3]
                            node_info.append(line_list[index_synonym_names])
                    else:
                        node_info = line_list[1:3]
                    node_info_list.append(node_info)
                count += 1
        return index_name, node_info_list
    if node_first_csv != node_second_csv:
        first_node_index_name, first_node_info = get_node_info_from_file(node_first_csv)
        second_node_index_name, second_node_info = get_node_info_from_file(node_second_csv)
    else:
        first_node_index_name, first_node_info = get_node_info_from_file(node_first_csv)
        second_node_index_name, second_node_info = first_node_index_name, first_node_info
    raw_relation_list = list()
    with codecs.open(raw_relation_file, 'r', 'utf8')as w:
        for line in w:
            line = line.strip()
            if line == '':
                continue
            # 对关系原文件进行操作。将每行用<->分割为列表，再存入need_to_change列表中
            line_list = line.split('<->')
            # 将英文引号替换成中文引号，解决csv文件导入时由于英文引号造成的中断
            line_list = [line_str.strip().replace("\"", "\“") for line_str in line_list]
            raw_relation_list.append(line_list)

    with codecs.open(relation_csv_file, 'w', 'utf8')as f_out:
        f_out.write(first_node_index_name + '\t' + second_node_index_name + '\t' + 'type' + '\n')
        for need_change_info_list in raw_relation_list:
            assert len(need_change_info_list) == 3
            first_node_name = need_change_info_list[0]
            second_node_name = need_change_info_list[2]

            # 遍历need_to_change列表
            for first_node_info_item in first_node_info:
                # print(first_node_info_item)
                # 遍历存储id、名称、同义词的第一个列表
                if first_node_name in first_node_info_item:
                    # 如果need_to_change中的名称在第一个列表中则将其替换为id
                    need_change_info_list[0] = first_node_info_item[0]
                    break
            for second_node_info_item in second_node_info:
                # print(second_node_info_item)
                # 同上方操作
                if second_node_name in second_node_info_item:
                    need_change_info_list[2] = second_node_info_item[0]
                    break
            f_out.write(
                need_change_info_list[0] + '\t' + need_change_info_list[2] + '\t' + need_change_info_list[1] + '\n')

    return None


if __name__ == '__main__':
    url_address = "http://172.18.30.88:7474"
    user_name = 'neo4j'
    # user_password = input("please input your password: ")
    # user_password = getpass.getpass("your password: ")
    # graph_db = init_database(url_address, user_name, user_password)
    #
    # # clear the database first, be careful !!!!!
    # clear_database(graph_db)

    disease_ready_neo4j_f = r'.\data\all_disease\final_ready_for_neo4j_total_disease_attribute.txt'
    drug_ready_neo4j_f = r'.\data\all_drugs\final_drug_ready_neo4j.txt'
    cause_ready_neo4j_f = r'.\data\all_causes\final_cause_attribute.txt'
    symptom_ready_neo4j_f = r'.\data\all_symptoms\final_total_symptom_attribute.txt'
    organ_ready_neo4j_f = r'.\data\all_organs\organ_attribute.txt'
    office_ready_neo4j_f = r'.\data\all_office\office_attribute.txt'
    test_ready_neo4j_f = r'.\data\all_test\test_attribute.txt'

    disease_node_csv_f = r'.\data\csv_files\disease_node.csv'
    drug_node_csv_f = r'.\data\csv_files\drug_node.csv'
    cause_node_csv_f = r'.\data\csv_files\cause_node.csv'
    symptom_node_csv_f = r'.\data\csv_files\symptom_node.csv'
    organ_node_csv_f = r'.\data\csv_files\organ_node.csv'
    office_node_csv_f = r'.\data\csv_files\office_node.csv'
    test_node_csv_f = r'.\data\csv_files\test_node.csv'

    disease_drug_relation_f = r'.\data\disease_drug_relation\final_disease_drug_relation.txt'
    disease_office_relation_f = r'.\data\disease_office_relation\disease_office_relation.txt'
    disease_organ_relation_f = r'.\data\disease_organ_relation\disease_organ_relation_sure.txt'
    disease_cause_relation_f = r'.\data\disease_cause_relation\final_disease_cause_relation.txt'
    disease_symptom_relation_f = r'.\data\disease_sympoton_relation\final_disease_symptom_relation_update_updated.txt'
    disease_test_relation_f = r'.\data\disease_with_test\disease_test_relation.txt'

    disease_drug_relation_csv_f = r'.\data\csv_files\disease_drug_relation.csv'
    disease_office_relation_csv_f = r'.\data\csv_files\disease_office_relation.csv'
    disease_organ_relation_csv_f = r'.\data\csv_files\disease_organ_relation.csv'
    disease_cause_relation_csv_f = r'.\data\csv_files\disease_cause_relation.csv'
    disease_symptom_relation_csv_f = r'.\data\csv_files\disease_symptom_relation.csv'
    disease_test_relation_csv_f = r'.\data\csv_files\disease_test_relation.csv'

    create_node_csv(disease_ready_neo4j_f, disease_node_csv_f)
    create_node_csv(drug_ready_neo4j_f, drug_node_csv_f)
    create_node_csv(cause_ready_neo4j_f, cause_node_csv_f)
    create_node_csv(symptom_ready_neo4j_f, symptom_node_csv_f)
    create_node_csv(organ_ready_neo4j_f, organ_node_csv_f)
    create_node_csv(office_ready_neo4j_f, office_node_csv_f)
    create_node_csv(test_ready_neo4j_f, test_node_csv_f)

    create_relation_csv(disease_node_csv_f,
                        drug_node_csv_f,
                        disease_drug_relation_f,
                        disease_drug_relation_csv_f)

    create_relation_csv(disease_node_csv_f,
                        cause_node_csv_f,
                        disease_cause_relation_f,
                        disease_cause_relation_csv_f)

    create_relation_csv(disease_node_csv_f,
                        symptom_node_csv_f,
                        disease_symptom_relation_f,
                        disease_symptom_relation_csv_f)

    create_relation_csv(disease_node_csv_f,
                        test_node_csv_f,
                        disease_test_relation_f,
                        disease_test_relation_csv_f)

    create_relation_csv(disease_node_csv_f,
                        organ_node_csv_f,
                        disease_organ_relation_f,
                        disease_organ_relation_csv_f)

    create_relation_csv(office_node_csv_f,
                        disease_node_csv_f,
                        disease_office_relation_f,
                        disease_office_relation_csv_f)
    create_relation_csv('/usr/local/Cellar/neo4j/batch-import-tool-master/file/disease_node.csv',
                        '/usr/local/Cellar/neo4j/batch-import-tool-master/file/disease_node.csv',
                        '/pycharm/deal file/final_disease_disease_relation.txt',
                        '/pycharm/result file/1.csv'
                        )

























