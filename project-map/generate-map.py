#!/usr/bin/env python3
"""
Генератор карты проекта 1С (двухуровневый).

Создаёт:
  project-map/PROJECT_MAP.md          — компактный индекс (~3K токенов)
  project-map/subsystems/<Name>.md    — детали по каждой подсистеме

Запуск:  python3 project-map/generate-map.py [путь_к_выгрузке]
"""

import os, re, sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime

OBJECT_TYPE_DIRS = {
    'CommonModules': 'Общие модули', 'Documents': 'Документы',
    'Catalogs': 'Справочники', 'Reports': 'Отчёты',
    'DataProcessors': 'Обработки', 'InformationRegisters': 'Регистры сведений',
    'AccumulationRegisters': 'Регистры накопления', 'Enums': 'Перечисления',
    'Constants': 'Константы', 'BusinessProcesses': 'Бизнес-процессы',
    'Tasks': 'Задачи', 'ExchangePlans': 'Планы обмена',
    'ChartsOfCharacteristicTypes': 'ПВХ', 'ChartsOfCalculationTypes': 'ПВР',
    'CalculationRegisters': 'Регистры расчёта', 'DocumentJournals': 'Журналы документов',
    'HTTPServices': 'HTTP-сервисы', 'WebServices': 'Веб-сервисы',
    'ScheduledJobs': 'Регламентные задания', 'EventSubscriptions': 'Подписки на события',
    'FunctionalOptions': 'Функциональные опции', 'CommonForms': 'Общие формы',
    'CommonCommands': 'Общие команды', 'CommonTemplates': 'Общие макеты',
    'DefinedTypes': 'Определяемые типы', 'SessionParameters': 'Параметры сеанса',
    'Roles': 'Роли', 'CommonPictures': 'Общие картинки',
    'StyleItems': 'Элементы стиля', 'Subsystems': 'Подсистемы',
    'CommonAttributes': 'Общие реквизиты', 'SettingsStorages': 'Хранилища настроек',
    'FilterCriteria': 'Критерии отбора', 'IntegrationServices': 'Интеграционные сервисы',
}

MDO_PREFIX_MAP = {
    'Subsystem': 'Subsystems', 'CommonModule': 'CommonModules',
    'Document': 'Documents', 'Catalog': 'Catalogs',
    'Report': 'Reports', 'DataProcessor': 'DataProcessors',
    'InformationRegister': 'InformationRegisters',
    'AccumulationRegister': 'AccumulationRegisters',
    'Enum': 'Enums', 'Constant': 'Constants',
    'BusinessProcess': 'BusinessProcesses', 'Task': 'Tasks',
    'ExchangePlan': 'ExchangePlans',
    'ChartOfCharacteristicTypes': 'ChartsOfCharacteristicTypes',
    'ChartOfCalculationTypes': 'ChartsOfCalculationTypes',
    'CalculationRegister': 'CalculationRegisters',
    'DocumentJournal': 'DocumentJournals',
    'HTTPService': 'HTTPServices', 'WebService': 'WebServices',
    'ScheduledJob': 'ScheduledJobs', 'EventSubscription': 'EventSubscriptions',
    'FunctionalOption': 'FunctionalOptions',
    'CommonForm': 'CommonForms', 'CommonCommand': 'CommonCommands',
    'CommonTemplate': 'CommonTemplates', 'DefinedType': 'DefinedTypes',
    'SessionParameter': 'SessionParameters', 'Role': 'Roles',
    'CommonPicture': 'CommonPictures', 'StyleItem': 'StyleItems',
    'CommonAttribute': 'CommonAttributes', 'SettingsStorage': 'SettingsStorages',
    'FilterCriterion': 'FilterCriteria', 'IntegrationService': 'IntegrationServices',
    'WSReference': 'WSReferences', 'Language': 'Languages',
    'XDTOPackage': 'XDTOPackages',
    'FunctionalOptionsParameter': 'FunctionalOptionsParameters',
    'DocumentNumerator': 'DocumentNumerators',
}

KEY_TYPES = {'Общие модули', 'Документы', 'Справочники', 'Отчёты', 'Обработки',
             'Регистры сведений', 'Регистры накопления'}


def xml_tag(el):
    t = el.tag
    return t.split('}')[-1] if '}' in t else t


