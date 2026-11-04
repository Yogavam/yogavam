# yogavam.com
Статический сайт для GitHub Pages (корень репозитория = корень сайта). Язык: русский.

- Тексты, схема и SEO-файлы (`*/index.html`, `sitemap.xml`, `robots.txt`, `llms.txt`, `site.webmanifest`) генерирует `tools/build.py`. HTML руками не править.
- После правки `build.py`: `python tools/build.py`, затем commit и push. Нужен Pillow: `pip install pillow`.
- Контакты, цены (`PRICES`), фото (`PHOTO_FILE`, `PHOTO_FOCUS`), сертификаты (`CERTS`), верификация — блок «НАСТРОЙКИ» в начале `build.py`.
- Новое фото: положить в корень как `natalya-umnova.jpg` (вертикальное/портрет, от 1200 px), при необходимости поправить `PHOTO_FOCUS` (например "50% 30%"), запустить build.
- Сертификаты: сканы класть в `_originals/`, добавить запись в `CERTS` (slug, src, title, short, period, issued, desc); build сам делает полный размер и миниатюру в `assets/img/certificates/`. Страница `/certificates/` и превью на главной обновятся сами.
- Стили: `assets/style.css` (править напрямую). Иконки и og.jpg: `python tools/make_images.py` (нужен playwright).
- `_originals/` в .gitignore: полноразмерные сканы, не публиковать.
- Шрифт Geologica лежит в `assets/fonts/` (self-hosted, OFL). Внешних скриптов и CDN нет, JS нет. Отдельных AI-файлов и спецразметки «для ИИ» не добавлять: Google их игнорирует.
- Не обещать лечение; дисклеймер в подвале сохранять.
