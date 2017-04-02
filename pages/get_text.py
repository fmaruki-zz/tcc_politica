import yaml
from pyquery import PyQuery as pq
import os
import re

def extract_text(filename, selector):
    with open(filename) as f:
        text = f.read()
        if not text:
            return ""
        try:
            html = pq(text, parser="html")
            html.remove("script,style,link,head")
            text = re.sub(r"(\s*\.\s+)+", ". ", " . ".join([el.text_content() or "" for el in html(selector)])).strip()
        except:
            import pdb;pdb.set_trace()
            pass
    return text

configs = yaml.load(open("config.yaml").read())
for config in configs:
    partido = config['partido']
    print partido
    files = os.listdir(config['sigla'])
    for filename in files:
        text = extract_text(config['sigla'] + "/" + filename, config['text'])
        if text:
            with open("text/" + config['sigla'] + "/" + filename, "w") as f:
                f.write(text.encode("utf-8"))
                f.close()