def parse_configuration(root_dir):
    path = os.path.join(root_dir, 'Configuration.xml')
    tree = ET.parse(path)
    props = {}
    synonym_found = False
    for el in tree.getroot().iter():
        tag = xml_tag(el)
        text = (el.text or '').strip()
        if tag == 'Name' and 'Name' not in props and text and '/' not in text:
            props['Name'] = text
        elif tag == 'Version' and 'Version' not in props and text and re.match(r'\d', text):
            props['Version'] = text
        elif tag == 'Vendor' and 'Vendor' not in props and text:
            props['Vendor'] = text
        elif tag == 'ConfigurationExtensionCompatibilityMode' and text:
            props['Compat'] = text
        elif tag == 'content' and not synonym_found and text and len(text) > 3:
            props['Synonym'] = text
            synonym_found = True
    return props


def count_objects(root_dir):
    counts = {}
    for d, ru in OBJECT_TYPE_DIRS.items():
        p = os.path.join(root_dir, d)
        if os.path.isdir(p):
            n = sum(1 for f in os.listdir(p) if f.endswith('.xml') and os.path.isfile(os.path.join(p, f)))
            if n:
                counts[ru] = n
    return counts


def parse_subsystem(xml_path, depth=0, max_depth=4):
    if depth > max_depth or not os.path.isfile(xml_path):
        return None
    try:
        tree = ET.parse(xml_path)
    except ET.ParseError:
        return None

    name = ''
    items = []
    for el in tree.getroot().iter():
        tag = xml_tag(el)
        if tag == 'Name' and not name:
            name = el.text or ''
        elif tag == 'Item':
            t = el.text or ''
            if t:
                items.append(t)

    children = []
    base = os.path.splitext(os.path.basename(xml_path))[0]
    parent = os.path.dirname(xml_path)
    for cand in [os.path.join(parent, name, 'Subsystems'), os.path.join(parent, base, 'Subsystems')]:
        if os.path.isdir(cand):
            for f in sorted(os.listdir(cand)):
                if f.endswith('.xml'):
                    c = parse_subsystem(os.path.join(cand, f), depth + 1, max_depth)
                    if c:
                        children.append(c)
            break

    by_type = defaultdict(list)
    for item in items:
        if '.' in item:
            tp, nm = item.split('.', 1)
            d = MDO_PREFIX_MAP.get(tp, tp)
            ru = OBJECT_TYPE_DIRS.get(d, tp)
            by_type[ru].append(nm)

    return {'name': name, 'content': dict(by_type), 'children': children, 'total': len(items)}


def parse_all_subsystems(root_dir):
    sdir = os.path.join(root_dir, 'Subsystems')
    if not os.path.isdir(sdir):
        return []
    result = []
    for f in sorted(os.listdir(sdir)):
        if f.endswith('.xml') and os.path.isfile(os.path.join(sdir, f)):
            s = parse_subsystem(os.path.join(sdir, f))
            if s:
                result.append(s)
    return result


def build_obj_map(subs, prefix=''):
    m = {}
    for s in subs:
        full = f"{prefix}.{s['name']}" if prefix else s['name']
        for tp, objs in s['content'].items():
            for o in objs:
                k = f"{tp}:{o}"
                if k not in m:
                    m[k] = full
        if s['children']:
            for k, v in build_obj_map(s['children'], full).items():
                if k not in m:
                    m[k] = v
    return m


def extract_exports(bsl_path, limit=20):
    if not os.path.isfile(bsl_path):
        return []
    exp = []
    pat = re.compile(r'^\s*(?:Процедура|Функция|Procedure|Function)\s+(\w+)\s*\(.*?(?:Экспорт|Export)', re.I)
    try:
        with open(bsl_path, 'r', encoding='utf-8-sig') as f:
            for line in f:
                m = pat.match(line)
                if m:
                    exp.append(m.group(1))
    except (UnicodeDecodeError, PermissionError):
        pass
    return exp[:limit]


def module_context(xml_path):
    if not os.path.isfile(xml_path):
        return '—'
    try:
        tree = ET.parse(xml_path)
    except ET.ParseError:
        return '—'
    p = {}
    for el in tree.getroot().iter():
        tag = xml_tag(el)
        text = (el.text or '').strip()
        if tag == 'Server':
            p['S'] = text == 'true'
        elif tag == 'ClientManagedApplication':
            p['C'] = text == 'true'
        elif tag == 'ServerCall':
            p['SC'] = text == 'true'
        elif tag == 'ReturnValuesReuse':
            p['cache'] = text != 'DontUse'
        elif tag == 'Global':
            p['gl'] = text == 'true'
        elif tag == 'Privileged':
            p['pr'] = text == 'true'
    parts = []
    if p.get('S') and p.get('C'):
        parts.append('КС')
    elif p.get('SC'):
        parts.append('СВ')
    elif p.get('S'):
        parts.append('С')
    elif p.get('C'):
        parts.append('К')
    if p.get('cache'):
        parts.append('кэш')
    if p.get('gl'):
        parts.append('гл')
    if p.get('pr'):
        parts.append('пр')
    return ','.join(parts) if parts else '—'


