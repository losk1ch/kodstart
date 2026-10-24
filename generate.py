#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Генератор статического сайта «Кодстарт» (образовательный ресурс по программированию).
Структура страниц повторяет структуру из лабораторной работы №2.

Запуск:
    python3 generate.py                                   # с адресом-заглушкой
    SITE_URL=https://USER.github.io/REPO python3 generate.py
    python3 generate.py https://USER.github.io/REPO

SITE_URL нужен для canonical, sitemap.xml, robots.txt и Open Graph.
Все внутренние ссылки на страницах относительные, поэтому сайт работает
и в подпапке (USER.github.io/REPO/), и в корне домена.
"""
import datetime
import html
import json
import os
import sys
from urllib.parse import urlparse

SITE_URL = os.environ.get("SITE_URL", "https://USERNAME.github.io/kodstart").rstrip("/")
if len(sys.argv) > 1:
    SITE_URL = sys.argv[1].rstrip("/")
CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "hello@example.com")
SITE_NAME = "Кодстарт"
BASE_PATH = urlparse(SITE_URL).path.rstrip("/")
OUT = os.path.dirname(os.path.abspath(__file__))
TODAY = datetime.date.today().isoformat()

# ----------------------------------------------------------------------------
# Структура сайта (из лабораторной работы)
# ----------------------------------------------------------------------------
NAV = [
    ("catalog", "Каталог курсов", [
        ("catalog/programming", "Программирование", [
            ("catalog/programming/python", "Python"),
            ("catalog/programming/csharp", "C#"),
            ("catalog/programming/javascript", "JavaScript"),
            ("catalog/programming/swift", "Swift"),
            ("catalog/programming/web", "Web-разработка"),
        ]),
        ("catalog/levels", "По уровню", [
            ("catalog/levels/beginner", "Начальный"),
            ("catalog/levels/intermediate", "Средний"),
            ("catalog/levels/advanced", "Продвинутый"),
        ]),
        ("catalog/practice", "Практика", [
            ("catalog/practice/tasks", "Практические задания"),
            ("catalog/practice/tests", "Тесты"),
            ("catalog/practice/mini-projects", "Мини-проекты"),
        ]),
        ("catalog/reference", "Справочник / Полезное", [
            ("catalog/reference/syntax", "Синтаксис языков"),
            ("catalog/reference/examples", "Примеры кода"),
            ("catalog/reference/errors", "Частые ошибки"),
            ("catalog/reference/articles", "Статьи"),
        ]),
    ]),
    ("about", "О нас", [
        ("about/project", "Описание проекта"),
        ("about/goals", "Цели и задачи"),
        ("about/authors", "Авторы материалов"),
    ]),
    ("contacts", "Контакты", []),
    ("faq", "FAQ", []),
]

TITLES = {"": "Главная"}


def _walk(items):
    for it in items:
        TITLES[it[0]] = it[1]
        if len(it) > 2:
            _walk(it[2])


_walk(NAV)
TITLES.update({
    "privacy": "Политика конфиденциальности",
    "terms": "Пользовательское соглашение",
    "sitemap": "Карта сайта",
})

PAGES = []  # (path, priority) для sitemap.xml


# ----------------------------------------------------------------------------
# Вспомогательные функции
# ----------------------------------------------------------------------------
def esc(s):
    return html.escape(s, quote=True)


def L(path):
    """Относительная ссылка; @ROOT@ заменяется при записи страницы."""
    return "@ROOT@" + (path + "/" if path else "")


def code(lang, src):
    return '<pre><code class="lang-%s">%s</code></pre>' % (lang, html.escape(src.strip("\n")))


def card(path, title, text, badge=None):
    b = '<span class="badge">%s</span>' % esc(badge) if badge else ""
    return '<a class="card" href="%s">%s<h3>%s</h3><p>%s</p></a>' % (L(path), b, esc(title), esc(text))


def cards(items):
    return '<div class="grid">%s</div>' % "".join(card(*i) for i in items)


def ul(items):
    return "<ul>%s</ul>" % "".join("<li>%s</li>" % i for i in items)


def section(h2, inner):
    return "<section><h2>%s</h2>%s</section>" % (esc(h2), inner)


def menu_html():
    out = ['<ul class="menu" id="menu">']
    for it in NAV:
        path, title = it[0], it[1]
        kids = it[2] if len(it) > 2 else []
        if not kids:
            out.append('<li><a href="%s">%s</a></li>' % (L(path), esc(title)))
        elif path == "catalog":
            out.append('<li class="has-sub mega"><a href="%s">%s</a>'
                       '<button class="sub-toggle" type="button" aria-label="Открыть подменю" aria-expanded="false">▾</button>'
                       '<div class="sub mega-grid">' % (L(path), esc(title)))
            for grp in kids:
                out.append('<div class="col"><a class="col-title" href="%s">%s</a><ul>' % (L(grp[0]), esc(grp[1])))
                for k in grp[2]:
                    out.append('<li><a href="%s">%s</a></li>' % (L(k[0]), esc(k[1])))
                out.append("</ul></div>")
            out.append("</div></li>")
        else:
            out.append('<li class="has-sub"><a href="%s">%s</a>'
                       '<button class="sub-toggle" type="button" aria-label="Открыть подменю" aria-expanded="false">▾</button>'
                       '<ul class="sub">' % (L(path), esc(title)))
            for k in kids:
                out.append('<li><a href="%s">%s</a></li>' % (L(k[0]), esc(k[1])))
            out.append("</ul></li>")
    out.append("</ul>")
    return "".join(out)


def crumbs(path):
    parts = [p for p in path.split("/") if p]
    items = [("", "Главная")]
    cur = []
    for p in parts:
        cur.append(p)
        key = "/".join(cur)
        items.append((key, TITLES.get(key, p)))
    return items


LAYOUT = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>@TITLE@</title>
<meta name="description" content="@DESC@">
<link rel="canonical" href="@CANONICAL@">
<meta property="og:type" content="website">
<meta property="og:locale" content="ru_RU">
<meta property="og:site_name" content="@SITE@">
<meta property="og:title" content="@TITLE@">
<meta property="og:description" content="@DESC@">
<meta property="og:url" content="@CANONICAL@">
<meta name="theme-color" content="#1d4ed8">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%231d4ed8'/%3E%3Ctext x='32' y='43' font-size='30' text-anchor='middle' fill='white' font-family='monospace'%3E%7B%7D%3C/text%3E%3C/svg%3E">
<link rel="stylesheet" href="@ROOT@assets/style.css">
@LD@
</head>
<body>
<a class="skip" href="#content">Перейти к содержимому</a>
<header class="site-header">
  <div class="container header-row">
    <a class="logo" href="@HOME@"><span class="logo-mark">{ }</span> @SITE@</a>
    <button class="burger" type="button" aria-label="Меню" aria-expanded="false" aria-controls="menu">☰</button>
    <nav aria-label="Главное меню">@MENU@</nav>
  </div>
</header>
<main id="content">
<div class="container">
@CRUMBS@
@BODY@
</div>
</main>
<footer class="site-footer">
  <div class="container footer-row">
    <div>
      <strong>@SITE@</strong>
      <p>Образовательный ресурс по программированию: курсы, практика, тесты и справочник.</p>
      <p class="muted">Учебный проект, выполненный в рамках лабораторной работы №2 (ТулГУ).</p>
    </div>
    <ul>
      <li><a href="@ROOT@catalog/">Каталог курсов</a></li>
      <li><a href="@ROOT@about/">О нас</a></li>
      <li><a href="@ROOT@contacts/">Контакты</a></li>
      <li><a href="@ROOT@faq/">FAQ</a></li>
    </ul>
    <ul>
      <li><a href="@ROOT@privacy/">Политика конфиденциальности</a></li>
      <li><a href="@ROOT@terms/">Пользовательское соглашение</a></li>
      <li><a href="@ROOT@sitemap/">Карта сайта</a></li>
    </ul>
  </div>
</footer>
<script src="@ROOT@assets/site.js" defer></script>
@EXTRA_JS@
</body>
</html>
"""


