import ast
import os
import collections

from nltk import pos_tag


def flat(_list):
    """ [(1,2), (3,4)] -> [1, 2, 3, 4]"""
    out_list = []
    for item in _list:
        out_list += list(item)
    return out_list


def is_verb(word):
    pos_info = pos_tag([word])
    if pos_info[0][1] in ('VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'):
        return pos_info[0][1]
    if not word:
        return False


def get_trees(_path, with_filenames=False, with_file_content=False):
    filenames = []
    trees = []
    tree_object = os.walk(path, topdown=True)
    for dirname, dirs, files in tree_object:
        for file in files:
            if len(filenames) == 100:
                break
            if file.endswith('.py'):
                filenames.append(os.path.join(dirname, file))
    print('total %s files' % len(filenames))

    for filename in filenames:
        with open(filename, 'r', encoding='utf-8') as attempt_handler:
            main_file_content = attempt_handler.read()
        try:
            tree = ast.parse(main_file_content)
        except SyntaxError as e:
            print(e)
            tree = None
        if with_filenames:
            if with_file_content:
                trees.append((filename, main_file_content, tree))
            else:
                trees.append((filename, tree))
        else:
            trees.append(tree)
    print('trees generated')
    return trees


def get_all_names(tree):
    all_names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            all_names.append(node.id)
    return all_names


def get_verbs_from_function_name(function_name):
    verbs = [word for word in function_name.split('_') if is_verb(word)]
    return verbs


def get_all_words_in_path(path):
    trees = [t for t in get_trees(path) if t]
    trees_names = [get_all_names(t) for t in trees]
    function_names = [f for f in flat(trees_names) if not (f.startswith('__') and f.endswith('__'))]

    def split_snake_case_name_to_words(name):
        split_name = [n for n in name.split('_') if n]
        return split_name

    words = [split_snake_case_name_to_words(function_name) for function_name in function_names]

    return flat(words)


def get_top_verbs_in_path(path, top_size=10):
    trees = [t for t in get_trees(path) if t]
    flat_lst = [[node.name.lower() for node in ast.walk(t) if isinstance(node, ast.FunctionDef)] for t in trees]
    fncs = [f for f in flat(flat_lst) if not (f.startswith('__') and f.endswith('__'))]
    print('functions extracted')
    verbs = flat([get_verbs_from_function_name(function_name) for function_name in fncs])
    return collections.Counter(verbs).most_common(top_size)


def get_top_functions_names_in_path(path, top_size=10):
    trees = get_trees(path)
    node_name_list = [node.name.lower() for node in ast.walk(trees) if isinstance(node, ast.FunctionDef)]
    node_name_in_trees = [node_name_list for t in trees]
    func_names = [f for f in flat(node_name_in_trees) if not (f.startswith('__') and f.endswith('__'))]
    return collections.Counter(func_names).most_common(top_size)


if __name__ == '__main__':
    wds = []
    projects = [
        'django',
        'flask',
        'pyramid',
        'reddit',
        'requests',
        'sqlalchemy',
    ]
    for project in projects:
        path = os.path.join('.', project)
        wds += get_top_verbs_in_path(path)

    top_size = 200
    print('total %s words, %s unique' % (len(wds), len(set(wds))))
    for word, occurence in collections.Counter(wds).most_common(top_size):
        print(word, occurence)