"""Reuse regular sections to render a deduplicated glossary and review questions."""


def output_sections(note: dict) -> list[dict]:
    sections = list(note['sections'])
    if note.get('glossary_title'):
        terms = {}
        for section in sections:
            for block in section['blocks']:
                if block['type'] == 'terms':
                    for item in block['items']:
                        terms.setdefault(item['term'].casefold(), item)
        if terms:
            sections.append({'h1': note['glossary_title'], 'blocks': [
                {'type': 'terms', 'items': list(terms.values())}
            ]})
    if note.get('self_check'):
        check = note['self_check']
        sections.append({'h1': check['title'], 'blocks': [
            {'type': 'learning_note',
             'question': item['question'] + ' (P' + ', P'.join(map(str, item['pages'])) + ')',
             'answer': item['answer']} for item in check['items']
        ]})
    return sections
