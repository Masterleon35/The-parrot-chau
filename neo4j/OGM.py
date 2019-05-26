from py2neo.ogm import GraphObject, Property, RelatedTo, RelatedFrom, Related
import codecs
import pdb
import sys
import re
import collections
import getpass
from pandas import DataFrame
from py2neo import Graph
import logging

# -*-coding:utf-8 -*-
#手册 OGM框架解释https://py2neo.org/v3/ogm.html
#OGM的源代码 https://py2neo.org/v3/_modules/py2neo/ogm.html
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


class Disease(GraphObject):
    __primarykey__ = 'name'
    __primarylabel__ = 'Disease'

    # properties
    name = Property()
    EnglishName = Property()
    SynonymNames = Property()
    ClinicFeature = Property()
    Cause = Property()
    Prevention = Property()
    Prognosis = Property()
    Complication = Property()
    Treatment = Property()
    Diagnosis = Property()
    Test = Property()
    ProneGroup = Property()
    Contagion = Property()

    # relations
    drugs = RelatedTo("Drug", "disease_need_drug")
    offices = RelatedFrom("Office", "office_contain_disease")
    symptoms = RelatedTo("Symptom", "disease_with_symptom")
    causes = RelatedTo("Cause", "disease_with_cause")
    tests = RelatedTo("Test", "disease_need_test")
    organs = RelatedTo("Organ", "disease_impact_on_organ")
    upper_diseases = RelatedFrom('Disease', 'part_of_disease_category')
    lower_diseases = RelatedTo('Disease', 'part_of_disease_category')

    properties = [name, EnglishName, SynonymNames]

    def __lt__(self, other):
        return self.name < other.name


class Drug(GraphObject):
    __primarykey__ = 'name'
    __primarylabel__ = 'Drug'

    # properties
    name = Property()
    EnglishName = Property()
    SynonymNames = Property()
    Specifications = Property()
    Indication = Property()
    AdverseReaction = Property()
    Contraindication = Property()
    Use = Property()
    Description = Property()
    DrugInteraction = Property()

    # relations
    drug_fit_disease = RelatedFrom("Disease", "disease_need_drug")
    upper_drugs = RelatedFrom('Drug', 'part_of_drug_category')
    lower_drugs = RelatedTo('Drug', 'part_of_drug_category')

    def __lt__(self, other):
        return self.name < other.name


class Symptom(GraphObject):
    __primarylabel__ = 'Symptom'
    __primarykey__ = 'name'

    # properties
    name = Property()

    # relations
    symptom_fit_disease = RelatedFrom("Disease", 'disease_with_symptom')
    upper_symptoms = RelatedFrom('Symptom', 'part_of_symptom_category')
    lower_symptoms = RelatedTo('Symptom', 'part_of_symptom_category')

    def __lt__(self, other):
        return self.name < other.name


class Cause(GraphObject):
    __primarylabel__ = 'Cause'
    __primarykey__ = 'name'

    # properties
    name = Property()

    # relations
    cause_fit_disease = RelatedFrom("Disease", 'disease_with_cause')
    upper_causes = RelatedFrom('Cause', 'part_of_cause_category')
    lower_causes = RelatedFrom('Cause', 'part_of_cause_category')

    def __lt__(self, other):
        return self.name < other.name


class Office(GraphObject):
    __primarykey__ = 'name'
    __primarylabel__ = 'Office'

    # properties
    name = Property()

    # relations
    office_contain_disease = RelatedTo("Disease", 'office_contain_disease')
    upper_offices = RelatedFrom('Office', 'part_of_office_category')
    lower_offices = RelatedTo('Office', 'part_of_office_category')

    def __lt__(self, other):
        return self.name < other.name


class Organ(GraphObject):
    __primarylabel__ = 'Organ'
    __primarykey__ = 'name'

    # properties
    name = Property()

    # relations
    organ_with_disease = RelatedFrom("Disease", 'disease_impact_on_organ')
    upper_organs = RelatedFrom('Organ', 'part_of_organ_category')
    lower_organs = RelatedTo('Organ', 'part_of_organ_category')

    def __lt__(self, other):
        return self.name < other.name


