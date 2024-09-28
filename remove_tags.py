import re
import os
import sys
import itertools


splitter = [r'\\begin\{document\}', r'\\section\{.*?\}', r'\\subsection\{.*?\}', r'\\subsubsection\{.*?\}', r'\\paragraph\{.*?\}', r'\\subparagraph\{.*?\}']

def split_sections(tex):
    splitter_regex = "(" + "|".join(splitter) + ")"
    sections_regex = re.split(splitter_regex, tex)

    titles = []
    sections = []
    current_title = ""
    current_section = ""
    
    for sec in sections_regex:
        if re.fullmatch(splitter_regex, sec) is not None:
            # Save the section
            if current_section:
                titles.append(current_title)
                sections.append(current_section)

            # Start the new section
            current_title = sec
            current_section = sec
        else:
            current_section += sec

    if current_section:
        titles.append(current_title)
        sections.append(current_section)

    # Check consistency
    assert(len(titles) == len(sections))
    assert(tex == "".join(sections))

    return titles, sections



subtext = {'math':   "'X'",
           '~eqref': "~(57)",
           'eqref':  "(58)",
           '~ref':   "~(59)",
           'ref':    "(60)",
           '~cite':  "~[61]",
           'cite':   "[62]",
           'env,':   '"ENVIRONMENT,"',
           'env.':   '"ENVIRONMENT."',
           'env':    '"ENVIRONMENT"',
          }

regex = {'math':   r'\$.*?\$',
         '~eqref': r'~\\eqref\{.*?\}',
         'eqref':  r'\\eqref\{.*?\}',
         '~ref':   r'~\\ref\{.*?\}',
         'ref':    r'\\ref\{.*?\}',
         '~cite':  r'~\\cite\{.*?\}',
         'cite':   r'\\cite\{.*?\}',
         'env,':   r'\\begin\{(equation|align|alignat|gather)\}(?:(?!\\end\{\1\})[\s\S])*,(?:(?!\\end\{\1\})[^,\.])*\\end\{\1\}',
         'env.':   r'\\begin\{(equation|align|alignat|gather)\}(?:(?!\\end\{\1\})[\s\S])*\.(?:(?!\\end\{\1\})[^,\.])*\\end\{\1\}',
         'env':    r'\\begin\{(equation|align|alignat|gather)\}(?:(?!\\end\{\1\})[\s\S])*\\end\{\1\}',
        }

assert(set(subtext.keys()) == set(regex.keys()))


# Usage remove_tags.py <mode> <tex_file>

# Read command-line arguments
if len(sys.argv) != 3:
    print("Usage: remove_tags.py <mode> <tex_file>")
    sys.exit(1)
mode = sys.argv[1]
tex_file = sys.argv[2]
if not tex_file.endswith('.tex'):
    print("Error: tex_file must end with .tex")
    sys.exit(1)
record_file = tex_file[:-4] + "_record.txt"
stripped_file = tex_file[:-4] + "_stripped.tex"
restored_file = tex_file[:-4] + "_restored.tex"

if mode == "remove":
    # Read the tex file and split it into sections
    with open(tex_file, "r") as f:
        tex = f.read()
    titles, sections = split_sections(tex)

    # Open output files
    f_stripped = open(stripped_file, "w")
    f_record = open(record_file, "w")

    for title, sec in zip(titles, sections):
        # Replace the tags with the subtext
        record = {}
        for key in subtext.keys():
            record[key] = [x.group() for x in re.finditer(regex[key], sec)]
            sec = re.sub(regex[key], subtext[key], sec)

        # Output the result
        f_stripped.write(sec)

        # Output the removed tags
        f_record.write("\n" + title + "\n")
        for key, tags in record.items():
            for tag in tags:
                f_record.write(f'###{key}#### #####{tag}######\n')
    
    f_stripped.close()
    f_record.close()


elif mode == "restore":
    # Read the removed tags and split it into sections
    with open(record_file, "r") as f:
        record_text = f.read()
    titles1, record_sections = split_sections(record_text)
    
    # Read the stripped file and split it into sections
    with open(stripped_file, "r") as f:
        tex = f.read()
    titles2, tex_sections = split_sections(tex)

    # Check consistency
    if len(titles1) != len(titles2):
        print("Error: # of sections do not match")
        print(f"# of sections in record: {len(titles1)}")
        print(f"# of sections in stripped: {len(titles2)}")
        print("Record || Stripped")
        for t1, t2 in itertools.zip_longest(titles1, titles2):
            print(f"{t1} || {t2}")
        sys.exit(1)

    # Open the output file
    f_restored = open(restored_file, "w")

    for title1, title2, record_sec, tex_sec in zip(titles1, titles2, record_sections, tex_sections):
        print(f"===== {title1} =====")
        if not title1 == title2:
            print("Warning: Titles do not match")
            print("Title_recorded:", title1)
            print("Title_stripped:", title2)
            
        # Parse the removed tags
        record = {}
        for key in subtext.keys():
            record[key] = [x.group(1) for x in re.finditer(f'###{re.escape(key)}#### #####([\s\S]*?)######', record_sec)]

        # Restore the tags
        for key, rec in record.items().__reversed__():
            nfield = tex_sec.count(subtext[key])
            if nfield != len(rec): 
                print(f'Warning: # of {key}s does not match: {nfield} fields found but {len(rec)} records given')
            for r in rec[:nfield]:
                tex_sec = tex_sec.replace(subtext[key], r, 1)

        # Output the result
        f_restored.write(tex_sec)

    f_restored.close()


else:
    print("Usage: remove_tags.py <mode> <tex_file>")
    sys.exit(1)