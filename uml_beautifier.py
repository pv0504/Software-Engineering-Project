import sys
import re
import argparse
from typing import List
VIS_RX = re.compile(r'^\s*(?:\{static\}\s*)?[+\-#]')
CLASS_HEADER_RX = re.compile(r'^\s*class\s+(?:"[^"]+"|\S+)(?:\s+as\s+\S+)?\s*\{', re.IGNORECASE)
ENUM_HEADER_RX = re.compile(r'^\s*enum\s+(?:"[^"]+"|\S+)(?:\s+as\s+\S+)?\s*\{', re.IGNORECASE)
def is_dotted_two_line(ln: str) -> bool:
    return ln.strip() == '..'
def is_method_line(ln: str) -> bool:
    return bool(VIS_RX.match(ln)) and '(' in ln
def is_object_line(ln: str) -> bool:
    return bool(VIS_RX.match(ln)) and '(' not in ln and ':' in ln
def is_enum_value_line(ln: str) -> bool:
    stripped = ln.strip()
    if not stripped:
        return False
    return not VIS_RX.match(ln) and '(' not in ln and ':' not in ln
def find_matching_paren(s: str, open_idx: int) -> int:
    depth = 0
    n = len(s)
    for i in range(open_idx, n):
        c = s[i]
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
            if depth == 0:
                return i
    return -1
def split_top_level_commas(s: str) -> List[str]:
    parts = []
    cur = []
    angle = paren = brace = bracket = 0
    in_single_q = in_double_q = False
    i = 0
    while i < len(s):
        ch = s[i]
        if ch == "'" and not in_double_q:
            in_single_q = not in_single_q
            cur.append(ch)
        elif ch == '"' and not in_single_q:
            in_double_q = not in_double_q
            cur.append(ch)
        elif in_single_q or in_double_q:
            cur.append(ch)
        else:
            if ch == '<':
                angle += 1
                cur.append(ch)
            elif ch == '>':
                if angle > 0:
                    angle -= 1
                cur.append(ch)
            elif ch == '(':
                paren += 1
                cur.append(ch)
            elif ch == ')':
                if paren > 0:
                    paren -= 1
                cur.append(ch)
            elif ch == '{':
                brace += 1
                cur.append(ch)
            elif ch == '}':
                if brace > 0:
                    brace -= 1
                cur.append(ch)
            elif ch == '[':
                bracket += 1
                cur.append(ch)
            elif ch == ']':
                if bracket > 0:
                    bracket -= 1
                cur.append(ch)
            elif ch == ',' and angle == 0 and paren == 0 and brace == 0 and bracket == 0:
                parts.append(''.join(cur))
                cur = []
            else:
                cur.append(ch)
        i += 1
    parts.append(''.join(cur))
    return parts
def truncate_arg_list_inside_line(ln: str, arg_limit: int) -> str:
    try:
        open_idx = ln.index('(')
    except ValueError:
        return ln
    close_idx = find_matching_paren(ln, open_idx)
    if close_idx == -1:
        return ln
    inside = ln[open_idx + 1:close_idx]
    if not inside.strip():
        return ln
    args = split_top_level_commas(inside)
    normalized_args = [a for a in args if a.strip() != '']
    if len(normalized_args) <= arg_limit:
        return ln
    kept = []
    kept_count = 0
    for a in args:
        if a.strip() == '':
            continue
        kept.append(a)
        kept_count += 1
        if kept_count >= arg_limit:
            break
    truncated_inside = ', '.join(x.strip() for x in kept) + ', ...'
    new_ln = ln[:open_idx + 1] + truncated_inside + ln[close_idx:]
    return new_ln
def process_enum_block(header_line: str, block_lines: List[str], max_enum_values: int) -> List[str]:
    out_lines: List[str] = []
    enum_count = 0
    truncated = False
    def guess_indent(lines, default=""):
        for l in lines:
            stripped = l.strip()
            if stripped and not stripped.startswith('__'):
                return l[:len(l) - len(l.lstrip())]
        return default
    for ln in block_lines:
        if is_dotted_two_line(ln):
            continue
        if is_enum_value_line(ln):
            if enum_count < max_enum_values:
                out_lines.append(ln)
                enum_count += 1
            else:
                if not truncated:
                    indent = guess_indent(block_lines)
                    out_lines.append(f"{indent}... (truncated enum values)\n")
                    truncated = True
        else:
            out_lines.append(ln)
    return [header_line] + out_lines
