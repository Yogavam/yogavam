# yogavam.com
Статический сайт для GitHub Pages (корень репозитория = корень сайта). Язык: русский.

- Тексты, схема и SEO-файлы (`*/index.html`, `sitemap.xml`, `robots.txt`, `llms.txt`, `site.webmanifest`) генерирует `tools/build.py`. HTML руками не править.
- После правки `build.py`: `python tools/build.py`, затем commit и push.
- Контакты, сертификаты, фото, верификация — блок «НАСТРОЙКИ» в начале `build.py`.
- Сертификаты: `assets/img/certificates/<имя>.jpg` (1400 px) и `<имя>-thumb.jpg` (600 px); добавить запись в `CERTS`.
- Стили: `assets/style.css` (править напрямую). Иконки и og.jpg: `python tools/make_images.py` (нужен playwright).
- `_originals/` в .gitignore: полноразмерные сканы, не публиковать.
- Без внешних скриптов и шрифтов, без JS. Отдельных AI-файлов и спецразметки «для ИИ» не добавлять: Google их игнорирует.
- Не обещать лечение; дисклеймер в подвале сохранять.
