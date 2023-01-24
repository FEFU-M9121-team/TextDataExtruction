# This is a sample Python script.

from natasha import Doc, Segmenter, NewsMorphTagger, NewsSyntaxParser, NewsEmbedding, MorphVocab, NewsNERTagger
from date import DatesExtractor
from rules import get_symptoms, get_reasons, get_actions, get_dates, get_temperature
import pandas as pd


class MyParser:

    def __init__(self):
        self.segmenter = Segmenter()
        self.morph_vocab = MorphVocab()
        self.emb = NewsEmbedding()
        self.morph_tagger = NewsMorphTagger(self.emb)
        self.syntax_parser = NewsSyntaxParser(self.emb)
        self.ner_tagger = NewsNERTagger(self.emb)
        self.dates_extractor = DatesExtractor(self.morph_vocab)

    def load_dataset(self, name):
        df = pd.read_excel('dataset/' + name)
        selections = map(list, zip(df['Возраст'], df['Пол'], df['История настоящего заболевания']))
        return selections

    def parse_data(self, data):
        for dat in data:
            print(dat[2])
            doc = Doc(dat[2])
            doc.segment(self.segmenter)
            doc.tag_morph(self.morph_tagger)
            doc.parse_syntax(self.syntax_parser)
            doc.tag_ner(self.ner_tagger)
            for token in doc.tokens:
                token.lemmatize(self.morph_vocab)
            # doc.sents[0].morph.print()

            print("Возраст: " + str(dat[0]))
            print("Пол: " + dat[1])

            print("Reasons:", end="\n")
            res = get_reasons(doc)
            for item in res:
                print([x.value for x in item.tokens])

            print("Symptoms:", end="\n")
            res = get_symptoms(doc)
            for item in res:
                print(item)

            print("Actions:", end="\n")
            res = get_actions(doc)
            for item in res:
                print([x.value for x in item.tokens])

            print("DATES:", end="\n")
            # res = get_dates(doc)
            # for item in res:
            #     print([x.value for x in item.tokens])
            matches = self.dates_extractor(dat[2])
            facts = [i.fact.as_json for i in matches]
            for f in facts:
                print(f"{f.get('day')}.{f.get('month')}.{f.get('year')}")

            print("TEMPS:", end="\n")
            res = get_temperature(doc)
            for item in res:
                print([x.value for x in item.tokens])

            print("-------------------------------------------------------")


def main():
    myParser = MyParser()
    # data = myParser.load_dataset('dataset.xls')
    data = [["", "", "…характерна тупая, ноющая боль в области правого подреберья постоянного характера или "
                    "возникающая через 1–3 ч после приема обильной и особенно жирной и жареной пищи. Боль иррадиирует "
                    "вверх, в область правого плеча и шеи, правой лопатки. Периодически может возникать резкая боль, "
                    "напоминающая желчную колику. Нередки диспепсические явления: ощущение горечи и металлического "
                    "вкуса во рту, отрыжка воздухом, тошнота, метеоризм, нарушение дефекации (нередко чередование "
                    "запора и поноса), а также раздражительность, бессонница."]]
    myParser.parse_data(data)


if __name__ == '__main__':
    main()
