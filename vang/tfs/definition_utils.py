from json import loads


def get_definition_name(project, repo, branch):
    return f'{project}_{repo}_{branch}'


def get_definition(template, replacements={}, additions={}):
    with open(template, 'rt', encoding='utf-8') as template_file:
        request = template_file.read()
        for key, value in replacements.items():
            request = request.replace(f'##{key}##', value)
        return {**loads(request), **additions}
