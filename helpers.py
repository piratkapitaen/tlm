import re

def user_markdown(message):
    div = '<div class="chat-row row-reverse">'
    div += '<img class="chat-icon" src="./app/static/user_icon1.png" width=40 height=40>'
    div += '<div class="chat-bubble human-bubble">'+message+' </div>  </div>'
    return div

def assistant_markdown(message):
    div = '<div class="chat-row">'
#    div += '<img class="chat-icon" src="./app/static/ai_icon1.png" width=40 height=40>'
    div += '<img class="chat-icon" src="./static/bot3.png" width=40 height=40>'
    div += '<div class="chat-bubble ai-bubble">'+message+' </div>  </div>'
    return div

def code_markdown(message):
    div = '<div class="chat-row">'
#    div += '<img class="chat-icon" src="./app/static/ai_icon1.png" width=40 height=40>'
    div += '<img class="chat-icon" src="./app/static/bot2.png" width=40 height=40>'
    div += '<div class="chat-bubble ai-bubble">'+message+' </div>  </div>'
    return div

def fix_indentation(code_block):
    lines = code_block.strip().split('\n')
    fixed_lines = []
    for line in lines:
        stripped_line = line.lstrip()
        if stripped_line.startswith('public ') or stripped_line.startswith('private '):
            fixed_lines.append(line)
        elif line.strip() and not line.startswith(' ' * 4):
            fixed_lines.append(' ' * 4 + line)
        else:
            fixed_lines.append(line)
    return '\n'.join(fixed_lines)

def correct_code(input_text):
    pattern = r'(\\begin\{code\}.*?\\end\{code\})'
    def replace_code_blocks(match):
        return fix_indentation(match.group(1))
    
    processed_text = re.sub(pattern, replace_code_blocks, input_text, flags=re.DOTALL)
    return processed_text

def fix_indentation_old(match):
    code_lines = match.group(1).split('\n')
    if code_lines:
        # Calculate the minimum indentation
        min_indent = min(len(line) - len(line.lstrip()) for line in code_lines if line.strip())
        fixed_lines = [line[min_indent:] if line.strip() else line for line in code_lines]
        return '\n'.join(fixed_lines)
    return match.group(1)

# # Find and replace code blocks
# pattern = r'begin\{code\}(.*?)end\{code\}'
# fixed_text = re.sub(pattern, fix_indentation, input_text, flags=re.DOTALL)

def filter_QA(text):
#    pattern = re.compile("name .* is valid", re.flags)
#    pattern.match(text)
#    r1 = re.search(r"^\w+", xx)
    r1 = re.findall(r"Question:.+\n+Answer:.+\n+", text)
    return text

template = """
You are a friendly chatbot assistant that responds in a conversational
manner to users questions. Keep the answers short, unless specifically
asked by the user to elaborate on something.
Question: {question}

Answer:"""


# create the prompt template
context_template = """
Please use the following context to answer questions.
Context: {context}
---
Question: {question}
Answer: Let's think step by step."""

