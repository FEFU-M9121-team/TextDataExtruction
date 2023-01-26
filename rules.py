import re

from yargy import Parser, rule, and_
from yargy.predicates import gram, dictionary, gte, lte, in_, eq
from yargy import interpretation as interp

from date import DATE


def load_lines(path):
    with open(path, encoding='UTF-8') as file:
        for line in file:
            yield line.rstrip('\n')


INT = type('INT')
NOUN = gram('NOUN')
ADJF = gram('ADJF')
PRTF = gram('PRTF')
GENT = gram('gent')
DOT = eq('.')

pretexts = {'в', 'на', 'под', 'из'}
Symptoms = set(load_lines('dictionaries/illnesses.txt'))
Reasons = set(load_lines('dictionaries/reasons.txt'))
Qures = set(load_lines('dictionaries/qures.txt'))


def normalize_float(value):
    value = re.sub('[\s,.]+', '.', value)
    return float(value)


FLOAT = rule(
    INT,
    in_('.,'),
    INT
).interpretation(
    interp.custom(normalize_float))

# symptoms extraction rules
Symptom1 = rule(gram('ADJF').optional(),
                dictionary(Symptoms))

Symptom2 = rule(gram('ADJF').optional().,
                dictionary({'и', ','}).optional(),
                gram('ADJF'),
                dictionary(Symptoms))

# Symptom2 = rule(dictionary(Symptoms),
#                 dictionary(pretexts),
#                 gram('ADJF').optional(),
#                 gram('NOUN'))

SubSymptom = rule(gram('ADJF').optional(),
                  gram('NOUN'))

Symptom3 = rule(dictionary(Symptoms),
                dictionary(pretexts),
                SubSymptom.optional(),
                SubSymptom
                )

# reasons extraction rules
Reasons1 = rule(dictionary(Reasons),
                dictionary(pretexts).optional(),
                gram('ADJF').optional(),
                gram('NOUN'))

# action extraction rules
Action1 = rule(dictionary(Qures))

Action2 = rule(dictionary({'не'}),
               gram('VERB'))
Action3 = rule(dictionary({"лечиться", "лечился"}),
               gram('ADVB'))

# dates extraction rules

Date1 = rule(dictionary({'c', 'по'}),
             DATE)

TEMPERATURE1 = rule(FLOAT,
                    dictionary({"град", "с"}).optional()
                    )
TEMPERATURE2 = rule(INT,
                    dictionary({"град", "с"}).optional())


def get_symptoms(doc):
    symptom_extractor = [Symptom1, Symptom2, Symptom3]
    result = []
    text = " ".join(_.text for _ in doc.tokens)
    text = text.lower()
    for extr in symptom_extractor:
        parser = Parser(extr)
        result += parser.findall(text)
    res = []
    for item in result:
        it = [x.value for x in item.tokens]
        if len(res) == 0:
            res.append(it)
        else:
            index = -1
            for i in range(0, len(res)):
                if set(res[i]).issubset(it):
                    index = i
            if index != -1:
                res.remove(res[index])
                res.append(it)
            else:
                res.append(it)
    return res


def get_reasons(doc):
    reasons_extractor = [Reasons1]
    result = []
    text = " ".join(_.text for _ in doc.tokens)
    text = text.lower()
    for extr in reasons_extractor:
        parser = Parser(extr)
        result += parser.findall(text)
    return result


def get_actions(doc):
    actions_extractor = [Action1, Action3]
    result = []
    text = " ".join(_.text for _ in doc.tokens)
    text = text.lower()
    text = text.replace('-', '')
    for extr in actions_extractor:
        parser = Parser(extr)
        result += parser.findall(text)
    return result


def get_dates(doc):
    date_extractor = [Date1]
    result = []
    text = " ".join(_.text for _ in doc.tokens)
    text = text.lower()
    text = text.replace('-', '')
    for extr in date_extractor:
        parser = Parser(extr)
        result += parser.findall(text)
    return result


def get_temperature(doc):
    temp_extractor = [TEMPERATURE1,TEMPERATURE2]
    result = []
    text = " ".join(_.text for _ in doc.tokens)
    text = text.lower()
    for extr in temp_extractor:
        parser = Parser(extr)
        result += parser.findall(text)
    return result

# def get_abbreviations(text):
