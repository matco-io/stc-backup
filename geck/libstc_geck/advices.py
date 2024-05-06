from collections import OrderedDict
from typing import Optional

TEMPORAL_RANKING_FORMULA = "original_score * custom_score * fastsigm(abs(now - issued_at) / (86400 * 3) + 5, -1)"
PR_TEMPORAL_RANKING_FORMULA = f"{TEMPORAL_RANKING_FORMULA} * fastsigm(iqpr(quantized_page_rank), 0.15)"


default_field_aliases = {
    'ark_id': 'id.ark_ids',
    'ark_ids': 'id.ark_ids',
    'author': 'authors.family',
    'authors': 'authors.family',
    'cid': 'links.cid',
    'doi': 'id.dois',
    'ev': 'metadata.event.name',
    'extension': 'links.extension',
    'format': 'links.extension',
    'isbn': 'metadata.isbns',
    'isbns': 'metadata.isbns',
    'issn': 'metadata.issns',
    'issns': 'metadata.issns',
    'lang': 'languages',
    'magzdb_id': 'magzdb_id',
    'manualslib_id': 'id.manualslib_id',
    'nexus_id': 'id.nexus_id',
    'oclc_id': 'id.oclc_ids',
    'pmid': 'id.pubmed_id',
    'pub': 'metadata.publisher',
    'pubmed_id': 'id.pubmed_id',
    'rd': 'references.doi',
    'ser': 'metadata.series',
    'wiki': 'id.wiki',
}


default_term_field_mapper_configs = {
    'doi': {'fields': ['id.dois']},
    'doi_isbn': {'fields': ['metadata.isbns']},
    'isbn': {'fields': ['metadata.isbns']},
}


default_field_boosts = {
    'authors': 1.7,
    'content': 0.65,
    'extra': 1.7,
    'title': 1.85,
}


def format_document(document: dict):
    parts = []
    if title := document.get('title'):
        parts.append(f'Title: {title}')
    if authors := document.get('authors'):
        parts.append(f'Authors: {authors}')
    if id_ := document.get('id'):
        parts.append(f'ID: {id_}')
    if links := document.get('links'):
        parts.append(f'Links: {links}')
    if abstract := document.get('abstract'):
        parts.append(f'Abstract: {abstract[:200]}')
    return '\n'.join(parts)


def plain_author(author):
    text = None
    if "family" in author and "given" in author:
        text = f"{author['given']} {author['family']}"
    elif "family" in author or "given" in author:
        text = author.get("family") or author.get("given")
    elif "name" in author:
        text = author["name"]
    return text


class BaseDocumentHolder:
    def __init__(self, document):
        self.document = document

    def __getattr__(self, name):
        if name in self.document:
            return self.document[name]
        if name == 'content':
            return
        elif 'metadata' in self.document and name in self.document['metadata']:
            return self.document['metadata'][name]
        elif 'id' in self.document and name in self.document['id']:
            return self.document['id'][name]

    def has_cover(self):
        return bool(self.isbns and len(self.isbns) > 0)

    def get_links(self):
        if self.has_field('links') and self.links:
            return LinksWrapper(self.links)
        return LinksWrapper([])

    @property
    def ordered_links(self):
        links = self.get_links()
        pdf_link = None
        epub_link = None
        other_links = []
        for link in links.links.values():
            if link['extension'] == 'pdf' and not pdf_link:
                pdf_link = link
            elif link['extension'] == 'pdf' and not epub_link:
                epub_link = link
            else:
                other_links.append(link)
        if epub_link:
            other_links = [epub_link] + other_links
        if pdf_link:
            other_links = [pdf_link] + other_links
        return other_links

    @property
    def doi(self):
        if self.has_field('dois') and self.dois:
            return self.dois[0]

    def has_field(self, name):
        return (
            name in self.document
            or name in self.document.get('metadata', {})
            or name in self.document.get('id', {})
        )

    def get_external_id(self):
        if self.doi:
            return f'id.dois:{self.doi}'
        elif self.internal_iso:
            return f'id.internal_iso:{self.internal_iso}'
        elif self.internal_bs:
            return f'id.internal_bs:{self.internal_bs}'
        elif self.pubmed_id:
            return f'id.pubmed_id:{self.pubmed_id}'
        elif self.ark_ids:
            return f'id.ark_ids:{self.ark_ids[-1]}'
        elif self.libgen_ids:
            return f'id.libgen_ids:{self.libgen_ids[-1]}'
        elif self.zlibrary_ids:
            return f'id.zlibrary_ids:{self.zlibrary_ids[-1]}'
        elif self.wiki:
            return f'id.wiki:{self.wiki}'
        elif self.magzdb_id:
            return f'id.magzdb_id:{self.magzdb_id}'
        elif self.manualslib_id:
            return f'id.manualslib_id:{self.manualslib_id}'
        elif self.oclc_ids:
            return f'id.oclc_ids:{self.oclc_ids[-1]}'
        else:
            return None

    def get_id(self):
        if self.nexus_id:
            return f'id.nexus_id:{self.nexus_id}'
        else:
            return self.get_external_id()


class LinksWrapper:
    def __init__(self, links):
        self.links = OrderedDict()
        for link in links:
            self.add(link)

    def reset(self):
        self.links = OrderedDict()

    def to_list(self):
        return list(self.links.values())

    def add(self, link):
        old_link = self.links.pop(link['cid'], None)
        self.links[link['cid']] = link
        return old_link

    def prepend(self, link):
        old_link = self.add(link)
        self.links.move_to_end(link['cid'], False)
        return old_link

    def delete_links_with_extension(self, extension):
        for cid in list(self.links.keys()):
            if self.links[cid]['extension'] == extension:
                del self.links[cid]

    def override_link_with_extension(self, new_link):
        self.delete_links_with_extension(new_link['extension'])
        return self.prepend(new_link)

    def remove_cid(self, cid):
        return self.links.pop(cid, None)

    def get_link_with_extension(self, extension: Optional[str] = None, from_end: bool = False):
        return self.get_first_link(extension=extension, from_end=from_end)

    def get_first_link(self, extension: Optional[str] = None, from_end: bool = False):
        links = list(self.links.values())
        if from_end:
            links = reversed(links)
        for link in links:
            if extension is None or link['extension'] == extension:
                return link