def scan_modules(root_dir, obj_map):
    mdir = os.path.join(root_dir, 'CommonModules')
    if not os.path.isdir(mdir):
        return []
    mods = []
    for d in sorted(os.listdir(mdir)):
        dp = os.path.join(mdir, d)
        if not os.path.isdir(dp):
            continue
        xml_p = os.path.join(mdir, f'{d}.xml')
        bsl_p = os.path.join(dp, 'Ext', 'Module.bsl')
        exp = extract_exports(bsl_p)
        ctx = module_context(xml_p)
        sub = obj_map.get(f'Общие модули:{d}', '')
        mods.append({'name': d, 'ctx': ctx, 'exports': exp, 'n': len(exp), 'sub': sub})
    return mods


def scan_documents(root_dir, obj_map):
    ddir = os.path.join(root_dir, 'Documents')
    if not os.path.isdir(ddir):
        return []
    docs = []
    for f in sorted(os.listdir(ddir)):
        if not f.endswith('.xml'):
            continue
        name = f[:-4]
        regs = []
        try:
            tree = ET.parse(os.path.join(ddir, f))
            in_rr = False
            for el in tree.getroot().iter():
                tag = xml_tag(el)
                if tag == 'RegisterRecords':
                    in_rr = True
                elif tag == 'Item' and in_rr:
                    t = el.text or ''
                    if '.' in t:
                        regs.append(t.split('.', 1)[1])
        except ET.ParseError:
            pass
        sub = obj_map.get(f'Документы:{name}', '')
        docs.append({'name': name, 'regs': regs, 'sub': sub})
    return docs


def flatten_subs(subs, prefix=''):
    r = []
    for s in subs:
        full = f"{prefix}.{s['name']}" if prefix else s['name']
        r.append((full, s))
        if s['children']:
            r.extend(flatten_subs(s['children'], full))
    return r


# ─── COMPACT INDEX ───────────────────────────────────────────────────────────