class Test(GraphObject):
    __primarykey__ = 'name'
    __primarylabel__ = 'Test'

    # properties
    name = Property()

    # relations
    test_fit_disease = RelatedFrom("Disease", 'disease_need_test')
    upper_tests = RelatedFrom('Test', 'part_of_test_category')
    lower_tests = RelatedTo('Test', 'part_of_test_category')

    def __lt__(self, other):
        return self.name < other.name


def search_disease_acc_to_office(graph, office_name):
    office_node = Office.select(graph, office_name).first()
    if not office_node:
        return []
    diseases = [item.name for item in office_node.office_contain_disease]
    return diseases


def search_symptom_acc_to_disease(graph, disease_name):
    disease_node = Disease.select(graph, disease_name).first()
    if not disease_node:
        return []

    symptoms = [item.name for item in disease_node.symptoms]
    return symptoms


def search_cause_acc_to_disease(graph, disease_name):
    disease_node = Disease.select(graph, disease_name).first()
    if not disease_node:
        return []
    causes = [item.name for item in disease_node.causes]
    return causes


def search_drug_acc_to_disease(graph, disease_name):
    disease_node = Disease.select(graph, disease_name)
    if not disease_node:
        return []
    drugs = [item.name for item in disease_node.drugs]
    return drugs

def search_offices_acc_to_disease(graph,disease_name):
    disease_node = Disease.select(graph, disease_name)
    if not disease_node:
        return []
    offices = [item.name for item in disease_node.offices]
    return  offices

def search_organs_acc_to_disease(graph,disease_name):
    disease_node = Disease.select(graph, disease_name)
    if not disease_node:
        return []
    organs = [item.name for item in disease_node.organs]
    return  organs

def search_tests_acc_to_disease(graph,disease_name):
    disease_node = Disease.select(graph, disease_name)
    if not disease_node:
        return []
    tests = [item.name for item in disease_node.tests]
    return  tests

def search_disease_acc_to_symptom(graph, symptom_name):
    symptom_name = Symptom.select(graph, symptom_name).first()
    if not symptom_name:
        return []
    diseases = [item.name for item in symptom_name.symptom_fit_disease]
    return diseases

def search_disease_acc_to_cause(graph, cause_name):
    cause_name = Cause.select(graph, cause_name).first()
    if not cause_name:
        return []
    diseases = [item.name for item in cause_name.cause_fit_disease]
    return diseases

def search_disease_acc_to_organ(graph, organ_name):
    organ_name = Organ.select(graph, organ_name).first()
    if not organ_name:
        return []
    diseases = [item.name for item in organ_name.organ_with_disease]
    return diseases

def search_disease_acc_to_test(graph, test_name):
    test_name = Test.select(graph, test_name).first()
    if not test_name:
        return []
    diseases = [item.name for item in test_name.test_fit_disease]
    return diseases

def search_disease_acc_to_drug(graph, drug_name):
    drug_name = Drug.select(graph, drug_name).first()
    if not drug_name:
        return []
    diseases = [item.name for item in drug_name.drug_fit_disease]
    return diseases

def search_disease_all_attribute(graph,disease_name_input):
    '''查询疾病的所有属性'''
    disease = Disease.select(graph, disease_name_input).first()
    if not disease:
        return []
    disease_all_attribute = {'name':disease.name,
                        'EnglishName':disease.EnglishName,
                        'SynonymNames': disease.SynonymNames,
                        'ClinicFeature': disease.ClinicFeature,
                        'Cause':disease.Cause,
                        'Prevention':disease.Prevention,
                        'Prognosis':disease.Prognosis,
                        'Complication':disease.Complication,
                        'Treatment':disease.Treatment,
                        'Diagnosis':disease.Diagnosis,
                        'Test':disease.Test,
                        'ProneGroup':disease.ProneGroup,
                        'Contagion':disease.Contagion
                        }
    return  disease_all_attribute

