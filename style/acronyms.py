"""
Panflute filter that allows for acronyms in latex using the acro package

Usage:

- In markdown, use it as links: [SO](acro "Stack Overflow")
- Then, this filter will add \DeclareAcronym{LRU}{long=Least Recently Used} 
for the definition of LRU and finally \ac{LRU} to every time the term is used in the text.

(Development of this tool can be followed here https://groups.google.com/forum/#!topic/pandoc-discuss/Bz1cG55BKjM)
"""

from string import Template  # using .format() is hard because of {} in tex
import panflute as pf

TEMPLATE_GLS = Template(r"\ac{$acronym}")
TEMPLATE_NEWACRONYM = Template(r"\DeclareAcronym{$acronym}{long=$definition}")


def prepare(doc):
    doc.acronyms = {}


def action(e, doc):
    if isinstance(e, pf.Link) and e.url == 'acro':
        acronym = pf.stringify(e)
        definition = e.title
        # Only update dictionary if definition is not empty
        if definition:
            doc.acronyms[acronym] = definition
        
        if doc.format == 'latex':
            tex = '\ac{{}}'.format(acronym)
            tex = TEMPLATE_GLS.safe_substitute(acronym=acronym)
            return pf.RawInline(tex, format='latex')


def finalize(doc):
    if doc.format == 'latex':
        tex = [r'\usepackage[]{acro}']
        for acronym, definition in doc.acronyms.items():
            tex_acronym = TEMPLATE_NEWACRONYM.safe_substitute(acronym=acronym, definition=definition)
            tex.append(tex_acronym)

        tex = [pf.MetaInlines(pf.RawInline(line, format='latex')) for line in tex]
        tex = pf.MetaList(*tex)
        if 'header-includes' in doc.metadata:
            doc.metadata['header-includes'].content.extend(tex)
        else:
            doc.metadata['header-includes'] = tex


def main(doc=None):
    return pf.run_filter(action, prepare=prepare, finalize=finalize, doc=doc) 


if __name__ == '__main__':
    main()