def write_page(path, title, desc, h1, body, ld=None, priority="0.6", extra_js="", lead=None):
    depth = len([p for p in path.split("/") if p])
    root = "../" * depth
    canonical = SITE_URL + "/" + (path + "/" if path else "")
    trail = crumbs(path)
    ld_items = []
    if path:
        bc = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1, "name": name,
                 "item": SITE_URL + "/" + (p + "/" if p else "")}
                for i, (p, name) in enumerate(trail)
            ],
        }
        ld_items.append(bc)
    for x in (ld or []):
        ld_items.append(x)
    ld_html = "\n".join(
        '<script type="application/ld+json">%s</script>' % json.dumps(x, ensure_ascii=False).replace("</", "<\\/")
        for x in ld_items
    )
    if path:
        crumbs_html = '<nav class="crumbs" aria-label="Хлебные крошки"><ol>%s</ol></nav>' % "".join(
            ('<li><a href="@ROOT@%s">%s</a></li>' % ((p + "/" if p else ""), esc(n)))
            if i < len(trail) - 1 else '<li aria-current="page">%s</li>' % esc(n)
            for i, (p, n) in enumerate(trail)
        )
    else:
        crumbs_html = ""
    head = ""
    if h1:
        head = "<h1>%s</h1>" % esc(h1)
        if lead:
            head += '<p class="lead">%s</p>' % lead
    full_title = title if path == "" else "%s | %s" % (title, SITE_NAME)
    page = (LAYOUT
            .replace("@TITLE@", esc(full_title))
            .replace("@DESC@", esc(desc))
            .replace("@CANONICAL@", canonical)
            .replace("@SITE@", SITE_NAME)
            .replace("@LD@", ld_html)
            .replace("@MENU@", menu_html())
            .replace("@CRUMBS@", crumbs_html)
            .replace("@BODY@", head + body)
            .replace("@EXTRA_JS@", extra_js))
    page = page.replace('href="@HOME@"', 'href="%s"' % (root or "./"))
    page = page.replace('"@ROOT@"', '"%s"' % (root or "./"))
    page = page.replace("@ROOT@", root)
    target = os.path.join(OUT, path) if path else OUT
    os.makedirs(target, exist_ok=True)
    with open(os.path.join(target, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)
    PAGES.append((path, priority))


# ----------------------------------------------------------------------------
# Данные: языки
# ----------------------------------------------------------------------------
LANGS = {
    "python": {
        "name": "Python",
        "h1": "Обучение Python с нуля",
        "title": "Обучение Python с нуля: уроки, практика и тесты",
        "desc": "Обучение Python: основы языка, функции, ООП и работа с файлами. Уроки с примерами кода, практические задания и тесты для проверки знаний.",
        "lead": "Python — язык с простым и читаемым синтаксисом. Он одинаково хорошо подходит для первых шагов в программировании, автоматизации, анализа данных и веб-разработки.",
        "learn": ["Переменные, типы данных, ввод и вывод", "Условия и циклы", "Функции и модули", "Объектно-ориентированное программирование", "Работа с файлами и обработка ошибок"],
        "topics": [
            ("Основы языка", "Переменные, условия и циклы — базовые конструкции, из которых строится любая программа. В Python блоки кода выделяются отступами.", "python",
             'name = "Анна"\nage = 20\n\nif age >= 18:\n    print(f"{name}, вам уже есть 18")\n\nfor i in range(3):\n    print(i)'),
            ("Функции", "Функция группирует повторяющийся код и принимает параметры, в том числе со значениями по умолчанию.", "python",
             "def area(width, height=1):\n    return width * height\n\nprint(area(3, 4))  # 12\nprint(area(5))     # 5"),
            ("Объектно-ориентированное программирование", "Класс описывает объект: его данные (атрибуты) и поведение (методы). Наследование позволяет переиспользовать код.", "python",
             'class Student:\n    def __init__(self, name):\n        self.name = name\n\n    def hello(self):\n        return f"Привет, я {self.name}"\n\nprint(Student("Олег").hello())'),
            ("Работа с файлами", "Конструкция with сама закроет файл, даже если внутри возникнет ошибка. Для русского текста указывайте кодировку.", "python",
             'with open("notes.txt", "w", encoding="utf-8") as f:\n    f.write("Первая строка\\n")\n\nwith open("notes.txt", encoding="utf-8") as f:\n    print(f.read())'),
        ],
    },
    "csharp": {
        "name": "C#",
        "h1": "Обучение C# с нуля",
        "title": "Обучение C# с нуля: уроки, задания и примеры кода",
        "desc": "Уроки C# для начинающих: типы данных, коллекции, классы, LINQ и работа с файлами. Примеры кода, практические задания и тесты.",
        "lead": "C# — основной язык платформы .NET. На нём пишут десктопные и веб-приложения, серверные сервисы и игры на Unity.",
        "learn": ["Типы данных и консольный ввод-вывод", "Условия, циклы и коллекции", "Классы, свойства, наследование", "LINQ — запросы к коллекциям", "Работа с файлами"],
        "topics": [
            ("Основы и типы данных", "C# — язык со строгой типизацией: тип переменной задаётся при объявлении или выводится через var.", "csharp",
             'int age = 20;\nstring name = "Анна";\nConsole.WriteLine($"{name}, {age} лет");'),
            ("Условия, циклы и коллекции", "List<T> — динамический список. Цикл foreach удобен для обхода любых коллекций.", "csharp",
             "var numbers = new List<int> { 1, 2, 3, 4 };\nforeach (var n in numbers)\n{\n    if (n % 2 == 0) Console.WriteLine(n);\n}"),
            ("Классы и ООП", "Свойства заменяют пары методов get/set, а выражение через => делает короткие методы лаконичными.", "csharp",
             'public class Student\n{\n    public string Name { get; }\n    public Student(string name) => Name = name;\n    public string Hello() => $"Привет, я {Name}";\n}'),
            ("LINQ", "LINQ позволяет фильтровать, сортировать и преобразовывать коллекции в одну строку (нужен using System.Linq).", "csharp",
             "var evens = numbers.Where(n => n % 2 == 0).ToList();\nvar sum = numbers.Sum();"),
            ("Работа с файлами", "Класс File из System.IO читает и пишет файлы одной командой.", "csharp",
             'File.WriteAllText("notes.txt", "Первая строка");\nConsole.WriteLine(File.ReadAllText("notes.txt"));'),
        ],
    },
    "javascript": {
        "name": "JavaScript",
        "h1": "Уроки JavaScript для начинающих",
        "title": "Уроки JavaScript для начинающих: обучение с нуля",
        "desc": "Обучение JavaScript с нуля: переменные, массивы, DOM, события и асинхронность. Понятные уроки с кодом, практика и тесты.",
        "lead": "JavaScript работает в каждом браузере и делает страницы интерактивными. С помощью Node.js его используют и на сервере.",
        "learn": ["Переменные, типы и операторы", "Функции и стрелочные функции", "Массивы и методы filter, map, reduce", "Работа с DOM и событиями", "Асинхронность: fetch и async/await"],
        "topics": [
            ("Основы языка", "Используйте const для значений, которые не переприсваиваются, и let — для остальных. Ключевое слово var считается устаревшим.", "javascript",
             'const name = "Анна";\nlet age = 20;\nif (age >= 18) {\n  console.log(`${name}, вам уже есть 18`);\n}'),
            ("Массивы и функции", "Методы массивов принимают функции и позволяют писать код декларативно.", "javascript",
             "const nums = [1, 2, 3, 4];\nconst evens = nums.filter(n => n % 2 === 0);\nconst squares = nums.map(n => n * n);\nconsole.log(evens, squares);"),
            ("Работа с DOM", "DOM — это дерево элементов страницы. Скрипт находит элемент и подписывается на событие.", "javascript",
             'const btn = document.querySelector("#theme");\nbtn.addEventListener("click", () => {\n  document.body.classList.toggle("dark");\n});'),
            ("Асинхронность", "async/await делает код с запросами к серверу похожим на обычный последовательный код.", "javascript",
             'async function load() {\n  const res = await fetch("https://api.example.com/data");\n  const data = await res.json();\n  console.log(data);\n}\nload();'),
        ],
    },
    "swift": {
        "name": "Swift",
        "h1": "Обучение Swift: разработка под iOS",
        "title": "Обучение Swift с нуля: язык для iOS и macOS",
        "desc": "Уроки Swift для начинающих: константы и переменные, опциональные типы, структуры, замыкания. Примеры кода и практика для разработки под iOS.",
        "lead": "Swift — современный язык Apple для приложений на iPhone, iPad и Mac. Он строгий и безопасный: многие ошибки находятся ещё до запуска программы.",
        "learn": ["Константы let и переменные var", "Опциональные типы и безопасная работа с nil", "Структуры и классы", "Замыкания и функции высшего порядка", "Основы SwiftUI"],
        "topics": [
            ("Константы и переменные", "let объявляет константу, var — переменную. Swift сам выводит тип, но его можно указать явно.", "swift",
             'let name = "Анна"\nvar age = 20\nage += 1\nprint("\\(name), \\(age) лет")'),
            ("Опциональные типы", "Тип со знаком ? может содержать nil. Значение безопасно извлекается через if let.", "swift",
             'var city: String? = nil\nif let c = city {\n    print(c)\n} else {\n    print("Город не указан")\n}'),
            ("Структуры", "Структуры в Swift — типы-значения: при присваивании они копируются.", "swift",
             'struct Student {\n    let name: String\n    func hello() -> String { "Привет, я \\(name)" }\n}\nprint(Student(name: "Олег").hello())'),
            ("Замыкания", "Замыкание — функция без имени. Сокращённая запись $0 обозначает первый аргумент.", "swift",
             "let nums = [1, 2, 3, 4]\nlet evens = nums.filter { $0 % 2 == 0 }\nprint(evens)  // [2, 4]"),
        ],
    },
    "web": {
        "name": "Web-разработка",
        "h1": "Web-разработка с нуля: HTML, CSS и JavaScript",
        "title": "Web-разработка с нуля: HTML, CSS и JavaScript",
        "desc": "Курс по web-разработке: вёрстка на HTML и CSS, адаптивный дизайн, JavaScript в браузере, Git и публикация сайта на GitHub Pages.",
        "lead": "Web-разработка начинается с трёх технологий: HTML описывает структуру страницы, CSS — оформление, JavaScript — поведение.",
        "learn": ["Семантическая вёрстка на HTML5", "Оформление и адаптивность на CSS", "Интерактивность на JavaScript", "Система контроля версий Git", "Публикация сайта на GitHub Pages"],
        "topics": [
            ("HTML: структура страницы", "Семантические теги помогают и пользователям, и поисковым системам понять содержание страницы.", "html",
             '<!DOCTYPE html>\n<html lang="ru">\n<head>\n  <meta charset="utf-8">\n  <title>Моя страница</title>\n</head>\n<body>\n  <h1>Привет, мир!</h1>\n</body>\n</html>'),
            ("CSS: оформление и адаптивность", "Flexbox выстраивает элементы в ряд, а медиазапрос перестраивает их на узких экранах.", "css",
             ".card { display: flex; gap: 16px; padding: 16px; border-radius: 12px; }\n\n@media (max-width: 600px) {\n  .card { flex-direction: column; }\n}"),
            ("JavaScript в браузере", "Скрипт реагирует на действия пользователя и меняет страницу без перезагрузки.", "javascript",
             'document.querySelector("button").addEventListener("click", () => {\n  alert("Привет!");\n});'),
            ("Git и публикация", "Git хранит историю изменений, а GitHub Pages бесплатно публикует статический сайт из репозитория.", "bash",
             'git init\ngit add .\ngit commit -m "Первый коммит"\ngit push origin main'),
        ],
    },
}

LEVELS = {
    "beginner": {
        "name": "Начальный",
        "h1": "Программирование для начинающих: начальный уровень",
        "title": "Программирование для начинающих: начальный уровень",
        "desc": "Начальный уровень обучения программированию: переменные, условия, циклы, функции. Подойдёт тем, кто никогда не писал код.",
        "lead": "Уровень для тех, кто ни разу не писал код. Начинаем с простых программ и учимся мыслить алгоритмами.",
        "who": ["Вы только знакомитесь с программированием", "Нужно выбрать первый язык и настроить рабочее место", "Хотите быстро получить первый работающий результат"],
        "learn": ["Установка языка и редактора кода", "Переменные, типы данных, ввод и вывод", "Условия и циклы", "Функции и первые структуры данных", "Чтение сообщений об ошибках"],
        "result": "Вы сможете самостоятельно написать небольшую консольную программу: калькулятор, угадайку или конвертер.",
        "langs": ["python", "javascript"],
        "hours": "Ориентировочно 4–6 недель при 5 часах занятий в неделю.",
    },
    "intermediate": {
        "name": "Средний",
        "h1": "Программирование: средний уровень",
        "title": "Программирование: средний уровень обучения",
        "desc": "Средний уровень: структуры данных, ООП, работа с файлами и API, отладка и Git. Переходите от упражнений к самостоятельным проектам.",
        "lead": "Уровень для тех, кто знает синтаксис, но теряется при создании собственного проекта.",
        "who": ["Вы умеете писать простые программы", "Хотите разобраться с ООП и структурами данных", "Планируете делать мини-проекты для портфолио"],
        "learn": ["Списки, словари, множества и их сложность", "Классы, наследование, инкапсуляция", "Работа с файлами, JSON и внешними API", "Отладка и обработка исключений", "Git: ветки, коммиты, pull request"],
        "result": "Вы сможете собрать проект из нескольких модулей и выложить его в публичный репозиторий.",
        "langs": ["python", "csharp", "javascript", "swift"],
        "hours": "Ориентировочно 6–8 недель при 5 часах занятий в неделю.",
    },
    "advanced": {
        "name": "Продвинутый",
        "h1": "Программирование: продвинутый уровень",
        "title": "Программирование: продвинутый уровень обучения",
        "desc": "Продвинутый уровень: паттерны проектирования, тестирование, асинхронность, оптимизация и архитектура приложений.",
        "lead": "Уровень для тех, кто уверенно пишет код и хочет делать его качественнее: чище, быстрее и надёжнее.",
        "who": ["Вы уже делали собственные проекты", "Хотите писать тесты и поддерживаемый код", "Интересуют архитектура и производительность"],
        "learn": ["Паттерны проектирования", "Автоматические тесты и TDD", "Асинхронность и многопоточность", "Профилирование и оптимизация", "Архитектура приложений, code review"],
        "result": "Вы сможете спроектировать приложение с тестами и документацией и объяснить свои архитектурные решения.",
        "langs": ["python", "csharp", "javascript"],
        "hours": "Ориентировочно 8–10 недель при 5 часах занятий в неделю.",
    },
}

TASKS = [
    ("Сумма цифр числа", "python", "Начальный", "Введите целое число и выведите сумму его цифр. Например, для 1234 ответ — 10.", "python",
     "n = int(input())\nprint(sum(int(d) for d in str(abs(n))))"),
    ("Чётные числа в диапазоне", "python", "Начальный", "Выведите все чётные числа от 1 до N включительно, через пробел.", "python",
     "n = int(input())\nprint(*range(2, n + 1, 2))"),
    ("Подсчёт слов в файле", "python", "Средний", "Прочитайте текстовый файл и выведите пять самых частых слов с количеством повторов.", "python",
     'from collections import Counter\n\nwith open("text.txt", encoding="utf-8") as f:\n    words = f.read().lower().split()\n\nfor word, count in Counter(words).most_common(5):\n    print(word, count)'),
    ("Палиндром", "javascript", "Начальный", "Напишите функцию isPalindrome(s), которая проверяет, читается ли строка одинаково в обе стороны (без учёта регистра).", "javascript",
     "function isPalindrome(s) {\n  const t = s.toLowerCase();\n  return t === [...t].reverse().join(\"\");\n}\nconsole.log(isPalindrome(\"Шалаш\")); // true"),
    ("Фильтрация и сортировка", "javascript", "Средний", "Дан массив объектов {name, age}. Оставьте тех, кому от 18 лет, и отсортируйте по имени.", "javascript",
     "const people = [{name: \"Олег\", age: 17}, {name: \"Анна\", age: 21}, {name: \"Борис\", age: 30}];\nconst adults = people\n  .filter(p => p.age >= 18)\n  .sort((a, b) => a.name.localeCompare(b.name));\nconsole.log(adults);"),
    ("FizzBuzz", "csharp", "Начальный", "Выведите числа от 1 до 100. Для кратных 3 выведите Fizz, для кратных 5 — Buzz, для кратных обоим — FizzBuzz.", "csharp",
     'for (int i = 1; i <= 100; i++)\n{\n    if (i % 15 == 0) Console.WriteLine("FizzBuzz");\n    else if (i % 3 == 0) Console.WriteLine("Fizz");\n    else if (i % 5 == 0) Console.WriteLine("Buzz");\n    else Console.WriteLine(i);\n}'),
    ("Факториал", "swift", "Начальный", "Напишите функцию factorial(n), которая возвращает n!. Для n = 5 ответ — 120.", "swift",
     "func factorial(_ n: Int) -> Int {\n    n <= 1 ? 1 : n * factorial(n - 1)\n}\nprint(factorial(5))  // 120"),
    ("Декоратор замера времени", "python", "Продвинутый", "Напишите декоратор timed, который печатает время выполнения функции.", "python",
     "import time\nfrom functools import wraps\n\ndef timed(func):\n    @wraps(func)\n    def wrapper(*args, **kwargs):\n        start = time.perf_counter()\n        result = func(*args, **kwargs)\n        print(f\"{func.__name__}: {time.perf_counter() - start:.4f} c\")\n        return result\n    return wrapper"),
]

QUIZ = {
    "python": {"name": "Python", "questions": [
        {"q": "Какой тип данных у значения 3.14?", "options": ["int", "float", "str", "bool"], "answer": 1, "explain": "Числа с дробной частью в Python имеют тип float."},
        {"q": "Что выведет print(len([1, 2, 3]))?", "options": ["2", "3", "4", "Ошибку"], "answer": 1, "explain": "len возвращает количество элементов списка — 3."},
        {"q": "Какое ключевое слово объявляет функцию?", "options": ["func", "function", "def", "lambda"], "answer": 2, "explain": "Функции объявляются через def."},
        {"q": "Какой режим open() используется для записи в файл?", "options": ["\"r\"", "\"w\"", "\"x+\"", "\"b\""], "answer": 1, "explain": "\"w\" — запись (файл создаётся или перезаписывается)."},
    ]},
    "javascript": {"name": "JavaScript", "questions": [
        {"q": "Какое ключевое слово объявляет константу?", "options": ["var", "let", "const", "static"], "answer": 2, "explain": "const объявляет переменную, которую нельзя переприсвоить."},
        {"q": "Что вернёт typeof null?", "options": ["\"null\"", "\"undefined\"", "\"object\"", "\"number\""], "answer": 2, "explain": "Это историческая особенность языка: typeof null === \"object\"."},
        {"q": "Какой метод добавляет элемент в конец массива?", "options": ["push", "pop", "shift", "concat"], "answer": 0, "explain": "push добавляет в конец, pop удаляет с конца."},
        {"q": "Что возвращает async-функция?", "options": ["undefined", "Promise", "Callback", "Массив"], "answer": 1, "explain": "async-функция всегда возвращает Promise."},
    ]},
    "csharp": {"name": "C#", "questions": [
        {"q": "Какой тип предназначен для целых чисел?", "options": ["int", "float", "string", "char"], "answer": 0, "explain": "int — 32-битное целое."},
        {"q": "Как вывести строку в консоль?", "options": ["print()", "Console.WriteLine()", "echo", "System.out.println()"], "answer": 1, "explain": "В C# используется Console.WriteLine."},
        {"q": "Как записывается наследование класса B от A?", "options": ["class B extends A", "class B : A", "class B inherits A", "class B -> A"], "answer": 1, "explain": "Наследование задаётся двоеточием: class B : A."},
        {"q": "Что такое List<T>?", "options": ["Массив фиксированного размера", "Обобщённая динамическая коллекция", "Словарь", "Строка"], "answer": 1, "explain": "List<T> — динамический список элементов типа T."},
    ]},
    "swift": {"name": "Swift", "questions": [
        {"q": "Чем let отличается от var?", "options": ["Ничем", "let — константа, var — переменная", "let — глобальная", "var — константа"], "answer": 1, "explain": "let объявляет константу, var — изменяемую переменную."},
        {"q": "Что означает тип String?", "options": ["Строка, которая может быть nil", "Массив строк", "Обязательная строка", "Символ"], "answer": 0, "explain": "Знак ? делает тип опциональным: значение может отсутствовать."},
        {"q": "Какая функция выводит данные в консоль?", "options": ["print", "console.log", "echo", "writeln"], "answer": 0, "explain": "В Swift используется print."},
        {"q": "Структуры (struct) в Swift — это...", "options": ["Ссылочные типы", "Типы-значения", "Протоколы", "Модули"], "answer": 1, "explain": "struct — тип-значение: при присваивании данные копируются."},
    ]},
}

MINI = [
    ("Консольный калькулятор", "Python", "Начальный", "Программа читает выражение, считает результат и обрабатывает ошибки ввода.", ["Ввод и разбор строки", "Функции для каждой операции", "Обработка деления на ноль"]),
    ("Список дел в браузере", "JavaScript", "Начальный", "Страница, где можно добавлять, отмечать и удалять задачи; данные хранятся в localStorage.", ["HTML-форма и список", "События и работа с DOM", "Сохранение в localStorage"]),
    ("Угадай число", "C#", "Начальный", "Игра в консоли: компьютер загадывает число, а пользователь угадывает с подсказками.", ["Генератор случайных чисел", "Цикл с условием выхода", "Подсчёт попыток"]),
    ("Конвертер валют", "Swift", "Средний", "Приложение пересчитывает суммы по курсам из локального набора данных.", ["Словарь курсов", "Опциональные типы", "Интерфейс на SwiftUI"]),
    ("Сайт-портфолио", "Web", "Средний", "Адаптивный сайт о себе, опубликованный на GitHub Pages.", ["Семантическая вёрстка", "Адаптивный CSS", "Публикация через Git"]),
    ("Сборщик новостей", "Python", "Продвинутый", "Скрипт скачивает RSS-ленты, фильтрует записи и сохраняет в JSON.", ["Запросы к сети", "Разбор XML/JSON", "Тесты на парсер"]),
]

ARTICLES = [
    ("start", "С чего начать изучение программирования",
     "Пошаговый план для новичка: как выбрать цель, настроить рабочее место и не бросить обучение на второй неделе.",
     [("Определите цель", "Сначала решите, зачем вам программирование: сайты, автоматизация рутины, анализ данных или мобильные приложения. От цели зависит первый язык и набор инструментов."),
      ("Настройте рабочее место", "Для старта достаточно редактора кода (например, Visual Studio Code), установленного языка и умения запускать программу из терминала. Для JavaScript хватит браузера и текстового файла."),
      ("Пишите код каждый день", "Лучше заниматься по 30–60 минут ежедневно, чем по пять часов раз в неделю. После каждого урока решайте задание без подсказок и только потом сверяйтесь с решением."),
      ("Делайте маленькие проекты", "Как только освоите условия, циклы и функции, сделайте мини-проект. Законченная простая программа даёт больше, чем десять недочитанных уроков.")]),
    ("first-language", "Как выбрать первый язык программирования",
     "Сравнение Python, JavaScript, C# и Swift: для каких задач подходит каждый и с чего начать новичку.",
     [("Python — универсальный старт", "Простой синтаксис позволяет сосредоточиться на логике. Язык подходит для автоматизации, анализа данных, скриптов и бэкенда."),
      ("JavaScript — если нужен веб", "Язык работает в браузере без установки. Он быстро даёт видимый результат — интерактивную страницу."),
      ("C# — приложения и игры", "Язык со строгой типизацией и мощными инструментами. Подходит для десктопных программ, серверных сервисов и игр на Unity."),
      ("Swift — разработка для Apple", "Выбирайте Swift, если цель — приложения для iPhone и Mac. Для практики потребуется компьютер Apple и среда Xcode."),
      ("Главное — начать", "Первый язык не определяет карьеру: основные идеи (переменные, циклы, функции, ООП) одинаковы. Выбрав любой из языков, вы сможете позже освоить другой гораздо быстрее.")]),
    ("read-errors", "Как читать сообщения об ошибках",
     "Учимся разбирать traceback и тексты ошибок: где искать тип ошибки, номер строки и причину.",
     [("Ошибка — это подсказка", "Сообщение об ошибке говорит, что именно и где пошло не так. Новички часто пугаются красного текста, хотя в нём почти всегда есть вся нужная информация."),
      ("Читайте с конца", "В Python главное находится в последней строке traceback: там тип ошибки и пояснение. Выше показана цепочка вызовов, а в ней — файл и номер строки."),
      ("Ищите номер строки", "Найдите строку, указанную в сообщении, и проверьте её и несколько строк выше: ошибка часто возникает из-за предыдущей инструкции."),
      ("Гуглите тип ошибки", "Скопируйте тип и текст ошибки без названий ваших переменных и найдите объяснение. Посмотрите также раздел «Частые ошибки» на нашем сайте.")]),
    ("github-pages", "Как опубликовать сайт на GitHub Pages",
     "Пошаговая инструкция: создаём репозиторий, загружаем файлы и включаем бесплатный хостинг статического сайта.",
     [("Создайте репозиторий", "На GitHub нажмите New repository и дайте имя, например kodstart. Репозиторий должен быть публичным (для бесплатного аккаунта)."),
      ("Загрузите файлы", "Файл index.html должен лежать в корне репозитория. Загрузите файлы через веб-интерфейс или командами Git."),
      ("Включите Pages", "В репозитории откройте Settings → Pages, выберите ветку main и папку / (root), сохраните. Через минуту-две сайт станет доступен по адресу https://ИМЯ.github.io/kodstart/."),
      ("Проверьте ссылки", "Если страницы открываются, но не загружаются стили, проверьте пути: на GitHub Pages сайт часто лежит не в корне домена, а в подпапке. Поэтому используйте относительные ссылки.")]),
]
for _slug, _title, _d, _s in ARTICLES:
    TITLES["catalog/reference/articles/" + _slug] = _title

FAQ = [
    ("Нужно ли платить за обучение?", "Нет. Материалы сайта открыты и бесплатны — это учебный проект."),
    ("С какого языка программирования лучше начать?", "Для первого знакомства подойдут Python или JavaScript. Подробнее — в статье «Как выбрать первый язык программирования»."),
    ("Нужно ли знать математику?", "Для начального уровня достаточно школьной математики. Более сложные разделы нужны только для отдельных направлений, например анализа данных."),
    ("Сколько времени занимает начальный уровень?", "Ориентировочно 4–6 недель при 5 часах занятий в неделю. Скорость зависит от вашего опыта и регулярности."),
    ("Как проверить свои знания?", "Пройдите тесты в разделе «Практика → Тесты» и решите практические задания с разбором решения."),
    ("Что нужно установить для занятий?", "Для Python, C# и Swift потребуется установленный язык или среда разработки, для JavaScript и web-разработки достаточно браузера и редактора кода."),
    ("Выдаются ли сертификаты?", "Нет. Ресурс учебный и сертификатов не выдаёт."),
    ("Как связаться с авторами?", "Контактные данные указаны на странице «Контакты»."),
]


# ----------------------------------------------------------------------------
# Страницы
# ----------------------------------------------------------------------------
def build_home():
    body = []
    body.append('<div class="hero"><p>Бесплатный учебный ресурс</p>'
                '<p class="hero-lead">Структурированные уроки, практические задания, тесты и справочник по Python, C#, JavaScript, Swift и web-разработке.</p>'
                '<p><a class="btn" href="%s">Выбрать курс</a> <a class="btn btn-ghost" href="%s">Пройти тест</a></p></div>'
                % (L("catalog"), L("catalog/practice/tests")))
    body.append(section("Направления обучения", cards([
        ("catalog/programming", "Курсы программирования", "Python, C#, JavaScript, Swift и web-разработка."),
        ("catalog/practice/tasks", "Практические задания", "Задачи с разбором решений по каждому языку."),
        ("catalog/practice/tests", "Тесты и проверка знаний", "Короткие тесты с объяснением ответов."),
        ("catalog/reference/articles", "Статьи и учебные материалы", "Советы новичкам и разбор частых вопросов."),
    ])))
    body.append(section("Языки программирования", cards(
        [("catalog/programming/" + k, v["name"], v["lead"]) for k, v in LANGS.items()])))
    body.append(section("Выберите свой уровень", cards(
        [("catalog/levels/" + k, v["name"], v["lead"]) for k, v in LEVELS.items()])))
    body.append(section("Справочник", cards([
        ("catalog/reference/syntax", "Синтаксис языков", "Сравнение конструкций четырёх языков в одной таблице."),
        ("catalog/reference/examples", "Примеры кода", "Короткие решения типовых задач."),
        ("catalog/reference/errors", "Частые ошибки", "Причины ошибок и способы их исправления."),
    ])))
    body.append(section("Новые статьи", cards(
        [("catalog/reference/articles/" + s, t, d) for s, t, d, _ in ARTICLES])))
    ld = [{
        "@context": "https://schema.org", "@type": "WebSite", "name": SITE_NAME, "url": SITE_URL + "/",
        "inLanguage": "ru",
        "description": "Образовательный ресурс по программированию: курсы, практика, тесты и справочник.",
    }]
    write_page("", "Обучение программированию онлайн: курсы, уроки и практика — " + SITE_NAME,
               "Бесплатное обучение программированию: уроки Python, C#, JavaScript и Swift, практические задания, тесты, мини-проекты и справочник.",
               "Обучение программированию онлайн: курсы, уроки и практика", "".join(body), ld=ld, priority="1.0")


def build_hubs():
    write_page("catalog", "Каталог курсов по программированию",
               "Каталог курсов: языки программирования, уровни подготовки, практика и справочные материалы.",
               "Каталог курсов по программированию",
               section("Выберите раздел", cards([
                   ("catalog/programming", "Программирование", "Курсы по языкам: Python, C#, JavaScript, Swift, web."),
                   ("catalog/levels", "По уровню", "Начальный, средний и продвинутый уровни."),
                   ("catalog/practice", "Практика", "Задания, тесты и мини-проекты."),
                   ("catalog/reference", "Справочник / Полезное", "Синтаксис, примеры кода, ошибки и статьи."),
               ])),
               lead="Все материалы разделены по языку, уровню и типу: курс, практика, справочник.", priority="0.9")

    write_page("catalog/programming", "Курсы программирования по языкам",
               "Курсы программирования: Python, C#, JavaScript, Swift и web-разработка. Выберите язык и начните обучение.",
               "Курсы программирования по языкам",
               cards([("catalog/programming/" + k, v["name"], v["lead"]) for k, v in LANGS.items()]),
               lead="Выберите язык: в каждом разделе вас ждут основы, примеры кода, задания и тесты.", priority="0.9")

    write_page("catalog/levels", "Обучение программированию по уровням",
               "Уровни обучения программированию: начальный, средний и продвинутый. Найдите подходящий для вашей подготовки.",
               "Обучение программированию по уровням",
               cards([("catalog/levels/" + k, v["name"], v["lead"]) for k, v in LEVELS.items()]),
               lead="Не знаете, с чего начать? Выберите уровень, который соответствует вашей подготовке.", priority="0.8")

    write_page("catalog/practice", "Практика по программированию",
               "Практика: задания с решениями, тесты для проверки знаний и мини-проекты для портфолио.",
               "Практика по программированию",
               cards([
                   ("catalog/practice/tasks", "Практические задания", "Задачи разной сложности с решениями."),
                   ("catalog/practice/tests", "Тесты", "Проверьте знания по каждому языку."),
                   ("catalog/practice/mini-projects", "Мини-проекты", "Идеи небольших проектов для портфолио."),
               ]),
               lead="Навык приходит только с практикой. Выберите формат: задачи, тест или проект.", priority="0.8")

    write_page("catalog/reference", "Справочник по программированию",
               "Справочник: сравнение синтаксиса языков, примеры кода, частые ошибки и полезные статьи.",
               "Справочник по программированию",
               cards([
                   ("catalog/reference/syntax", "Синтаксис языков", "Сравнительная таблица конструкций."),
                   ("catalog/reference/examples", "Примеры кода", "Решения типовых задач."),
                   ("catalog/reference/errors", "Частые ошибки", "Причины и способы исправления."),
                   ("catalog/reference/articles", "Статьи", "Материалы для самостоятельного изучения."),
               ]),
               lead="Короткие материалы, к которым удобно возвращаться во время работы.", priority="0.8")

    write_page("about", "О проекте",
               "О проекте «Кодстарт»: описание, цели и задачи образовательного ресурса, авторы материалов.",
               "О проекте",
               cards([
                   ("about/project", "Описание проекта", "Что это за сайт и для кого он."),
                   ("about/goals", "Цели и задачи", "Чего мы хотим достичь."),
                   ("about/authors", "Авторы материалов", "Кто подготовил сайт."),
               ]), priority="0.5")


def build_languages():
    for key, d in LANGS.items():
        path = "catalog/programming/" + key
        body = []
        body.append(section("Чему вы научитесь", ul([esc(x) for x in d["learn"]])))
        topics = "".join(
            "<article><h3>%s</h3><p>%s</p>%s</article>" % (esc(t), esc(txt), code(lang, src))
            for t, txt, lang, src in d["topics"])
        body.append(section("Программа и примеры", topics))
        body.append(section("Закрепите знания", cards([
            ("catalog/practice/tasks", "Практические задания", "Решите задачи по теме «%s»." % d["name"]),
            ("catalog/practice/tests", "Тест", "Проверьте себя и посмотрите разбор ответов."),
            ("catalog/reference/syntax", "Синтаксис", "Сравните конструкции с другими языками."),
        ])))
        others = [(("catalog/programming/" + k), v["name"], v["lead"]) for k, v in LANGS.items() if k != key]
        body.append(section("Другие языки", cards(others)))
        write_page(path, d["title"], d["desc"], d["h1"], "".join(body), lead=esc(d["lead"]), priority="0.9")


def build_levels():
    for key, d in LEVELS.items():
        body = []
        body.append(section("Кому подойдёт", ul([esc(x) for x in d["who"]])))
        body.append(section("Что вы изучите", ul([esc(x) for x in d["learn"]])))
        body.append(section("Результат", "<p>%s</p><p class=\"muted\">%s</p>" % (esc(d["result"]), esc(d["hours"]))))
        body.append(section("Рекомендуемые языки", cards(
            [("catalog/programming/" + k, LANGS[k]["name"], LANGS[k]["lead"]) for k in d["langs"]])))
        others = [("catalog/levels/" + k, v["name"], v["lead"]) for k, v in LEVELS.items() if k != key]
        body.append(section("Другие уровни", cards(others)))
        write_page("catalog/levels/" + key, d["title"], d["desc"], d["h1"], "".join(body), lead=esc(d["lead"]), priority="0.8")


def build_practice():
    # Задания
    items = []
    for title, lang, level, text, clang, sol in TASKS:
        items.append(
            '<article class="task"><h3>%s</h3><p><span class="badge">%s</span> <span class="badge badge-alt">%s</span></p>'
            '<p>%s</p><details><summary>Показать решение</summary>%s</details></article>'
            % (esc(title), esc(LANGS[lang]["name"]), esc(level), esc(text), code(clang, sol)))
    write_page("catalog/practice/tasks", "Практические задания по программированию",
               "Практические задания по Python, C#, JavaScript и Swift с условиями и решениями. Задачи для начинающих и продвинутых.",
               "Практические задания по программированию", "".join(items),
               lead="Сначала решите задачу самостоятельно, затем сверьтесь с решением.", priority="0.8")

    # Тесты
    data = json.dumps(QUIZ, ensure_ascii=False).replace("</", "<\\/")
    body = ('<div id="quiz" class="quiz"></div>'
            '<noscript><p>Для работы тестов включите JavaScript.</p></noscript>'
            '<script type="application/json" id="quiz-data">%s</script>' % data)
    write_page("catalog/practice/tests", "Тесты по программированию онлайн",
               "Онлайн-тесты по Python, JavaScript, C# и Swift. Проверьте знания и получите объяснение каждого ответа.",
               "Тесты по программированию онлайн", body,
               lead="Выберите язык, ответьте на вопросы и нажмите «Проверить» — мы покажем результат и объясним ответы.",
               extra_js='<script src="@ROOT@assets/quiz.js" defer></script>', priority="0.8")

    # Мини-проекты
    items = []
    for title, lang, level, text, steps in MINI:
        items.append(
            '<article class="task"><h3>%s</h3><p><span class="badge">%s</span> <span class="badge badge-alt">%s</span></p>'
            '<p>%s</p><p><strong>Этапы:</strong></p>%s</article>'
            % (esc(title), esc(lang), esc(level), esc(text), ul([esc(s) for s in steps])))
    write_page("catalog/practice/mini-projects", "Мини-проекты для начинающих программистов",
               "Идеи мини-проектов для портфолио: калькулятор, список дел, игра, конвертер, сайт-портфолио и сборщик новостей.",
               "Мини-проекты для начинающих программистов", "".join(items),
               lead="Небольшие законченные проекты — лучший способ закрепить знания и пополнить портфолио.", priority="0.7")


def build_reference():
    # Синтаксис
    rows = [
        ("Переменная", 'name = "Анна"', 'string name = "Анна";', 'let name = "Анна";', 'let name = "Анна"'),
        ("Вывод", 'print("Привет")', 'Console.WriteLine("Привет");', 'console.log("Привет");', 'print("Привет")'),
        ("Список", "nums = [1, 2, 3]", "var nums = new List<int> {1, 2, 3};", "const nums = [1, 2, 3];", "let nums = [1, 2, 3]"),
        ("Условие", "if x > 0:\n    print('+')\nelse:\n    print('-')",
         'if (x > 0) Console.WriteLine("+");\nelse Console.WriteLine("-");',
         "if (x > 0) console.log('+');\nelse console.log('-');",
         'if x > 0 { print("+") } else { print("-") }'),
        ("Цикл", "for i in range(3):\n    print(i)", "for (int i = 0; i < 3; i++)\n    Console.WriteLine(i);",
         "for (let i = 0; i < 3; i++) {\n  console.log(i);\n}", "for i in 0..<3 {\n    print(i)\n}"),
        ("Функция", "def add(a, b):\n    return a + b", "int Add(int a, int b) => a + b;",
         "const add = (a, b) => a + b;", "func add(_ a: Int, _ b: Int) -> Int {\n    a + b\n}"),
    ]
    thead = "<tr><th>Конструкция</th><th>Python</th><th>C#</th><th>JavaScript</th><th>Swift</th></tr>"
    trs = "".join(
        "<tr><th scope=\"row\">%s</th>%s</tr>" % (
            esc(r[0]), "".join("<td><pre><code>%s</code></pre></td>" % html.escape(c) for c in r[1:]))
        for r in rows)
    body = '<div class="table-wrap"><table class="syntax"><thead>%s</thead><tbody>%s</tbody></table></div>' % (thead, trs)
    body += section("Что дальше", cards([
        ("catalog/reference/examples", "Примеры кода", "Решения типовых задач на четырёх языках."),
        ("catalog/practice/tasks", "Практика", "Закрепите конструкции на заданиях."),
    ]))
    write_page("catalog/reference/syntax", "Синтаксис языков программирования: сравнение",
               "Сравнительная таблица синтаксиса Python, C#, JavaScript и Swift: переменные, условия, циклы и функции.",
               "Синтаксис языков программирования: сравнение", body,
               lead="Как одна и та же конструкция выглядит в разных языках.", priority="0.8")

    # Примеры кода
    ex = [
        ("Hello, World!", {
            "Python": ("python", 'print("Hello, World!")'),
            "C#": ("csharp", 'Console.WriteLine("Hello, World!");'),
            "JavaScript": ("javascript", 'console.log("Hello, World!");'),
            "Swift": ("swift", 'print("Hello, World!")')}),
        ("Сумма элементов списка", {
            "Python": ("python", "print(sum([1, 2, 3, 4]))"),
            "C#": ("csharp", "// using System.Linq;\nConsole.WriteLine(new[] { 1, 2, 3, 4 }.Sum());"),
            "JavaScript": ("javascript", "console.log([1, 2, 3, 4].reduce((a, b) => a + b, 0));"),
            "Swift": ("swift", "print([1, 2, 3, 4].reduce(0, +))")}),
        ("Максимальный элемент", {
            "Python": ("python", "print(max([3, 9, 2]))"),
            "C#": ("csharp", "// using System.Linq;\nConsole.WriteLine(new[] { 3, 9, 2 }.Max());"),
            "JavaScript": ("javascript", "console.log(Math.max(...[3, 9, 2]));"),
            "Swift": ("swift", "print([3, 9, 2].max()!)")}),
    ]
    body = ""
    for title, variants in ex:
        blocks = "".join("<div><h3>%s</h3>%s</div>" % (esc(n), code(l, c)) for n, (l, c) in variants.items())
        body += section(title, '<div class="grid2">%s</div>' % blocks)
    write_page("catalog/reference/examples", "Примеры кода: решения типовых задач",
               "Готовые примеры кода на Python, C#, JavaScript и Swift: вывод текста, сумма и максимум элементов списка.",
               "Примеры кода: решения типовых задач", body,
               lead="Короткие решения типовых задач на разных языках.", priority="0.7")

    # Частые ошибки
    errs = [
        ("Python", "IndentationError", "Неверные отступы: тело функции или условия должно быть сдвинуто.", "python", "def f():\nprint(1)", "def f():\n    print(1)"),
        ("Python", "TypeError: can only concatenate str", "Строку складывают с числом.", "python", 'print("Возраст: " + 20)', 'print("Возраст: " + str(20))'),
        ("Python", "NameError", "Переменная используется до объявления или с опечаткой в имени.", "python", "print(total)", "total = 0\nprint(total)"),
        ("JavaScript", "Cannot read properties of undefined", "Обращение к свойству несуществующего объекта.", "javascript", "const user = {};\nconsole.log(user.address.city);", "const user = {};\nconsole.log(user.address?.city);"),
        ("JavaScript", "Путаница == и ===", "Оператор == приводит типы и даёт неожиданные результаты.", "javascript", 'console.log(0 == "");   // true', 'console.log(0 === "");  // false'),
        ("C#", "NullReferenceException", "Обращение к члену объекта, равного null.", "csharp", "string s = null;\nConsole.WriteLine(s.Length);", "string? s = null;\nConsole.WriteLine(s?.Length ?? 0);"),
        ("C#", "CS0103: имя не существует в текущем контексте", "Переменная не объявлена или объявлена в другой области видимости.", "csharp", "Console.WriteLine(count);", "int count = 0;\nConsole.WriteLine(count);"),
        ("Swift", "Unexpectedly found nil", "Принудительное извлечение (!) значения, равного nil.", "swift", "let n: Int? = nil\nprint(n!)", "let n: Int? = nil\nif let n = n { print(n) }"),
    ]
    items = []
    for lang, name, cause, cl, bad, good in errs:
        items.append(
            '<article class="task"><h3>%s</h3><p><span class="badge">%s</span></p><p>%s</p>'
            '<div class="grid2"><div><h4>Ошибка</h4>%s</div><div><h4>Исправление</h4>%s</div></div></article>'
            % (esc(name), esc(lang), esc(cause), code(cl, bad), code(cl, good)))
    write_page("catalog/reference/errors", "Частые ошибки начинающих программистов",
               "Разбор частых ошибок на Python, JavaScript, C# и Swift: причины возникновения и способы исправления.",
               "Частые ошибки начинающих программистов", "".join(items),
               lead="Что означает сообщение об ошибке и как её исправить.", priority="0.7")

    # Статьи
    write_page("catalog/reference/articles", "Статьи для начинающих программистов",
               "Статьи и учебные материалы: как начать программировать, выбрать язык, читать ошибки и опубликовать сайт.",
               "Статьи для начинающих программистов",
               cards([("catalog/reference/articles/" + s, t, d) for s, t, d, _ in ARTICLES]),
               lead="Материалы для самостоятельного изучения.", priority="0.7")
    for slug, title, desc, secs in ARTICLES:
        body = "".join("<h2>%s</h2><p>%s</p>" % (esc(h), esc(p)) for h, p in secs)
        if slug == "github-pages":
            body += "<h2>Команды для загрузки через Git</h2>" + code("bash",
                "git init\ngit add .\ngit commit -m \"Первая версия сайта\"\ngit branch -M main\ngit remote add origin https://github.com/ИМЯ/kodstart.git\ngit push -u origin main")
        others = [("catalog/reference/articles/" + s, t, d) for s, t, d, _ in ARTICLES if s != slug][:3]
        body += section("Читайте также", cards(others))
        ld = [{
            "@context": "https://schema.org", "@type": "Article", "headline": title, "description": desc,
            "inLanguage": "ru", "datePublished": TODAY, "dateModified": TODAY,
            "author": {"@type": "Person", "name": "Потапов В.С."},
            "mainEntityOfPage": SITE_URL + "/catalog/reference/articles/" + slug + "/",
        }]
        write_page("catalog/reference/articles/" + slug, title, desc, title, body, ld=ld, priority="0.6")


def build_about():
    write_page("about/project", "Описание проекта",
               "«Кодстарт» — образовательный ресурс по программированию: курсы, практические задания, тесты и справочник.",
               "Описание проекта",
               "<p>«Кодстарт» — образовательный ресурс по программированию. Он помогает пройти путь от первой программы до собственного проекта: выбрать язык и уровень, изучить тему, выполнить практическое задание и проверить знания.</p>"
               + section("Что есть на сайте", ul([
                   "Курсы по Python, C#, JavaScript, Swift и web-разработке",
                   "Три уровня подготовки: начальный, средний, продвинутый",
                   "Практические задания, тесты и мини-проекты",
                   "Справочник: синтаксис, примеры кода, частые ошибки и статьи"]))
               + section("Для кого этот сайт", "<p>Для школьников, студентов и всех, кто хочет научиться программировать с нуля или систематизировать знания.</p>")
               + "<p class=\"muted\">Проект создан в рамках лабораторной работы №2 по дисциплине «Технологии оптимизации и продвижения веб-ресурсов» (ТулГУ) как основа для дальнейшей SEO-оптимизации.</p>",
               priority="0.5")
    write_page("about/goals", "Цели и задачи проекта",
               "Цели и задачи образовательного ресурса «Кодстарт»: структурированные материалы, практика и удобная навигация.",
               "Цели и задачи проекта",
               section("Цель", "<p>Предоставить пользователю структурированные учебные материалы, практические задания и дополнительные информационные материалы по программированию.</p>")
               + section("Задачи", ul([
                   "Разделить материалы по языку программирования, уровню подготовки и типу контента",
                   "Обеспечить понятный путь пользователя: от выбора темы до практического задания",
                   "Сделать навигацию простой, с вложенностью не более 3–4 уровней",
                   "Подготовить структуру, удобную для SEO-оптимизации: осмысленные адреса, заголовки, хлебные крошки, карта сайта"])),
               priority="0.5")
    write_page("about/authors", "Авторы материалов",
               "Авторы материалов образовательного ресурса «Кодстарт».",
               "Авторы материалов",
               "<article class=\"task\"><h3>Потапов В.С.</h3><p>Студент группы 220632, Институт прикладной математики и компьютерных наук, Тульский государственный университет.</p>"
               "<p>Разработка структуры сайта, подготовка учебных материалов и вёрстка.</p></article>",
               priority="0.4")


def build_service():
    write_page("contacts", "Контакты",
               "Контакты проекта «Кодстарт»: как связаться с авторами, задать вопрос или предложить тему.",
               "Контакты",
               "<p>Есть вопрос, замечание или идея новой темы? Напишите нам.</p>"
               "<p><strong>E-mail:</strong> <a href=\"mailto:%s\">%s</a></p>" % (CONTACT_EMAIL, CONTACT_EMAIL)
               + '<form class="contact" action="mailto:%s" method="post" enctype="text/plain">'
                 '<label>Ваше имя<input type="text" name="name" required></label>'
                 '<label>Ваш e-mail<input type="email" name="email" required></label>'
                 '<label>Сообщение<textarea name="message" rows="5" required></textarea></label>'
                 '<button class="btn" type="submit">Отправить</button>'
                 '<p class="muted">Кнопка откроет вашу почтовую программу с готовым письмом.</p></form>' % CONTACT_EMAIL,
               priority="0.5")

    faq_html = "".join("<details><summary>%s</summary><p>%s</p></details>" % (esc(q), esc(a)) for q, a in FAQ)
    ld = [{
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ],
    }]
    write_page("faq", "FAQ: частые вопросы об обучении",
               "Ответы на частые вопросы: стоимость, выбор языка, нужное ПО, длительность обучения и проверка знаний.",
               "Часто задаваемые вопросы", faq_html, ld=ld, priority="0.6")

    write_page("privacy", "Политика конфиденциальности",
               "Политика конфиденциальности учебного сайта «Кодстарт»: какие данные собираются и как они используются.",
               "Политика конфиденциальности",
               "<p>Сайт «Кодстарт» — учебный статический проект. Мы не требуем регистрации и не собираем персональные данные автоматически.</p>"
               + section("Какие данные обрабатываются", "<p>Если вы пишете нам на e-mail, мы получаем ваш адрес и текст сообщения. Эти данные используются только для ответа.</p>")
               + section("Cookies и счётчики", "<p>На данный момент сайт не использует собственные cookies и сервисы веб-аналитики. При подключении таких сервисов эта страница будет обновлена.</p>")
               + section("Хостинг", "<p>Сайт размещён на GitHub Pages; хостинг-провайдер может фиксировать технические данные посещений согласно своей политике.</p>")
               + section("Связь", "<p>По вопросам обработки данных пишите на <a href=\"mailto:%s\">%s</a>.</p>" % (CONTACT_EMAIL, CONTACT_EMAIL)),
               priority="0.2")
    write_page("terms", "Пользовательское соглашение",
               "Пользовательское соглашение учебного сайта «Кодстарт»: правила использования материалов.",
               "Пользовательское соглашение",
               section("Общие положения", "<p>Используя сайт, вы соглашаетесь с настоящими условиями. Сайт носит образовательный характер, а материалы предоставляются «как есть».</p>")
               + section("Использование материалов", "<p>Материалы можно использовать в личных учебных целях. Примеры кода можно свободно копировать и изменять. Републикация текстов целиком допускается со ссылкой на источник.</p>")
               + section("Ответственность", "<p>Авторы стремятся к точности материалов, но не гарантируют их применимость в конкретных проектах и не несут ответственности за возможные последствия их использования.</p>")
               + section("Изменения", "<p>Условия могут быть изменены. Актуальная версия всегда размещена на этой странице.</p>"),
               priority="0.2")


