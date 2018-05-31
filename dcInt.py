import ast
import os
import collections
from nltk import pos_tag

"""Функция выпрямляет список с кортежами в обычный список, работает только для вложенности 1"""
def flat(data_for_flatten):
    """ [(1,2), (3,4)] -> [1, 2, 3, 4]"""
    return sum([list(item) for item in data_for_flatten], [])

"""Функция спрашивает у nltk глагол перед нами или нет"""
def is_verb(word):
    if not word:
        return False
    pos_info = pos_tag([word])
    return pos_info[0][1] == 'VB'

def get_trees(_path, with_filenames=False, with_file_content=False):
    filenames = []
    trees = []
    path = Path
    #Шарится по файловой системе
    for dirname, dirs, files in os.walk(path, topdown=True):
        #Цикл по всем найденным файлам
        for file in files:
            # Если файл оканчивается на .py то оно его заносим в список
            if file.endswith('.py'):
                filenames.append(os.path.join(dirname, file))
            #Если у нас питоновских файлов больше чем 100 то мы выходим мз цикла
            if len(filenames) == 100:
                break
    print('total %s files' % len(filenames))
    # Для каждого питоновского файла в массиве
    for filename in filenames:
        # Мы его открываем и читаем
        with open(filename, 'r', encoding='utf-8') as attempt_handler:
            main_file_content = attempt_handler.read()
        try:
            # Строим абстрактоне синтаксическое дерево
            tree = ast.parse(main_file_content)
        except SyntaxError as e:
            print(e)
            tree = None
        #Если какие-то флаги включены, то мы добавляем в деревья имя файла и текст его
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
    return [node.id for node in ast.walk(tree) if isinstance(node, ast.Name)]

"""Функция возвращает список слов в названии функции которые являются глаголами"""
def get_verbs_from_function_name(function_name):
    return [word for word in function_name.split('_') if is_verb(word)]

def get_all_words_in_path(path):
    # Получаем все не None деревья
    trees = [t for t in get_trees(path) if t]
    # Получам имена всех функций кроме магических
    function_names = [f for f in flat([get_all_names(t) for t in trees]) if
                      not (f.startswith('__') and f.endswith('__'))]

    # Разбиваем функцию на список слов
    def split_snake_case_name_to_words(name):
        return [n for n in name.split('_') if n]
    # Возвращаем список имен вообще всех
    return flat([split_snake_case_name_to_words(function_name) for function_name in function_names])

def get_top_verbs_in_path(path, top_size=10):
    global Path
    #Обновляет путь
    Path = path
    #Строит деревья
    trees = [t for t in get_trees(None) if t]
    #Оч сложный кусок добра
    fncs = [f for f in
            flat([[node.name.lower() for node in ast.walk(t) if isinstance(node, ast.FunctionDef)] for t in trees]) if
            not (f.startswith('__') and f.endswith('__'))]
    print('functions extracted')
    #Заносит в плоский список все имена функций
    verbs = flat([get_verbs_from_function_name(function_name) for function_name in fncs])
    #Возвращает 10 самых распростраенных глаголов
    return collections.Counter(verbs).most_common(top_size)


def get_top_functions_names_in_path(path, top_size=10):
    t = get_trees(path)
    nms = [f for f in
           flat([[node.name.lower() for node in ast.walk(t) if isinstance(node, ast.FunctionDef)] for t in t]) if
           not (f.startswith('__') and f.endswith('__'))]
    return collections.Counter(nms).most_common(top_size)




if __name__ == "__main__":
    #Начальный сетап
    Path = ''
    wds = []
    projects = [
        'django',
        'flask',
        'pyramid',
        'reddit',
        'requests',
        'sqlalchemy',
    ]
    #Для каждогоиз списка проектов
    for project in projects:
        #Прибавляет папки с проектами в путь
        path = os.path.join('.', project)
        #Для каждого нового пути
        wds += get_top_verbs_in_path(path)
    top_size = 200
    # тут у нас в wds типа 10n самых популярных слов и потом мы выводим типа уникальные слова с помощью функции set
    print('total %s words, %s unique' % (len(wds), len(set(wds))))
    # Цикл, для каждого из 200 самых популярных мы выводим слово -> число раз
    for word, occurence in collections.Counter(wds).most_common(top_size):
        print(word, occurence)
    print(flat([(1,2), (3,4)]))