def search_drugs_all_attribute(graph,drug_name_input):
    drug = Drug.select(graph,drug_name_input).first()
    if not drug:
        return []
    drug_all_attribute = {'name': drug.name,
                        'EnglishName': drug.EnglishName,
                        'SynonymNames': drug.SynonymNames,
                        'Specifications': drug.Specifications,
                        'Indication ': drug.Indication ,
                        'AdverseReaction': drug.AdverseReaction,
                        'Contraindication': drug.Contraindication,
                        'Use': drug.Use,
                        'Description': drug.Description,
                        'DrugInteraction': drug.DrugInteraction
                     }
    return  drug_all_attribute


def search_symptom_all_attribute(graph,symptom_name_input):
    symptom = Symptom.select(graph,symptom_name_input).first()
    if not symptom:
        return []
    symptom_all_attribute = {'name': symptom.name
                     }
    return symptom_all_attribute

def search_cause_all_attribute(graph, cause_name_input):
    cause = Cause.select(graph, cause_name_input).first()
    if not cause:
        return []
    drug_all_attribute = {'name': cause.name
                     }
    return  drug_all_attribute

def search_test_all_attribute(graph, test_name_input):
    test = Test.select(graph, test_name_input).first()
    if not test:
        return []
    test_all_attribute = {'name': test.name
                     }
    return test_all_attribute

def search_organ_all_attribute(graph, organ_name_input):
    organ = Organ.select(graph, organ_name_input).first()
    if not organ:
        return []
    organ_all_attribute = {'name': organ.name
                     }
    return organ_all_attribute

def search_office_all_attribute(graph, office_name_input):
    office = Test.select(graph, office_name_input).first()
    if not office:
        return []
    office_all_attribute = {'name': office.name
                     }
    return office_all_attribute



if __name__ == '__main__':
    logging.getLogger().setLevel(logging.ERROR)
    #url_address = "http://172.18.30.118:7474"
    url_address= 'http://202.85.214.151:7474'
    user_name = 'neo4j'
    # user_password = input("please input your password: ")
    graph_db = init_database(url_address, user_name, 'yangzhen042618')




    # # attributes files
    # disease_attribute_file = r'.\data\all_disease\final_ready_for_neo4j_total_disease_attribute.txt'
    # drug_attribute_file = r'.\data\all_drugs\final_drug_ready_neo4j.txt'
    # organ_attribute_file = r'.\data\all_organs\organ_attribute.txt'
    # office_attribute_file = r'.\data\all_office\office_attribute.txt'
    # symptom_attribute_file = r'.\data\all_symptoms\final_symptom_attribute.txt'
    # test_attribute_file = r'.\data\all_test\test_attribute.txt'
    # cause_attribute_file = r'.\data\all_causes\new_cause_attribute.txt'  # need to revise
    #
    # # relation files in single entity
    # disease_disease_relation_file = r'.\data\all_disease\final_disease_disease_relation.txt'
    # drug_drug_relation_file = r'.\data\all_drugs\final_drug_drug_relation.txt'  # need to revise
    # organ_organ_relation_file = r'.\data\all_organs\organ_organ_relation.txt'
    # office_office_relation_file = r'.\data\all_office\office_office_relation.txt'
    # symptom_symptom_relation_file = r'.\data\all_symptoms\final_symptom_symptom_relation.txt'
    # test_test_relation_file = r'.\data\all_test\test_test_relation.txt'
    # cause_cause_relation_file = r'.\data\all_causes\new_cause_cause_relation.txt'  # need to revise
    #
    # # relation files in two different entities
    # disease_drug_relation_file = r'.\data\disease_drug_relation\final_disease_drug_relation.txt'
    # disease_organ_relation_file = r'.\data\disease_organ_relation\disease_organ_relation_sure.txt'  # need to revise
    # disease_office_relation_file = r'.\data\disease_office_relation\disease_office_relation.txt'  # need to revise
    # disease_symptom_relation_file = r'.\data\disease_sympoton_relation\final_disease_symptom_relation.txt'
    # disease_cause_relation_file = r'.\data\disease_cause_relation\disease_cause_relation.txt'  # need to revise
    # disease_test_relation_file = r'.\data\disease_with_test\disease_test_relation.txt'