def build_sitemap_html():
    def render(items):
        out = "<ul>"
        for it in items:
            out += '<li><a href="%s">%s</a>' % (L(it[0]), esc(it[1]))
            if len(it) > 2:
                out += render(it[2])
            if it[0] == "catalog/reference/articles":
                out += "<ul>%s</ul>" % "".join(
                    '<li><a href="%s">%s</a></li>' % (L("catalog/reference/articles/" + s), esc(t)) for s, t, _, _ in ARTICLES)
            out += "</li>"
        return out + "</ul>"

    body = '<ul><li><a href="%s">Главная</a></li></ul>' % L("")
    body += render(NAV)
    body += '<ul><li><a href="%s">Политика конфиденциальности</a></li><li><a href="%s">Пользовательское соглашение</a></li></ul>' % (L("privacy"), L("terms"))
    write_page("sitemap", "Карта сайта", "HTML-карта сайта «Кодстарт»: все разделы и страницы в одном списке.",
               "Карта сайта", '<div class="sitemap">%s</div>' % body, priority="0.3")


def build_technical():
    # sitemap.xml
    urls = []
    for path, prio in PAGES:
        loc = SITE_URL + "/" + (path + "/" if path else "")
        urls.append("  <url><loc>%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>" % (loc, TODAY, prio))
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s\n</urlset>\n' % "\n".join(urls)
    with open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(xml)
    # robots.txt
    with open(os.path.join(OUT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write("User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % SITE_URL)
    # .nojekyll
    open(os.path.join(OUT, ".nojekyll"), "w").close()
    # 404.html (абсолютные пути от базового пути сайта)
    base = BASE_PATH or ""
    page = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>Страница не найдена | %(site)s</title>
<link rel="stylesheet" href="%(base)s/assets/style.css">
</head>
<body>
<main class="container notfound">
<h1>404 — страница не найдена</h1>
<p>Возможно, адрес набран с ошибкой или страница была перемещена.</p>
<p><a class="btn" href="%(base)s/">На главную</a> <a class="btn btn-ghost" href="%(base)s/catalog/">Каталог курсов</a></p>
</main>
</body>
</html>
""" % {"site": SITE_NAME, "base": base}
    with open(os.path.join(OUT, "404.html"), "w", encoding="utf-8") as f:
        f.write(page)


def main():
    build_home()
    build_hubs()
    build_languages()
    build_levels()
    build_practice()
    build_reference()
    build_about()
    build_service()
    build_sitemap_html()
    build_technical()
    print("Готово: %d страниц. SITE_URL = %s" % (len(PAGES), SITE_URL))


if __name__ == "__main__":
    main()
