import re
import os
import sys

subtext = {'math':  "'X'",
           '~eqref': " (57)",
           'eqref': "(58)",
           '~ref':   " (59)",
           'ref':   "(60)",
           '~cite':  " [61]",
           'cite':  "[62]",
           'env,':   '"ENVIRONMENT,"',
           'env.':   '"ENVIRONMENT."',
           'env':   '"ENVIRONMENT"',
          }

regex = {'math':   r'\$.*?\$',
         '~eqref':  r'~\\eqref\{.*?\}',
         'eqref':  r'\\eqref\{.*?\}',
         '~ref':    r'~\\ref\{.*?\}',
         'ref':    r'\\ref\{.*?\}',
         '~cite':   r'~\\cite\{.*?\}',
         'cite':   r'\\cite\{.*?\}',
         'env,':    r'\\begin\{(.*?)\}(?:(?!\\begin|\\end)[\s\S])*,(?:(?!\\begin|\\end)[^,\.])*\\end\{\1\}',
         'env.':    r'\\begin\{(.*?)\}(?:(?!\\begin|\\end)[\s\S])*\.(?:(?!\\begin|\\end)[^,\.])*\\end\{\1\}',
         'env':    r'\\begin\{(.*?)\}(?:(?!\\begin|\\end)[\s\S])*\\end\{\1\}',
        }

assert(set(subtext.keys()) == set(regex.keys()))


# Usage remove_tags.py <mode> <tex_file>

# Read command-line arguments
if len(sys.argv) != 3:
    print("Usage: remove_tags.py <mode> <tex_file>")
    sys.exit(1)
mode = sys.argv[1]
tex_file = sys.argv[2]
assert(tex_file.endswith('.tex'))
record_file = tex_file[:-4] + "_record.txt"
backup_file = tex_file[:-4] + "_backup.tex"

if mode == "remove":
    # Make backup of the tex file
    os.system(f"cp {tex_file} {backup_file}")

    # Read the tex file
    with open(tex_file, "r") as f:
        tex = f.read()

    # Replace the tags with the subtext
    record = {}
    for key in subtext.keys():
        record[key] = [x.group() for x in re.finditer(regex[key], tex)]
        tex = re.sub(regex[key], subtext[key], tex)

    # Output the result
    with open(tex_file, "w") as f:
        f.write(tex)

    # Output the removed tags
    with open(record_file, "w") as f:
        for key, tags in record.items():
            for tag in tags:
                f.write(f'###{key}### ####{tag}####\n')
        
elif mode == "restore":
    # Read the removed tags
    with open(record_file, "r") as f:
        record_text = f.read()
    
    # Parse the removed tags
    record = {}
    for key in subtext.keys():
        record[key] = [x.group() for x in re.finditer(f'###{key}### ####(.*?)####', record_text)]

    # Read the tex file
    with open(tex_file, "r") as f:
        tex = f.read()

    # Restore the tags
    for key, rec in record.items():
        nfield = tex.count(subtext[key])
        if nfield != len(rec): 
            print(f'Warning: # of {key}s does not match: {nfield} fields found but {len(rec)} records given')
        for r in rec[:nfield]:
            tex = tex.replace(subtext[key], r, 1)

    # Output the result
    with open(tex_file, "w") as f:
        f.write(tex)

else:
    print("Usage: remove_tags.py <mode> <tex_file>")
    sys.exit(1)