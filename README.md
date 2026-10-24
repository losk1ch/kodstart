# Кодстарт — образовательный сайт по программированию

Статический сайт (чистый HTML/CSS/JS, без сборки и зависимостей). Структура страниц повторяет структуру из лабораторной работы №2:

- Каталог курсов → Программирование (Python, C#, JavaScript, Swift, Web-разработка), По уровню, Практика, Справочник / Полезное (+ Статьи)
- О нас → Описание проекта, Цели и задачи, Авторы материалов
- Контакты, FAQ, Политика конфиденциальности, Пользовательское соглашение, Карта сайта

SEO-основа: осмысленные URL, один H1 на странице, title/description, canonical, Open Graph, хлебные крошки (+ микроразметка BreadcrumbList), FAQPage и Article, `sitemap.xml`, `robots.txt`, HTML-карта сайта.

## Публикация на GitHub Pages

1. Создайте на GitHub публичный репозиторий (например, `kodstart`).
2. Загрузите в него **содержимое этой папки** (файл `index.html` должен лежать в корне репозитория).
3. Откройте **Settings → Pages**, в разделе *Build and deployment* выберите **Deploy from a branch**, ветку `main` и папку `/ (root)`, нажмите Save.
4. Через 1–2 минуты сайт будет доступен по адресу `https://ВАШ_ЛОГИН.github.io/kodstart/`.

Через командную строку:

```bash
git init
git add .
git commit -m "Первая версия сайта"
git branch -M main
git remote add origin https://github.com/ВАШ_ЛОГИН/kodstart.git
git push -u origin main
```

Если назвать репозиторий `ВАШ_ЛОГИН.github.io`, сайт откроется в корне: `https://ВАШ_ЛОГИН.github.io/`.

## Важно: укажите свой адрес

Страницы уже сгенерированы с адресом-заглушкой `https://USERNAME.github.io/kodstart` (он используется в canonical, `sitemap.xml`, `robots.txt`). Перед публикацией пересоберите сайт со своим адресом и e-mail (нужен Python 3):

```bash
SITE_URL=https://ВАШ_ЛОГИН.github.io/kodstart CONTACT_EMAIL=you@mail.ru python3 generate.py
```

(в Windows PowerShell: `$env:SITE_URL="https://ВАШ_ЛОГИН.github.io/kodstart"; $env:CONTACT_EMAIL="you@mail.ru"; python generate.py`)

Все внутренние ссылки относительные, поэтому сайт работает и в подпапке, и в корне домена.

## Как менять содержимое

Весь текст лежит в `generate.py` (списки `LANGS`, `LEVELS`, `TASKS`, `QUIZ`, `MINI`, `ARTICLES`, `FAQ`). Измените данные и запустите `generate.py` ещё раз — все страницы, меню и sitemap обновятся. Стили — `assets/style.css`.

## После публикации (для SEO-части лабораторной)

- Добавьте сайт в Яндекс Вебмастер и Google Search Console, отправьте `sitemap.xml`.
- Подключите Яндекс Метрику (и обновите политику конфиденциальности).