def process_class_block(header_line: str, block_lines: List[str], max_methods: int, max_objects: int, arg_limit: int) -> List[str]:
    sep_idx = None
    for idx, ln in enumerate(block_lines):
        if ln.strip() == '__':
            sep_idx = idx
            break
    if sep_idx is not None:
        work_region = block_lines[:sep_idx]
        rest_region = block_lines[sep_idx:]
    else:
        work_region = block_lines
        rest_region = []
    out_work: List[str] = []
    method_count = 0
    object_count = 0
    methods_truncated = False
    objects_truncated = False
    def guess_indent(lines, default=""):
        for l in lines:
            m = re.match(r'^(\s*)(?:\{static\}\s*)?[+\-#]', l)
            if m:
                return m.group(1)
        return default
    for ln in work_region:
        if is_dotted_two_line(ln):
            continue
        if is_method_line(ln):
            ln2 = truncate_arg_list_inside_line(ln, arg_limit)
            if method_count < max_methods:
                out_work.append(ln2)
                method_count += 1
            else:
                if not methods_truncated:
                    indent = guess_indent(work_region)
                    out_work.append(f"{indent}+... : (truncated methods)\n")
                    methods_truncated = True
        elif is_object_line(ln):
            if object_count < max_objects:
                out_work.append(ln)
                object_count += 1
            else:
                if not objects_truncated:
                    indent = guess_indent(work_region)
                    out_work.append(f"{indent}... : (truncated objects)\n")
                    objects_truncated = True
        else:
            out_work.append(ln)
    if rest_region:
        out_rest = []
        if not is_dotted_two_line(rest_region[0]):
            out_rest.append(rest_region[0])
        tail_region = rest_region[1:]
        for ln in tail_region:
            if is_dotted_two_line(ln):
                continue
            if is_object_line(ln):
                if object_count < max_objects:
                    out_rest.append(ln)
                    object_count += 1
                else:
                    if not objects_truncated:
                        indent = guess_indent(rest_region)
                        out_rest.append(f"{indent}... : (truncated objects)\n")
                        objects_truncated = True
            else:
                if is_method_line(ln):
                    ln2 = truncate_arg_list_inside_line(ln, arg_limit)
                    if method_count < max_methods:
                        out_rest.append(ln2)
                        method_count += 1
                    else:
                        if not methods_truncated:
                            indent = guess_indent(rest_region)
                            out_rest.append(f"{indent}+... : (truncated methods)\n")
                            methods_truncated = True
                else:
                    out_rest.append(ln)
        out = [header_line] + out_work + out_rest
    else:
        out = [header_line] + out_work
    return out
def modify_plantuml(text: str, max_methods: int, max_objects: int, max_enum_values: int, arg_limit: int) -> str:
    lines = text.splitlines(keepends=True)
    out_lines: List[str] = []
    i = 0
    n = len(lines)
    while i < n:
        ln = lines[i]
        if is_dotted_two_line(ln):
            i += 1
            continue
        if ENUM_HEADER_RX.match(ln):
            header_line = ln
            i += 1
            block_lines: List[str] = []
            while i < n:
                cur = lines[i]
                if re.match(r'^\s*\}\s*$', cur):
                    i += 1
                    break
                block_lines.append(cur)
                i += 1
            processed = process_enum_block(header_line, block_lines, max_enum_values)
            out_lines.extend(processed)
            out_lines.append("}\n")
        elif CLASS_HEADER_RX.match(ln):
            header_line = ln
            i += 1
            block_lines: List[str] = []
            while i < n:
                cur = lines[i]
                if re.match(r'^\s*\}\s*$', cur):
                    i += 1
                    break
                block_lines.append(cur)
                i += 1
            processed = process_class_block(header_line, block_lines, max_methods, max_objects, arg_limit)
            out_lines.extend(processed)
            out_lines.append("}\n")
        else:
            out_lines.append(ln)
            i += 1
    return ''.join(out_lines)
def main():
    ap = argparse.ArgumentParser(description="Truncate methods, objects, and enum values in PlantUML class/enum blocks.")
    ap.add_argument('infile', nargs='?', default='-', help="Input PUML file (default: stdin)")
    ap.add_argument('-n', '--max-methods', type=int, default=5, help="Max number of methods to keep per class (default 5)")
    ap.add_argument('-m', '--max-objects', type=int, default=5, help="Max number of objects/fields to keep per class (default 5)")
    ap.add_argument('-e', '--max-enum-values', type=int, default=5, help="Max number of enum values to keep per enum (default 5)")
    ap.add_argument('-a', '--arg-limit', type=int, default=5, help="Max number of arguments to show per method (default 5)")
    args = ap.parse_args()
    if args.infile == '-':
        text = sys.stdin.read()
    else:
        with open(args.infile, 'r', encoding='utf-8') as f:
            text = f.read()
    result = modify_plantuml(text, args.max_methods, args.max_objects, args.max_enum_values, args.arg_limit)
    sys.stdout.write(result)
if __name__ == '__main__':
    main()
