import urllib.request
import json
import os
import re

API_URL = "https://rosettacode.org/w/api.php"
CATEGORY = "Category:Zen_C"

# Zen C keywords that are not function calls when followed by '('
_KEYWORDS = {
    'fn', 'if', 'else', 'for', 'while', 'return', 'let', 'struct', 'impl',
    'match', 'assert', 'import', 'include', 'sizeof', 'typeof', 'and', 'or',
    'not', 'true', 'false', 'switch', 'case', 'break', 'continue', 'loop',
    'defer', 'panic', 'main', 'Self', 'as',
}

def fetch_json(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Zen-C-AutoScraper/1.1'})
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())

# --- multi-block handling ------------------------------------------------
#
# A Rosetta task can carry several Zen C snippets. When they are separate
# programs (each with its own `fn main`), joining them into a single file
# produces something that cannot compile. Instead we emit one file per program
# and, when a snippet reuses a function defined in an earlier snippet (e.g. the
# "Repeat" task's second solution calls `times` from the first), we prepend the
# required definitions so every emitted file is self-contained.

def count_mains(code):
    return len(re.findall(r'\bfn\s+main\s*\(', code))

def defined_fns(code):
    return set(re.findall(r'\bfn\s+([A-Za-z_]\w*)\s*\(', code))

def called_fns(code):
    defined = defined_fns(code)
    calls = set(re.findall(r'\b([A-Za-z_]\w*)\s*\(', code))
    return {c for c in calls if c not in defined and c not in _KEYWORDS}

def extract_defs(code):
    """Return {name: definition_text} for every top-level fn/struct definition."""
    defs = {}
    for m in re.finditer(r'\b(?:fn|struct)\s+([A-Za-z_]\w*)\s*', code):
        name = m.group(1)
        brace = code.find('{', m.end())
        if brace == -1:
            continue
        depth = 0
        end = -1
        for i in range(brace, len(code)):
            if code[i] == '{':
                depth += 1
            elif code[i] == '}':
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        if end != -1:
            defs.setdefault(name, code[m.start():end])
    return defs

def make_self_contained(blocks):
    """Turn a list of separate-program snippets into self-contained files.

    Each snippet with a `main` becomes its own file. Any function it calls but
    does not define is pulled in from the definitions of earlier snippets.
    """
    all_defs = [extract_defs(b) for b in blocks]
    files = []
    for i, block in enumerate(blocks):
        if count_mains(block) == 0:
            continue  # pure definition snippet; only used as a dependency source
        needed = called_fns(block) - defined_fns(block)
        preamble = []
        for j in range(i):
            for name in sorted(all_defs[j].keys()):
                if name in needed:
                    preamble.append(all_defs[j][name])
                    needed.discard(name)
        files.append("\n\n".join(preamble + [block]))
    return files

_MODULE_LABEL = re.compile(r'^\s*/\*\s*([\w./\-]+\.zc)\s*\*/\s*$')

def split_modules(blocks):
    """Separate labeled module snippets (a block starting with `/* name.zc */`
    and no `main`) from the rest, so a program that imports them can be emitted
    as its own file next to the module file."""
    modules = []
    programs = []
    for b in blocks:
        first = b.splitlines()[0] if b.splitlines() else ''
        m = _MODULE_LABEL.match(first)
        if m and count_mains(b) == 0:
            modules.append((m.group(1), b))
        else:
            programs.append(b)
    return modules, programs

def dedup_program(blocks):
    """Merge snippets that together form one program.

    Walks from the last snippet backwards and keeps a snippet only when it
    either has a `main` or defines functions not yet seen. This drops earlier
    illustrative snippets that are fully superseded by a later complete program
    (e.g. a task page showing a fragment and then the whole program), as well
    as stray non-code blocks.
    """
    kept = []
    seen = set()
    for b in reversed(blocks):
        defs = defined_fns(b)
        new_defs = defs - seen
        if count_mains(b) > 0 or new_defs:
            kept.insert(0, b)
        seen |= defs
    return "\n\n".join(kept)

