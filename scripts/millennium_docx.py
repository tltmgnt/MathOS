"""Generate editable Word copies of canonical Millennium milestone papers.

No third-party dependencies; deterministic zipped Office Open XML.
Run from repository root: python scripts/millennium_docx.py
Use --verify to check the on-disk library against the canonical Markdown.
"""
import argparse
import base64
import re
from pathlib import Path
from xml.sax.saxutils import escape
from xml.etree import ElementTree as ET
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

ROOT=Path(__file__).resolve().parents[1]/'docs/research/papers/millennium'
NS='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
W={'w':NS}
TRACKS='RH PNP NS YM HODGE BSD POINCARE'.split()
STYLE=f'''<?xml version="1.0" encoding="UTF-8"?>
<w:styles xmlns:w="{NS}">
<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Cambria" w:hAnsi="Cambria"/><w:sz w:val="22"/><w:color w:val="20252D"/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:spacing w:after="120" w:line="276" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>
<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/></w:style>
<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:basedOn w:val="Normal"/><w:pPr><w:keepNext/><w:spacing w:after="180"/></w:pPr><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:b/><w:color w:val="17365D"/><w:sz w:val="38"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:qFormat/><w:pPr><w:keepNext/><w:keepLines/><w:spacing w:before="240" w:after="80"/><w:outlineLvl w:val="0"/></w:pPr><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:b/><w:color w:val="17365D"/><w:sz w:val="27"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Meta"><w:name w:val="Research status"/><w:basedOn w:val="Normal"/><w:pPr><w:keepNext/><w:spacing w:after="180"/></w:pPr><w:rPr><w:i/><w:color w:val="52667A"/><w:sz w:val="20"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Code"><w:name w:val="Evidence code"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:after="0" w:line="240" w:lineRule="auto"/><w:ind w:left="180"/></w:pPr><w:rPr><w:rFonts w:ascii="Courier New" w:hAnsi="Courier New"/><w:sz w:val="18"/></w:rPr></w:style>
</w:styles>'''
TYPES='''<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>'''
RELS='''<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>'''
DOCRELS='''<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>'''


def paragraphs(text):
    code=False
    for line in text.split('\n'):
        if line.startswith('\x60\x60\x60'):
            code=not code
            continue
        if code:
            yield line,'Code'
            continue
        if not line.strip():
            continue
        style='Normal'
        if line.startswith('# '): line=line[2:];style='Title'
        elif line.startswith('## '): line=line[3:];style='Heading1'
        elif line.startswith('**MathOS'): style='Meta'
        line=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',r'\1 (\2)',line)
        line=re.sub(r'\x60([^\x60]+)\x60',r'\1',line.replace('**',''))
        yield line,style
    if code: raise ValueError('unclosed code block')


def make_docx(source,target):
    body=''.join(f'<w:p><w:pPr><w:pStyle w:val="{style}"/></w:pPr><w:r><w:t xml:space="preserve">{escape(line)}</w:t></w:r></w:p>' for line,style in paragraphs(source.read_text(encoding='utf-8')))
    document=f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="{NS}"><w:body>{body}<w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="1008" w:right="1152" w:bottom="1008" w:left="1152" w:header="360" w:footer="360" w:gutter="0"/></w:sectPr></w:body></w:document>'''
    parts={'[Content_Types].xml':TYPES,'_rels/.rels':RELS,'word/document.xml':document,'word/styles.xml':STYLE,'word/_rels/document.xml.rels':DOCRELS}
    target.parent.mkdir(parents=True,exist_ok=True)
    with ZipFile(target,'w') as z:
        for name,value in parts.items():
            z.writestr(ZipInfo(name,(2026,11,24,0,0,0)),value.encode('utf-8'),compress_type=ZIP_DEFLATED)


def verify(source,target):
    with ZipFile(target) as z:
        if z.testzip() is not None: raise ValueError(f'CRC error: {target}')
        for name in ('[Content_Types].xml','_rels/.rels','word/styles.xml','word/_rels/document.xml.rels'):
            ET.fromstring(z.read(name))
        doc=ET.fromstring(z.read('word/document.xml'))
    actual=[''.join(t.text or '' for t in p.findall('.//w:t',W)) for p in doc.findall('.//w:body/w:p',W)]
    if actual!=[line for line,style in paragraphs(source.read_text(encoding='utf-8'))]:
        raise ValueError(f'DOCX text mismatch: {target}')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--verify',action='store_true')
    p.add_argument('--emit-base64',action='store_true',help='bootstrap transport for checked-in binary copies')
    args=p.parse_args()
    papers=sorted(p for p in ROOT.glob('*.md') if re.fullmatch(r'(RH|PNP|NS|YM|HODGE|BSD|POINCARE)-\d{3}',p.stem))
    if set(x.stem.split('-')[0] for x in papers)!=set(TRACKS): raise ValueError('all seven tracks required')
    for source in papers:
        target=ROOT/'docx'/source.stem.split('-')[0]/(source.stem+'.docx')
        if not args.verify: make_docx(source,target)
        verify(source,target)
        print(f'PASS {target.relative_to(ROOT)}')
        if args.emit_base64:
            data=base64.b64encode(target.read_bytes()).decode('ascii')
            for i in range(0,len(data),3000):
                print(f'DOCX64 {source.stem} {data[i:i+3000]}')
    print(f'{len(papers)} editable papers verified')


if __name__=='__main__':
    main()
