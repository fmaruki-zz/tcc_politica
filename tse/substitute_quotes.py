import re
import sys

with open(sys.argv[1]) as f:
    for line in f:
        if "PLEBISCITO" in line:
            continue
        print re.sub(r'(?<=[^;])"(?=[^;\n\r])', r'""', line),