def wiki_to_markdown(wiki_text, page_url):
    def repl_code(match):
        return f"\n```zc\n{match.group(1).strip()}\n```\n"
    
    md = re.sub(r'(?:<lang[^>]*>|<syntaxhighlight[^>]*>|<highlight[^>]*>)(.*?)(?:</lang>|</syntaxhighlight>|</highlight>)', 
                repl_code, wiki_text, flags=re.DOTALL | re.IGNORECASE)    
    
    md = re.sub(r'\{\{out\}\}', r'\n**Output:**\n', md, flags=re.IGNORECASE)
    
    def repl_pre(match):
        return f"\n```\n{match.group(1).strip()}\n```\n"
    md = re.sub(r'<pre[^>]*>(.*?)</pre>', repl_pre, md, flags=re.DOTALL | re.IGNORECASE)

    def repl_header(match):
        level = len(match.group(1))
        content = match.group(2).strip()
        return f"\n{'#' * level} {content}\n"
    md = re.sub(r'^(=+)\s*(.*?)\s*\1\s*$', repl_header, md, flags=re.MULTILINE)

    md = re.sub(r'\[\[([^\]|]+)\|([^\]]+)\]\]', r'[\2](https://rosettacode.org/wiki/\1)', md)
    md = re.sub(r'\[\[([^\]]+)\]\]', r'[\1](https://rosettacode.org/wiki/\1)', md)
    md = re.sub(r"'''(.*?)'''", r"**\1**", md)
    md = re.sub(r"''(.*?)''", r"*\1*", md)
    md = re.sub(r'\n{3,}', '\n\n', md)
    return md.strip()

def write_zc(filename, content):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content + "\n")

def write_md(filename, title, content_md, page_url, history_url):
    with open(filename, "w", encoding="utf-8") as f:
        f.write("+++\n")
        f.write(f'title = "{title}"\n')
        f.write("+++\n\n")
        f.write(f"# {title}\n\n")
        f.write(content_md + "\n\n")
        f.write("---\n")
        f.write(f"**Attribution:** This is a community solution for the Rosetta Code task [**{title}**]({page_url}) in Zen C.\n\n")
        f.write(f"*This article uses material from the Rosetta Code article **{title}**, which is released under the [GNU Free Documentation License 1.3](https://www.gnu.org/licenses/fdl-1.3.html). A list of the original authors can be found in the [page history]({history_url}).*\n")

def main():
    print("-> Fetching tasks from Rosetta Code...")
    
    url = f"{API_URL}?action=query&list=categorymembers&cmtitle={CATEGORY}&cmlimit=500&format=json"
    data = fetch_json(url)
    pages = data['query']['categorymembers']
    
    os.makedirs("examples/rosetta", exist_ok=True)
    os.makedirs("website_out", exist_ok=True)

    for page in pages:
        title = page['title']
        pageid = page['pageid']
        
        content_url = f"{API_URL}?action=query&prop=revisions&rvprop=content&rvslots=main&pageids={pageid}&format=json"
        content_data = fetch_json(content_url)
        text = content_data['query']['pages'][str(pageid)]['revisions'][0]['slots']['main']['*']

        parts = re.split(r'==\{\{header\|Zen[ _-]?C\}\}==', text, flags=re.IGNORECASE)
        
        if len(parts) > 1:
            zen_c_section = parts[1].split('=={{header|')[0].strip()
            
            code_blocks = re.findall(r'(?:<lang[^>]*>|<syntaxhighlight[^>]*>|<highlight[^>]*>)(.*?)(?:</lang>|</syntaxhighlight>|</highlight>)', 
                                    zen_c_section, re.DOTALL | re.IGNORECASE)
            
            if code_blocks:
                blocks = [block.strip() for block in code_blocks]
                safe_title = title.replace("/", "_").replace(" ", "_")
                page_url = f"https://rosettacode.org/wiki/{title.replace(' ', '_')}"
                history_url = f"{page_url}?action=history"

                # Labeled module snippets (e.g. `/* rat.zc */`) become their own
                # file so programs that import them compile standalone.
                modules, prog_blocks = split_modules(blocks)
                for name, content in modules:
                    module_name = os.path.basename(name)
                    write_zc(f"examples/rosetta/{module_name}", content)
                    print(f"  -> module: {module_name}")

                if prog_blocks:
                    combined = "\n\n".join(prog_blocks)
                    if count_mains(combined) > 1:
                        # Several independent programs on one page.
                        files = make_self_contained(prog_blocks)
                        for idx, content in enumerate(files):
                            suffix = "" if idx == 0 else f"_{idx + 1}"
                            write_zc(f"examples/rosetta/{safe_title}{suffix}.zc", content)
                        print(f"-> Scraped: {title} ({len(files)} programs across {len(blocks)} blocks)")
                    else:
                        # A single program, possibly split across helper + main
                        # blocks; drop fragments superseded by a later block.
                        combined = dedup_program(prog_blocks)
                        if combined.strip():
                            write_zc(f"examples/rosetta/{safe_title}.zc", combined)
                            print(f"-> Scraped: {title} ({len(blocks)} blocks)")

                content_md = wiki_to_markdown(zen_c_section, page_url)
                write_md(f"website_out/{safe_title}.md", title, content_md, page_url, history_url)
            else:
                print(f"-> Found header, but NO code block in: {title}")
        else:
            print(f"-> Could not find Zen C header in: {title}")

if __name__ == "__main__":
    main()
