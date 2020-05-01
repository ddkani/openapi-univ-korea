import logging

import lxml.html
from lxml.html import HtmlElement

logging.getLogger(__name__)


class HtmlParser:
    def init_tree(self, raw_html: str) -> HtmlElement:
        return lxml.html.document_fromstring(raw_html)


class SugangParser(HtmlParser):

    def __init__(self):
        super().__init__()

    def parse_colleage_list(self, raw_html:str):
        assert raw_html != ""
        tree = self.init_tree(raw_html) # type: HtmlElement

        result = list()

        for _opt in tree.xpath("//select[@name = 'col' and @id='col'//option]"): # type: HtmlElement
            name = _opt.text_content()
            colcd = _opt.attrib['value']
            result.append((name, colcd))

        return result


    def parse_department_list(self, raw_html: str) -> list:
        assert raw_html != ""
        tree = self.init_tree(raw_html)

        result = list()
