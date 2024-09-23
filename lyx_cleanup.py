import re
import os
import sys

# Usage lyx_cleanup.py <tex_file>

# Read the tex file
if len(sys.argv) != 2:
    print("Usage: lyx_cleanup.py <tex_file>")
    sys.exit(1)

tex_file = sys.argv[1]
with open(tex_file, "r") as f:
    tex = f.read()

# Insert spaces around all the math relations
mathrels1 = ["=", ">", "<"]
mathrels2 = [r"\\neq", r"\\equiv", r"\\simeq", r"\\sim", r"\\approx", r"\\mapsto", r"\\geq", r"\\leq", 
            r"\\to", r"\\ll", r"\\gg", r"\\coloneqq", r"\\eqqcolon", r"\\propto", r"\\in", r"\\ni"]

for rel in mathrels1:
    tex = re.sub(rel, ' ' + rel + ' ', tex)
for rel in mathrels2:
    tex = re.sub(rel + r"([^\w])", ' ' + rel + r' \1', tex)
tex = re.sub(r'=  =', r'==', tex)
tex = re.sub(r'=  =', r'==', tex)

# Insert linebreaks
tex = re.sub(r'([^\n])\\label', r'\1\n\\label', tex)
tex = re.sub(r'([^\n])\\caption', r'\1\n\\caption', tex)

# Remove unnecessary linebreaks
ordinaries = [r'\w', ',', r'\.', ';', ':', '!', r'\?', r'\$', r'\(', r'\)']
for ord1 in ordinaries:
    for ord2 in ordinaries:
        tex = re.sub('(' + ord1 + r')\n(' + ord2 + ')', r'\1 \2', tex)

# Rewrite ref
tex = re.sub(r'\(\\ref\{(.+?)\}\)', r'\eqref{\1}', tex)

# Write the cleaned up tex file
with open(tex_file, "w") as f:
    f.write(tex)