def gen_compact_index(config, counts, subsystems, modules, documents, path):
    """Компактный индекс ~3K токенов. Только имена и структура, без деталей."""
    L = []
    L.append(f"# PROJECT MAP — {config.get('Synonym', config.get('Name', ''))}")
    L.append(f"> v{config.get('Version','?')} | {config.get('Compat','?')} | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    L.append(f"> Регенерация: `python3 project-map/generate-map.py`")
    L.append(f"> Детали по подсистеме: `project-map/subsystems/<Имя>.md`")
    L.append('')

    top = sorted(counts.items(), key=lambda x: -x[1])[:10]
    L.append('## Объекты')
    L.append(' | '.join(f"{n} **{c}**" for n, c in top))
    L.append('')

    L.append('## Подсистемы')
    L.append('')
    for s in subsystems:
        key_counts = [(t, len(o)) for t, o in s['content'].items() if t in KEY_TYPES and len(o) > 0]
        key_counts.sort(key=lambda x: -x[1])
        summary = '; '.join(f"{t} {n}" for t, n in key_counts[:3])
        n_kids = len(s.get('children', []))
        line = f"- **{s['name']}**"
        if summary:
            line += f" [{summary}]"
        if n_kids:
            line += f" ({n_kids} дочерних)"
        L.append(line)
    L.append('')

    L.append('## Ключевые модули (топ по экспорту)')
    L.append('> Контекст: С=Серв К=Клиент КС=оба СВ=СервВызов. Подробнее → `project-map/subsystems/*.md`')
    L.append('')

    top_mods = sorted([m for m in modules if m['n'] >= 5], key=lambda x: -x['n'])[:80]
    by_sub = defaultdict(list)
    for m in top_mods:
        key = m['sub'].split('.')[0] if m['sub'] else '—'
        by_sub[key].append(m)

    for sub_name, mods in sorted(by_sub.items()):
        names = ', '.join(f"{m['name']}[{m['ctx']}]" for m in sorted(mods, key=lambda x: x['name']))
        L.append(f"**{sub_name}**: {names}")
    L.append('')

    L.append('## Ключевые документы (с движениями, топ по кол-ву регистров)')
    L.append('')
    top_docs = sorted([d for d in documents if d['regs']], key=lambda x: -len(x['regs']))[:50]
    by_sub = defaultdict(list)
    for d in top_docs:
        key = d['sub'].split('.')[0] if d['sub'] else '—'
        by_sub[key].append(d)

    for sub_name, docs in sorted(by_sub.items()):
        names = ', '.join(f"{d['name']}({len(d['regs'])}рег)" for d in sorted(docs, key=lambda x: x['name']))
        L.append(f"**{sub_name}**: {names}")
    L.append('')

    content = '\n'.join(L)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return len(content)


# ─── SUBSYSTEM DETAIL ────────────────────────────────────────────────────────

def gen_subsystem_detail(full_name, sub, modules, documents, out_dir):
    sub_mods = [m for m in modules if m['sub'] == full_name or m['sub'].startswith(full_name + '.')]
    sub_docs = [d for d in documents if d['sub'] == full_name or d['sub'].startswith(full_name + '.')]

    if not sub_mods and not sub_docs and not sub['content']:
        return False

    safe = re.sub(r'[./\\]', '_', full_name)
    L = []
    L.append(f'# {full_name}')
    L.append('')

    if sub['content']:
        L.append('## Состав')
        for tp, objs in sorted(sub['content'].items()):
            names = sorted(objs)
            if len(names) <= 15:
                L.append(f'**{tp}** ({len(names)}): {", ".join(names)}')
            else:
                L.append(f'**{tp}** ({len(names)}): {", ".join(names[:15])} ... +{len(names)-15}')
        L.append('')

    if sub['children']:
        L.append('## Дочерние подсистемы')
        for c in sub['children']:
            key = [(t, len(o)) for t, o in c['content'].items() if t in KEY_TYPES and len(o) > 0]
            key.sort(key=lambda x: -x[1])
            s = '; '.join(f"{t} {n}" for t, n in key[:4])
            L.append(f'- **{c["name"]}** [{s}]' if s else f'- **{c["name"]}**')
        L.append('')

    with_exp = sorted([m for m in sub_mods if m['n'] > 0], key=lambda x: -x['n'])
    without_exp = sorted([m for m in sub_mods if m['n'] == 0], key=lambda x: x['name'])

    if with_exp:
        L.append('## Модули с экспортом')
        L.append('')
        L.append('| Модуль | Ctx | Экспорт |')
        L.append('|--------|-----|---------|')
        for m in with_exp:
            exp = ', '.join(m['exports'][:10])
            if m['n'] > 10:
                exp += f' +{m["n"]-10}'
            L.append(f"| {m['name']} | {m['ctx']} | {exp} |")
        L.append('')

    if without_exp:
        L.append('## Модули без экспорта')
        L.append(', '.join(m['name'] for m in without_exp))
        L.append('')

    docs_r = [d for d in sub_docs if d['regs']]
    docs_nr = [d for d in sub_docs if not d['regs']]
    if docs_r:
        L.append('## Документы с движениями')
        L.append('')
        L.append('| Документ | Регистры |')
        L.append('|----------|----------|')
        for d in sorted(docs_r, key=lambda x: x['name']):
            L.append(f"| {d['name']} | {', '.join(d['regs'])} |")
        L.append('')
    if docs_nr:
        L.append('## Документы без движений')
        L.append(', '.join(d['name'] for d in sorted(docs_nr, key=lambda x: x['name'])))
        L.append('')

    content = '\n'.join(L)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, f'{safe}.md'), 'w', encoding='utf-8') as f:
        f.write(content)
    return True


# ─── MAIN ────────────────────────────────────────────────────────────────────

def main():
    root = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    map_dir = os.path.join(root, 'project-map')
    sub_dir = os.path.join(map_dir, 'subsystems')
    idx_path = os.path.join(map_dir, 'PROJECT_MAP.md')

    print(f"Сканирование: {root}")
    config = parse_configuration(root)
    print(f"  Конфигурация: {config.get('Synonym', config.get('Name', '?'))}")

    counts = count_objects(root)
    subsystems = parse_all_subsystems(root)
    print(f"  Подсистем: {len(subsystems)}")

    obj_map = build_obj_map(subsystems)
    print(f"  Маппинг: {len(obj_map)} объектов")

    modules = scan_modules(root, obj_map)
    print(f"  Модулей: {len(modules)} (с экспортом: {sum(1 for m in modules if m['n']>0)})")

    documents = scan_documents(root, obj_map)
    print(f"  Документов: {len(documents)} (с движениями: {sum(1 for d in documents if d['regs'])})")

    sz = gen_compact_index(config, counts, subsystems, modules, documents, idx_path)
    print(f"\n  INDEX: {idx_path}")
    print(f"    {sz} символов, ~{sz//4} токенов")

    flat = flatten_subs(subsystems)
    n = 0
    for full_name, sub in flat:
        if gen_subsystem_detail(full_name, sub, modules, documents, sub_dir):
            n += 1
    print(f"  SUBSYSTEMS: {n} файлов в {sub_dir}")
    print("\nГотово.")


if __name__ == '__main__':
    main()
