import urllib.request
import json
import os
import re

API_URL = "https://rosettacode.org/w/api.php"
CATEGORY = "Category:Zen_C"

def fetch_json(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Zen-C-AutoScraper/1.1'})
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())

def wiki_to_markdown(wiki_text, page_url):
    def repl_code(match):
        return f"\n```zc\n{match.group(1).strip()}\n```\n"
    
    md = re.sub(r'(?:<lang[^>]*>|<syntaxhighlight[^>]*>|<highlight[^>]*>)(.*?)(?:</lang>|</syntaxhighlight>|</highlight>)', 
                repl_code, wiki_text, flags=re.DOTALL | re.IGNORECASE)    
    md = re.sub(r'\[\[([^\]|]+)\|([^\]]+)\]\]', r'[\2](https://rosettacode.org/wiki/\1)', md)
    md = re.sub(r'\[\[([^\]]+)\]\]', r'[\1](https://rosettacode.org/wiki/\1)', md)
    md = re.sub(r"'''(.*?)'''", r"**\1**", md)
    md = re.sub(r"''(.*?)''", r"*\1*", md)
    md = re.sub(r'\n{3,}', '\n\n', md)
    return md.strip()

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
                combined_code = "\n\n".join(block.strip() for block in code_blocks)
                safe_title = title.replace("/", "_").replace(" ", "_")
                page_url = f"https://rosettacode.org/wiki/{title.replace(' ', '_')}"
                history_url = f"{page_url}?action=history"
                
                zc_filename = f"examples/rosetta/{safe_title}.zc"
                with open(zc_filename, "w", encoding="utf-8") as f:
                    f.write(combined_code + "\n")
                    
                md_filename = f"website_out/{safe_title}.md"
                content_md = wiki_to_markdown(zen_c_section, page_url)
                
                with open(md_filename, "w", encoding="utf-8") as f:
                    f.write("+++\n")
                    f.write(f'title = "{title}"\n')
                    f.write("+++\n\n")
                    f.write(f"# {title}\n\n")
                    f.write(content_md + "\n\n")
                    f.write("---\n")
                    f.write(f"**Attribution:** This is a community solution for the Rosetta Code task [**{title}**]({page_url}) in Zen C.\n\n")
                    f.write(f"*This article uses material from the Rosetta Code article **{title}**, which is released under the [GNU Free Documentation License 1.3](https://www.gnu.org/licenses/fdl-1.3.html). A list of the original authors can be found in the [page history]({history_url}).*\n")
                
                print(f"-> Scraped: {title} ({len(code_blocks)} blocks)")
            else:
                print(f"-> Found header, but NO code block in: {title}")
        else:
            print(f"-> Could not find Zen C header in: {title}")

if __name__ == "__main__":
    main()
