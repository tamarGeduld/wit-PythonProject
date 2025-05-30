import os, ast
from collections import Counter, defaultdict
import matplotlib.pyplot as plt

def analyze_project(root_path):
    report = {
        'function_lengths': [],
        'issues': [],       # כל אזהרה: file, line, type, detail
        'issues_per_file': Counter(),
        'issues_per_type': Counter(),
    }

    for dirpath, _, filenames in os.walk(root_path):
        if '.wit' in dirpath: continue
        for fname in filenames:
            if not fname.endswith('.py'): continue
            full = os.path.join(dirpath, fname)
            with open(full, 'r', encoding='utf-8') as f:
                src = f.read().splitlines()
            # 1. בדיקות על קובץ
            if len(src) > 200:
                report['issues'].append({
                    'file': full, 'line': 1,
                    'type': 'FileLength',
                    'detail': f'File too long: {len(src)} lines'
                })
                report['issues_per_file'][full] += 1
                report['issues_per_type']['FileLength'] += 1

            # 2. AST עבור פונקציות ומשתנים
            tree = ast.parse('\n'.join(src))
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    length = node.end_lineno - node.lineno + 1
                    report['function_lengths'].append(length)
                    if length > 20:
                        report['issues'].append({
                            'file': full, 'line': node.lineno,
                            'type': 'FunctionLength',
                            'detail': f'Function "{node.name}" is {length} lines'
                        })
                        report['issues_per_file'][full] += 1
                        report['issues_per_type']['FunctionLength'] += 1
                    if ast.get_docstring(node) is None:
                        report['issues'].append({
                            'file': full, 'line': node.lineno,
                            'type': 'MissingDocstring',
                            'detail': f'Function "{node.name}" missing docstring'
                        })
                        report['issues_per_file'][full] += 1
                        report['issues_per_type']['MissingDocstring'] += 1

            # 3. בדיקת משתנים לא בשימוש
            assigned = set()
            used = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            assigned.add((full, target.id, node.lineno))
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                    used.add((full, node.id))
            for file, var, lineno in assigned:
                if (file, var) not in used:
                    report['issues'].append({
                        'file': file, 'line': lineno,
                        'type': 'UnusedVariable',
                        'detail': f'Variable "{var}" assigned but never used'
                    })
                    report['issues_per_file'][file] += 1
                    report['issues_per_type']['UnusedVariable'] += 1

    return report

def generate_graphs(report, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    paths = {}

    # 1. היסטוגרמת אורכי פונקציות
    plt.figure()
    plt.hist(report['function_lengths'], bins=10)
    p1 = os.path.join(output_dir, 'func_length_hist.png')
    plt.savefig(p1); plt.close()
    paths['Function Lengths Histogram'] = p1

    # 2. פאי של סוגי בעיות
    plt.figure()
    labels = list(report['issues_per_type'].keys())
    sizes  = list(report['issues_per_type'].values())
    plt.pie(sizes, labels=labels, autopct='%1.1f%%')
    p2 = os.path.join(output_dir, 'issues_pie.png')
    plt.savefig(p2); plt.close()
    paths['Issues Pie Chart'] = p2

    # 3. ברצ’ארט בעיות לפי קובץ
    plt.figure()
    files = list(report['issues_per_file'].keys())
    counts= list(report['issues_per_file'].values())
    plt.bar(files, counts)
    plt.xticks(rotation=45, ha='right')
    p3 = os.path.join(output_dir, 'issues_bar.png')
    plt.tight_layout()
    plt.savefig(p3); plt.close()
    paths['Issues per File Bar Chart'] = p3

    return paths
