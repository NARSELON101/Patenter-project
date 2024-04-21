from datetime import datetime

import bs4
import requests

from query_processor.data_source.source import DataSource


def get_p_if_start_with(p, s) -> bs4.Tag | None:
    p_21_22: bs4.Tag | None = None
    if p.text.strip().startswith(s):
        p_21_22 = p
    return p_21_22


class FipsFetcherDataSource(DataSource):
    url_template = ('https://www1.fips.ru/registers-doc-view/fips_servlet?DB={DB}&rn={RN}&DocNumber={'
                    'DocNumber}&TypeFile=html')
    default_db = 'RUPM'
    default_rn = 6919
    __scheme = {
        'id': 'int',
        'status': 'str',
        'application_id_21': 'str',
        'date_of_application_submission_22': 'datetime',
        'date_of_begin_24': 'datetime',
        'priority': 'list[str]',
        'published_45': 'datetime',
        'list_of_documents_cited_56': 'str',
        'authors_72': 'list[str]',
        'patent_name_54': 'str'
    }

    def get(self, patent_id: int | str) -> dict | None:
        return self.get_doc(int(patent_id))

    def get_doc(self, id_: int, db=default_db, rn=default_rn) -> dict | None:
        url = self.get_final_url(id_, db, rn)
        req = requests.get(url)
        if not req.ok:
            return None

        html = req.text
        if html == 'Документ с данным номером отсутствует':
            return None

        soup = bs4.BeautifulSoup(html, 'html.parser')
        res = {'id': id_}
        all_td = soup.find_all('td', id='StatusL')

        if all_td is None:
            return None

        for s in all_td:
            if s.text.strip() == 'Статус:':
                status = s.find_next("td", id="StatusR")
                res['status'] = status.text
                break
        table_bib = soup.find('table', id='bib')

        if table_bib is None:
            return None

        p_21_22: bs4.Tag | None = None
        p_24: bs4.Tag | None = None
        p_45: bs4.Tag | None = None
        p_56: bs4.Tag | None = None
        p_72: bs4.Tag | None = None

        for p in table_bib.find_all('p'):
            if p_21_22 is None:
                p_21_22 = get_p_if_start_with(p, '(21)(22) Заявка:')
            if p_24 is None:
                p_24 = get_p_if_start_with(p, '(24) Дата начала отсчета срока действия патента:')
            if p_45 is None:
                p_45 = get_p_if_start_with(p, '(45) Опубликовано:')
            if p_56 is None:
                p_56 = get_p_if_start_with(p, '(56) Список документов, цитированных в отчете о поиске:')
            if p_72 is None:
                p_72 = get_p_if_start_with(p, '(72) Автор(ы):')

        if p_21_22 is not None:
            application_id_21, date_of_application_submission_22 = p_21_22.find_next('b').text.strip().split(',')
            date_of_application_submission_22 = datetime.strptime(date_of_application_submission_22.strip(), '%d.%m.%Y')

            res['application_id_21'] = application_id_21
            res['date_of_application_submission_22'] = date_of_application_submission_22

        if p_24 is not None:
            date_of_begin_24 = p_24.find_next('b').text.strip()
            res['date_of_begin_24'] = datetime.strptime(date_of_begin_24, '%d.%m.%Y')

        if p_45 is not None:
            published_45 = p_45.find_next('b').text.strip()
            res['published_45'] = datetime.strptime(published_45, '%d.%m.%Y')

        if p_56 is not None:
            list_of_documents_cited_56 = p_56.find_next('b').text.strip()
            res['list_of_documents_cited_56'] = list_of_documents_cited_56

        if p_72 is not None:
            authors_72 = p_72.find_next('b').text.strip().split(',')
            res['authors_72'] = authors_72

        p = p_45
        priority: list[str] = []
        while 'prior' not in p.attrs['class'] if 'class' in p.attrs else True:
            p = p.find_previous_sibling('p')
            if p is None:
                break
            priority.append(p.text.strip())

        res['priority'] = priority[:-1]

        patent_name_54 = soup.find('p', id='B542').find_next('b').text
        res["patent_name_54"] = patent_name_54

        return res

    def get_final_url(self, id_, db, rn):
        return self.url_template.format(DocNumber=id_, DB=db, RN=rn)
