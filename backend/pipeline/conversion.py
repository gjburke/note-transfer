import re
from anytree import Node, PreOrderIter

def strict_clean_str(text):
    clean_text = re.sub(r"[^a-zA-Z0-9 ]", "", text)
    return clean_text

def lax_clean_str(text):
    # Regex to find common markdown characters
    markdown_chars = r"([\\`*_{}\[\]()#+\-.!|])"
    # Add a backslash before every match
    escaped_text = re.sub(markdown_chars, r"\\\1", text)
    return escaped_text

def get_parent_section(node):
    curr = node
    while not curr.is_section and curr is not None:
        curr = curr.parent
    return curr

def markdown_from_nodes(root):
    parts = []

    prev_header_depth, curr_header_level = 0, 0
    prev_bullet_section = None
    prev_bullet_depth, curr_bullet_level = 0, 0
    ordered_bullet_numbers = []
    for node in PreOrderIter(root):
        if node.is_section:
            match node.cls_id:
                case -1: # Root
                    print("Root")
                case 0: # Header
                    if node.depth > prev_header_depth:
                        curr_header_level += 1
                    elif node.depth < prev_header_depth:
                        curr_header_level -= 1
                    prev_header_depth = node.depth
                    parts.append("\n\n" + "#"*curr_header_level + " ")
                case 1: # Section
                    parts.append("\n\n")
                case _:
                    print("Unknown Class")
        else:
            match node.cls_id:
                case 0:
                    print("None Class")
                case 1: # Unordered Bullet
                    # Handle indentation
                    parent_section = get_parent_section(node)
                    if prev_bullet_section is None or prev_bullet_section != parent_section:
                        curr_bullet_level = 0
                    else:
                        if node.depth > prev_bullet_depth:
                            curr_bullet_level += 1
                        elif node.depth < prev_bullet_depth:
                            curr_bullet_level = max(0, curr_bullet_level-1)

                    prev_bullet_section = parent_section
                    prev_bullet_depth = node.depth

                    parts.append("\n")
                    parts.append("    "*curr_bullet_level)
                    parts.append(f"- ")
                case 2: # Ordered Bullet
                    # Handle indentation
                    parent_section = get_parent_section(node)
                    if prev_bullet_section is None or prev_bullet_section != parent_section:
                        curr_bullet_level = 0
                    else:
                        if node.depth > prev_bullet_depth:
                            curr_bullet_level += 1
                        elif node.depth < prev_bullet_depth:
                            curr_bullet_level = max(0, curr_bullet_level-1)

                    # Handle Numbering
                    if prev_bullet_section is None or prev_bullet_section != parent_section:
                        ordered_bullet_numbers = [0]
                    else:
                        if node.depth > prev_bullet_depth:
                            ordered_bullet_numbers.append(0)
                        elif node.depth < prev_bullet_depth:
                            ordered_bullet_numbers.pop()
                        if len(ordered_bullet_numbers) == 0:
                            ordered_bullet_numbers = [0]

                    prev_bullet_section = parent_section
                    prev_bullet_depth = node.depth
                    bullet_number = ordered_bullet_numbers[-1] + 1
                    ordered_bullet_numbers[-1] = bullet_number

                    parts.append("\n")
                    parts.append("    "*curr_bullet_level)
                    parts.append(f"{bullet_number}. ")

                case 3: # Text
                    if node.parent.is_section and node.parent.cls_id == 0: # If parent is header
                        parts.append(strict_clean_str(node.text))
                    else:
                        parts.append(lax_clean_str(node.text))
                    parts.append(" ")
                case 4: # Figure
                    print("Doing nothign with figures for now")
                case _:
                    print("Unknown Class")

    return "".join(parts)