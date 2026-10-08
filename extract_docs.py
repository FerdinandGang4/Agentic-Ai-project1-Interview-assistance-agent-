from zipfile import ZipFile
from xml.etree import ElementTree as ET
from pathlib import Path

base = Path(r'c:\Users\dinga\Desktop\Agentic AI cause Prep\Agentic-Ai-project1-Interview-assistance-agent-\Documentation')

for p in sorted(base.glob('*.docx')):
    print(f'\n===== {p.name} =====')
    try:
        with ZipFile(p) as z:
            xml = z.read('word/document.xml')
        root = ET.fromstring(xml)
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        texts = []
        for t in root.findall('.//w:t', ns):
            texts.append(t.text or '')
        txt = ' '.join(texts)
        print(txt[:4000])
    except Exception as e:
        print('ERROR:', e)
