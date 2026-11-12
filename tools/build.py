#!/usr/bin/env python3
"""Генератор yogavam.com. Запуск: python tools/build.py
Пишет страницы в корень репозитория (корень репозитория = корень сайта).
Руками меняются: блок НАСТРОЙКИ и тексты ниже. HTML не править."""
import json, os, html, datetime, urllib.parse, hashlib, glob

e = html.escape
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = ROOT
IMG = os.path.join(ROOT, "assets", "img")
CERT_DIR = os.path.join(IMG, "certificates")
ORIG = os.path.join(ROOT, "_originals")

# ===================== НАСТРОЙКИ =====================
DOMAIN = "https://yogavam.com"
BRAND = "Yogavam"
AUTHOR = "Наталья Умнова"
AUTHOR_FIRST = "Наталья"
WA_NUMBER = "995599018912"
YT_URL = "https://www.youtube.com/@yogaumnova"
TG_URL = "https://t.me/yogaumnova"
IG_URL = "https://www.instagram.com/nata_umnova_/"
FORM_KEY = ""                         # ключ Web3Forms (access_key). Пока пусто: форма и кнопка «Написать» не выводятся
PHOTO_FILE = "natalya-umnova.jpg"     # исходное фото: assets/img/natalya-umnova.jpg (вертикальное 4:5, от 1200×1500)
PHOTO_FOCUS = "50% 30%"               # что держать в кадре при обрезке: x y (лицо обычно 25–35% сверху)
OG_IMAGE = "/assets/img/og.jpg"
GOOGLE_VERIFY = ""
YANDEX_VERIFY = ""

# Стоимость одного индивидуального занятия
PRICES = {
    "online": {"USD": 40, "RUB": 3500, "GEL": 70},
    "batumi": {"USD": 50, "RUB": 4000, "GEL": 100},
}
CUR = {"USD": "$", "RUB": "₽", "GEL": "₾"}

ORG = "International Open Yoga Foundation Europe"
ORG2 = "Академия йоги и йогатерапии Татьяны Дудиной (Yoga Dudina)"
# Сертификаты. slug -> файлы assets/img/certificates/<slug>.jpg и <slug>-thumb.jpg.
# Если рядом лежит скан _originals/<src>, оба файла создаются автоматически.
CERTS = [
    {"slug": "open-yoga-master-2021", "src": "Docs393.jpg", "group": "Йога",
     "title": "Мастер Open Yoga", "short": "Мастер Open Yoga", "org": ORG, "period": "2014–2021", "issued": "2021-11-13",
     "desc": "Высшая квалификация программы Open Yoga. Даёт право вести практические занятия, воркшопы, ретриты и теоретические уроки."},
    {"slug": "open-yoga-teacher-2018", "src": "Docs395.jpg", "group": "Йога",
     "title": "Преподаватель Open Yoga", "short": "Преподаватель Open Yoga", "org": ORG, "period": "2014–2018", "issued": "2018-11-17",
     "desc": "Квалификация преподавателя Open Yoga. Даёт право вести практические занятия, воркшопы, ретриты и теоретические уроки."},
    {"slug": "open-yoga-instructor-2017", "src": "Docs394.jpg", "group": "Йога",
     "title": "Курс инструкторов Open Yoga", "short": "Курс инструкторов, 816 часов", "org": ORG, "period": "2014–2017", "issued": "2017-11-04",
     "desc": "Первая ступень обучения: 447 часов теоретических занятий и 369 часов практики. Даёт право вести практические и теоретические занятия Open Yoga."},
    {"slug": "tbs-2024", "src": "ТБС.jpg", "group": "Йогатерапия и биомеханика",
     "title": "Тазобедренные суставы", "short": "Тазобедренные суставы", "org": ORG2, "period": "2024", "hours": 26, "issued": "2024-08-23",
     "desc": "Курс «Тазобедренные суставы» из цикла «Йогатерапия и биомеханика» для преподавателей йоги и йогатерапии, без сдачи экзамена."},
    {"slug": "pelvic-floor-2024", "src": "Тазовое дно.jpg", "group": "Йогатерапия и биомеханика",
     "title": "Тазовое дно", "short": "Тазовое дно", "org": ORG2, "period": "2024", "hours": 54, "issued": "2024-05-24",
     "desc": "Курс «Тазовое дно» из цикла «Йогатерапия и биомеханика» для преподавателей йоги и йогатерапии, без сдачи экзамена."},
    {"slug": "breathing-2024", "src": "Дыхание.jpg", "group": "Йогатерапия и биомеханика",
     "title": "Дыхание и дыхательные техники", "short": "Дыхание и дыхательные техники", "org": ORG2, "period": "2024", "hours": 36, "issued": "2024-02-02",
     "desc": "Курс «Дыхание и дыхательные техники» из цикла «Йогатерапия и биомеханика» для преподавателей йоги и йогатерапии, без сдачи экзамена."},
    {"slug": "feet-2024", "src": "Стопы.jpg", "group": "Йогатерапия и биомеханика",
     "title": "Стопы", "short": "Стопы", "org": ORG2, "period": "2024", "hours": 59, "issued": "2024-02-02",
     "desc": "Курс «Стопы» из цикла «Йогатерапия и биомеханика» для преподавателей йоги и йогатерапии, без сдачи экзамена."},
    {"slug": "neck-2023", "src": "Шейный отдел.jpg", "group": "Йогатерапия и биомеханика",
     "title": "Шейный отдел", "short": "Шейный отдел", "org": ORG2, "period": "2023", "hours": 58, "issued": "2023-10-31",
     "desc": "Курс «Шейный отдел» из цикла «Йогатерапия и биомеханика» для преподавателей йоги и йогатерапии, без сдачи экзамена."},
    {"slug": "pelvis-si-2023", "src": "Таз и КПС.jpg", "group": "Йогатерапия и биомеханика",
     "title": "Таз и крестцово-подвздошный сустав", "short": "Таз и крестцово-подвздошный сустав", "org": ORG2, "period": "2023", "hours": 50, "issued": "2023-07-18",
     "desc": "Курс «Таз и крестцово-подвздошный сустав» из цикла «Йогатерапия и биомеханика» для преподавателей йоги и йогатерапии, без сдачи экзамена."},
    {"slug": "shoulder-arm-2023", "src": "Плечо запястье локоть.jpg", "group": "Йогатерапия и биомеханика",
     "title": "Плечо, запястье, локоть", "short": "Плечо, запястье, локоть", "org": ORG2, "period": "2023", "hours": 41, "issued": "2023-04-14",
     "desc": "Курс «Плечо, запястье, локоть» из цикла «Йогатерапия и биомеханика» для преподавателей йоги и йогатерапии, без сдачи экзамена."},
    {"slug": "posture-thoracic-2022", "src": "Осанка и грудной отдел.jpg", "group": "Йогатерапия и биомеханика",
     "title": "Осанка и грудной отдел", "short": "Осанка и грудной отдел", "org": ORG2, "period": "2022", "hours": 46, "issued": "2022-10-31",
     "desc": "Курс «Осанка и грудной отдел» из цикла «Йогатерапия и биомеханика» для преподавателей йоги и йогатерапии, без сдачи экзамена."},
    {"slug": "lumbar-2022", "src": "Поясница.jpg", "group": "Йогатерапия и биомеханика",
     "title": "Поясница", "short": "Поясница", "org": ORG2, "period": "2022", "hours": 84, "issued": "2022-04-05",
     "desc": "Курс «Поясница» из цикла «Йогатерапия и биомеханика» для преподавателей йоги и йогатерапии, без сдачи экзамена."},
]
TODAY = datetime.date.today().isoformat()
# =====================================================

WA_TEXT = f"Здравствуйте, {AUTHOR_FIRST}! Хочу узнать о занятиях."
WA_URL = f"https://wa.me/{WA_NUMBER}?text=" + urllib.parse.quote(WA_TEXT)
NB = " "
RU_MONTHS = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"]

person_id = DOMAIN + "/#person"
website_id = DOMAIN + "/#website"
abs_url = lambda p: DOMAIN + p


# ---------- подготовка картинок ----------
PHOTO_W = PHOTO_H = 0
PHOTO_WIDTHS = []

def prepare_images():
    global PHOTO_W, PHOTO_H, PHOTO_WIDTHS
    try:
        from PIL import Image
    except ImportError:
        print("ВНИМАНИЕ: нет pillow (pip install pillow), картинки не обработаны")
        Image = None
    src = os.path.join(IMG, PHOTO_FILE)
    if os.path.exists(src) and Image:
        im = Image.open(src).convert("RGB")
        PHOTO_W, PHOTO_H = im.size
        for old in glob.glob(os.path.join(IMG, "photo-*.webp")): os.remove(old)
        PHOTO_WIDTHS = [w for w in (640, 1000, 1400) if w < PHOTO_W] + [PHOTO_W]
        for w in PHOTO_WIDTHS:
            h = round(im.height * w / im.width)
            im.resize((w, h), Image.LANCZOS).save(os.path.join(IMG, f"photo-{w}.webp"), "WEBP", quality=82, method=6)
    elif os.path.exists(src):
        from struct import unpack
        PHOTO_W, PHOTO_H = 900, 1125
    for c in CERTS:
        full = os.path.join(CERT_DIR, c["slug"] + ".jpg")
        thumb = os.path.join(CERT_DIR, c["slug"] + "-thumb.jpg")
        scan = os.path.join(ORIG, c.get("src", "")) if c.get("src") else ""
        if Image and scan and os.path.exists(scan):
            if not (os.path.exists(thumb) and os.path.getmtime(thumb) >= os.path.getmtime(scan)):
                im = Image.open(scan).convert("RGB")
                os.makedirs(CERT_DIR, exist_ok=True)
                for w, p, q in ((1400, full, 80), (600, thumb, 78)):
                    im.resize((w, round(im.height * w / im.width)), Image.LANCZOS).save(p, "JPEG", quality=q, optimize=True, progressive=True)
        c["ok"] = os.path.exists(full) and os.path.exists(thumb)
        c["tw"], c["th"] = 600, 826
        if c["ok"] and Image:
            c["tw"], c["th"] = Image.open(thumb).size

prepare_images()
CERTS = [c for c in CERTS if c.get("ok")]
CERT_BY = {c["slug"]: c for c in CERTS}
COURSES = [c for c in CERTS if c.get("hours")]
COURSES_N = len(COURSES)
HOURS_N = sum(c["hours"] for c in COURSES)


# ---------- мелкие помощники ----------
def money(n): return f"{n:,}".replace(",", NB)

def ru_date(iso):
    y, m, d = map(int, iso.split("-"))
    return f"{d} {RU_MONTHS[m - 1]} {y}"

def icon(name):
    p = {
        "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
        "whatsapp": '<path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8z"/>'
                    '<path transform="translate(7.3 7.3) scale(.4)" vector-effect="non-scaling-stroke" d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>',
        "telegram": '<path d="M22 2 11 13M22 2l-7 20-4-9-9-4 20-7z"/>',
        "instagram": '<rect x="3.5" y="3.5" width="17" height="17" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.3" cy="6.7" r=".7" fill="currentColor"/>',
        "youtube": '<rect x="3" y="5" width="18" height="14" rx="4"/><path d="m10.5 9.5 4 2.5-4 2.5z"/>',
        "mail": '<rect x="3" y="5" width="18" height="14" rx="3"/><path d="m4 7.5 8 6 8-6"/>',
        "burst": '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M18.4 5.6l-2.8 2.8M8.4 15.6l-2.8 2.8"/>',
        "spine": '<rect x="8" y="2.5" width="8" height="3.8" rx="1.9"/><rect x="7" y="8" width="8" height="3.8" rx="1.9"/><rect x="8" y="13.5" width="8" height="3.8" rx="1.9"/><rect x="9.5" y="19" width="6" height="2.8" rx="1.4"/>',
        "figure": '<circle cx="12" cy="4.5" r="2"/><path d="M12 8.5v6.5M7.5 10.5 12 8.5l4.5 2M9.5 21.5 12 15l2.5 6.5"/>',
        "joint": '<circle cx="6.5" cy="6.5" r="2.7"/><circle cx="17.5" cy="17.5" r="2.7"/><path d="m8.6 8.6 6.8 6.8M3.5 12.5l2-2M18.5 11.5l2 2"/>',
        "wave": '<path d="M2.5 12c2-8 4 8 6 0s4 8 6 0 4 8 6 0"/>',
        "heart": '<path d="M12 20.5C6 16.6 3.5 13.3 3.5 9.8A4.3 4.3 0 0 1 12 8a4.3 4.3 0 0 1 8.5 1.8c0 3.5-2.5 6.8-8.5 10.7z"/>',
    }[name]
    return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{p}</svg>'

def more(href, text):
    return f'<a class="more" href="{href}"><span>{text}</span><i aria-hidden="true">{icon("arrow")}</i></a>'

def btn_wa(label="Записаться в WhatsApp", cls=""):
    return f'<a class="btn {cls}" href="{e(WA_URL)}" rel="noopener" target="_blank">{icon("whatsapp")}<span>{label}</span></a>'

def contact_row(wa_cls="", cls="ghost", wa_label="Записаться в WhatsApp"):
    """WhatsApp + Telegram + «Написать» (последние две — только если заданы TG_URL / FORM_KEY)"""
    out = btn_wa(wa_label, wa_cls)
    if TG_URL:
        out += f'<a class="btn {cls}" href="{e(TG_URL)}" rel="noopener" target="_blank">{icon("telegram")}<span>Telegram</span></a>'
    if FORM_KEY:
        out += f'<a class="btn {cls}" href="/contacts/#napisat">{icon("mail")}<span>Написать</span></a>'
    return out

def contact_box(title="Запись и удобное время"):
    return f'<div class="contact-box"><p>{title}</p><div class="actions">{contact_row("sm", "ghost sm", "WhatsApp")}</div></div>'

def sec(inner, cls="", id=""):
    i = f' id="{id}"' if id else ""
    return f'<section class="sec {cls}"{i}><div class="wrap">{inner}</div></section>'

def sec_head(title, lede="", tag="h2", lede_html=""):
    p = lede_html or (f"<p>{lede}</p>" if lede else "")
    return f'<div class="sec-head"><{tag}>{title}</{tag}>{p}</div>'

def picture(cls="photo", eager=False, sizes="(min-width:52rem) 42vw, 100vw", style=True):
    srcset = ", ".join(f"/assets/img/photo-{w}.webp {w}w" for w in PHOTO_WIDTHS)
    source = f'<source type="image/webp" srcset="{srcset}" sizes="{sizes}">' if PHOTO_WIDTHS else ""
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    st = f' style="--focus:{PHOTO_FOCUS}"' if style else ""
    return (f'<picture>{source}<img class="{cls}" src="/assets/img/{PHOTO_FILE}" width="{PHOTO_W}" height="{PHOTO_H}" '
            f'{load} decoding="async" alt="{AUTHOR} — инструктор йоги и йогатерапии"{st}></picture>')

def prices_list(key, cls="prices"):
    items = "".join(f'<li><span class="num">{money(v)}</span><span class="cur">{CUR[k]}</span></li>' for k, v in PRICES[key].items())
    return f'<ul class="{cls}" aria-label="Стоимость одного занятия">{items}</ul>'

def prices_text(key):
    return " или ".join(f"{money(v)}{NB}{CUR[k]}" for k, v in PRICES[key].items())

def pill_prices(key):
    items = "".join(f'<li>{money(v)}{NB}{CUR[k]}</li>' for k, v in PRICES[key].items())
    return f'<ul class="pill-prices"><li class="cap">Одно занятие:</li>{items}</ul>'

def plan(key, title, text, link, dark=False):
    cls = "plan dark" if dark else "plan"
    lk = f'<div class="{"on-dark" if dark else ""}">{more(*link)}</div>' if link else ""
    return (f'<article class="{cls}"><div><h3>{title}</h3><p>{text}</p></div>{prices_list(key)}'
            f'<p class="per">Стоимость одного индивидуального занятия</p>{lk}</article>')

def offers(key, name):
    return [{"@type": "Offer", "name": name, "price": str(v), "priceCurrency": k,
             "availability": "https://schema.org/InStock", "url": DOMAIN + "/" + ("online/" if key == "online" else "batumi/")}
            for k, v in PRICES[key].items()]

def faq_html(qa):
    rows = "".join(f'<div class="row"><dt>{e(q)}</dt><dd>{e(a)}</dd></div>' for q, a in qa)
    return f'<dl class="faq">{rows}</dl>'

def faq_node(url, qa):
    return {"@type": "FAQPage", "@id": url + "#faq", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]}

def crumbs(items):
    lis = "".join(f'<li><a href="{u}">{e(n)}</a></li>' for u, n in items[:-1]) + f'<li aria-current="page">{e(items[-1][1])}</li>'
    node = {"@type": "BreadcrumbList", "@id": abs_url(items[-1][0]) + "#breadcrumb", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": abs_url(u)} for i, (u, n) in enumerate(items)]}
    return f'<nav class="crumbs" aria-label="Навигация"><ol>{lis}</ol></nav>', node

def cta_band(title="Расскажите, что вас беспокоит, и подберём формат занятий",
             text="Напишите в WhatsApp или Telegram: отвечу и предложу, с чего начать. Можно онлайн из любой точки мира или очно в Батуми."):
    return sec(f'<div class="cta"><h2>{title}</h2><div><p>{text}</p><div class="actions">{contact_row("light", "ghost-dark", "Написать в WhatsApp")}</div></div></div>', "tight")

def cert_fan(n=3):
    imgs = "".join(f'<img src="/assets/img/certificates/{c["slug"]}-thumb.jpg" width="{c["tw"]}" height="{c["th"]}" loading="lazy" '
                   f'decoding="async" alt="Сертификат «{e(c["title"])}»">' for c in CERTS[:n])
    return f'<div class="fan">{imgs}</div>'


# ---------- направления ----------
DIRS = [
 {"path": "/bol-v-spine/", "name": "Боли в спине", "icon": "spine",
  "tile": "Поясница, шея и грудной отдел: мягкая практика без «через боль».",
  "title": "Йога при болях в спине: занятия онлайн и в Батуми | Yogavam",
  "desc": "Йогатерапия при болях в пояснице, шее и грудном отделе. Индивидуальные занятия Натальи Умновой онлайн и в Батуми, программа под ваше тело.",
  "h1": "Йогатерапия при болях в спине",
  "lead": "Боль в спине часто связана с привычками движения: долгим сидением, напряжением в шее и плечах, зажатым тазом и поверхностным дыханием. На индивидуальных занятиях я смотрю, как вы двигаетесь, и подбираю мягкую практику для поясницы, шеи и грудного отдела. Это обучение движению, а не лечение.",
  "when_title": "Когда обращаются",
  "when": ["тянущая боль в пояснице после рабочего дня", "напряжение в шее и между лопатками", "скованность по утрам",
           "ощущение «забитой» спины после сидячей работы или тренировок", "осторожность в движении после периода боли (после согласования с врачом)"],
  "how": "Начинаем с вашего запроса и коротких двигательных тестов: смотрю, как работают спина, таз, плечи и дыхание. Затем программа из йогатерапии, миофасциальных и соматических упражнений и элементов метода Фельденкрайза. Движения мягкие, в комфортном диапазоне, без «через боль». В конце занятия вы получаете простую практику для самостоятельных занятий.",
  "exp": ["lumbar-2022", "neck-2023", "pelvis-si-2023", "posture-thoracic-2022"],
  "note": "При острой боли, онемении рук или ног, травме и после операции сначала обратитесь к врачу. Занятия не заменяют лечение.",
  "faq": [
   ("Можно ли заниматься йогой, если болит спина?", "Часто да, но формат зависит от причины боли. При острой боли, онемении или после травмы сначала нужна консультация врача. Если врач не против движения, я подберу мягкую практику без нагрузки на болезненную зону."),
   ("Чем йогатерапия отличается от обычной йоги?", "В группе программа одна на всех. В йогатерапии практика подбирается под ваше тело и запрос: мы выбираем движения, которые вам подходят, и исключаем те, что сейчас неуместны."),
   ("Сколько занятий нужно?", "Зависит от запроса и регулярности. После первого занятия обычно понятно, с чем мы работаем и как часто встречаться. Обещать срок результата нельзя."),
   ("Подходят ли онлайн-занятия при болях в спине?", "Да. Я вижу вас по видеосвязи целиком, корректирую технику по ходу занятия и даю рекомендации. Подробнее на странице «Онлайн»."),
  ]},
 {"path": "/osanka/", "name": "Осанка", "icon": "figure",
  "tile": "Сутулость, напряжение в шее и плечах, сидячая работа.",
  "title": "Йога для осанки: занятия онлайн и в Батуми | Yogavam",
  "desc": "Работа с осанкой взрослых: сутулость, напряжение в шее и плечах, сидячая работа. Индивидуальные занятия йогатерапией онлайн и в Батуми.",
  "h1": "Йога для осанки: как работать с нарушением осанки взрослому",
  "lead": "Осанка — это не «держать спину прямо», а привычка стоять, сидеть и дышать, и она меняется вместе с движением: подвижностью грудного отдела, работой плеч, таза и стоп. На индивидуальных занятиях я помогаю заметить ваши привычки и мягко находить более лёгкое положение тела.",
  "when_title": "Когда обращаются",
  "when": ["сутулость и «круглая» спина после работы за компьютером", "напряжение в шее и плечах", "ощущение, что одно плечо выше другого",
           "усталость спины к вечеру", "желание «выпрямиться» без постоянного усилия"],
  "how": "Смотрю, как вы стоите, сидите и ходите, как двигается грудной отдел и дышат рёбра. Затем практика: подвижность грудного отдела, работа плеч и таза, стопы как опора, дыхание. Без жёсткого «держать спину», с вниманием к ощущениям. Для сидячей работы даю простые упражнения, которые можно делать на рабочем месте.",
  "exp": ["posture-thoracic-2022", "shoulder-arm-2023", "neck-2023", "feet-2024"],
  "note": "Сколиоз и другие диагнозы обсуждайте с врачом. Я работаю в согласованных рамках и не обещаю изменить структуру костей.",
  "faq": [
   ("Можно ли исправить осанку во взрослом возрасте?", "Осанка зависит от привычек, мышечного тонуса и подвижности, и работать над тем, как вы двигаетесь, можно в любом возрасте. Врождённые особенности и диагнозы требуют обсуждения с врачом."),
   ("Достаточно ли занятия раз в неделю?", "Короткая практика несколько раз в неделю обычно полезнее одного длинного занятия. На сессии мы выбираем простую практику, которую реально встроить в день."),
   ("Чем это отличается от корсета и фитнеса?", "Корсет поддерживает тело снаружи, а здесь мы учим тело двигаться и держаться самому. Фитнес даёт нагрузку, здесь акцент на внимании, подвижности и лёгкости."),
   ("Поможет ли йога при сидячей работе?", "При сидячей работе чаще всего зажимаются шея, плечи, грудной отдел и таз. Мы возвращаем им подвижность и учим чаще менять положение тела."),
  ]},
 {"path": "/sustavy/", "name": "Суставы", "icon": "joint",
  "tile": "Подвижность тазобедренных суставов, плеча, запястья, шеи и стоп.",
  "title": "Йогатерапия для суставов: занятия онлайн и в Батуми | Yogavam",
  "desc": "Подвижность суставов: тазобедренные, плечо, запястье, стопы. Индивидуальные занятия йогатерапией онлайн и в Батуми, мягкая практика без боли.",
  "h1": "Йогатерапия для суставов: подвижность и лёгкость движения",
  "lead": "Скованность в суставах часто связана с привычками и однообразным движением. Я работаю с тазобедренными суставами, плечом, запястьем и локтем, шеей и стопами: помогаю вернуть подвижность и найти движения без лишнего напряжения. Занятия не заменяют лечение суставов и консультацию врача.",
  "when_title": "Когда обращаются",
  "when": ["скованность в тазобедренных суставах и «зажатый» таз", "напряжение в плече и шее", "дискомфорт в запястье и локте при работе за компьютером",
           "усталые стопы", "скованность суставов по утрам"],
  "how": "Начинаю с вашего запроса и наблюдения за движением. Затем мягкая практика: соматические упражнения, йогатерапия, дыхание и приёмы метода Фельденкрайза, которые помогают найти новый способ двигаться. Работаем в вашем диапазоне, без растяжки через боль.",
  "exp": ["tbs-2024", "shoulder-arm-2023", "feet-2024", "pelvis-si-2023", "neck-2023"],
  "note": "Острая боль, отёк, воспаление, травма, эндопротез: сначала врач. Практику согласуем с его рекомендациями.",
  "faq": [
   ("Можно ли заниматься при артрозе?", "Это вопрос к лечащему врачу: при многих диагнозах движение полезно, но тип и объём нагрузки нужно согласовать. С разрешения врача я подберу щадящую практику без боли и перегрузки."),
   ("Чем это отличается от ЛФК и растяжки?", "ЛФК назначает врач по диагнозу, растяжка тянет мышцы. Здесь внимание на способе движения: как участвует сустав, как включается всё тело, как вы дышите. Это дополняет ЛФК, но не заменяет её."),
   ("Нужна ли гибкость?", "Нет. Мы работаем в вашем диапазоне движения."),
   ("Можно ли заниматься онлайн?", "Да, я вижу вас по видеосвязи целиком и корректирую движения по ходу занятия."),
  ]},
 {"path": "/zhenskoe-zdorovie/", "name": "Женское здоровье", "icon": "heart",
  "tile": "Тазовое дно, подготовка к родам и восстановление после них.",
  "title": "Йога для женского здоровья: тазовое дно, роды | Yogavam",
  "desc": "Тазовое дно, подготовка к родам и восстановление после родов. Индивидуальные занятия йогатерапией для женщин онлайн и в Батуми.",
  "h1": "Женское здоровье: тазовое дно, подготовка к родам и восстановление после них",
  "lead": "Телу женщины в разные периоды жизни нужна разная поддержка. Я помогаю в работе с тазовым дном, подготовке тела к родам и восстановлении после них, а также при напряжении в тазе и пояснице. Работа мягкая, в вашем темпе и не заменяет наблюдение у врача.",
  "when_title": "Для кого",
  "when": ["подготовка к родам (беременность после одобрения ведущего врача)", "восстановление после родов", "ощущение слабости или напряжения в области таза",
           "боль в пояснице и тазу после беременности", "желание лучше чувствовать тело и управлять им"],
  "how": "Начинаем с разговора о вашем запросе и самочувствии. Работа с тазовым дном — это не только упражнения Кегеля: мы учимся чувствовать мышцы, расслаблять и включать их, связываем дыхание, таз, спину и стопы. Практику подбираю под срок беременности и самочувствие; после родов начинаем только с разрешения врача.",
  "exp": ["pelvic-floor-2024", "pelvis-si-2023", "tbs-2024", "breathing-2024"],
  "note": "При беременности и после родов все занятия согласуйте с ведущим врачом. Боль, кровотечение, недержание: сначала к врачу.",
  "faq": [
   ("Когда можно начинать занятия после родов?", "Сроки определяет врач после осмотра, разрешение нужно получить до начала занятий. После этого мы начинаем с мягкой практики, дыхания и работы с тазовым дном."),
   ("Можно ли заниматься во время беременности?", "Обычно да, если у ведущего врача нет противопоказаний. Я учитываю срок и самочувствие и не даю нагрузок, которые вам не подходят."),
   ("Нужны ли упражнения Кегеля?", "Не всегда: иногда мышцам тазового дна нужно не усиление, а расслабление. Сначала разбираемся, что происходит, а не выполняем упражнения «на всякий случай». Диагноз ставит врач."),
   ("Подходят ли онлайн-занятия?", "Да, онлайн и очно в Батуми."),
  ]},
 {"path": "/stress-i-dyhanie/", "name": "Стресс и дыхание", "icon": "wave",
  "tile": "Мягкое движение и дыхание, чтобы замедлиться и отпустить напряжение.",
  "title": "Йога от стресса и тревоги: движение и дыхание | Yogavam",
  "desc": "Восстановление через мягкое движение и дыхательные практики при стрессе и напряжении. Индивидуальные занятия онлайн и в Батуми.",
  "h1": "Йога от стресса: восстановление через движение и дыхание",
  "lead": "Стресс живёт в теле: в зажатой шее, поверхностном дыхании, напряжении в животе и челюсти. Мягкое движение и дыхательные практики помогают нервной системе успокоиться и вернуть ощущение опоры. Занятия не заменяют помощь врача или психолога.",
  "when_title": "Когда обращаются",
  "when": ["постоянное напряжение в шее и плечах", "поверхностное дыхание", "трудно расслабиться и уснуть",
           "усталость, ощущение, что «не отпускает»", "хочется практики без соревнования и перегрузки"],
  "how": "Начинаем с дыхания и ощущений тела. Затем практики на расслабление, мягкое движение лёжа и сидя, дыхательные техники. Метод Фельденкрайза и соматика помогают замечать напряжение и отпускать его. Темп спокойный, без «выжать из себя».",
  "exp": ["breathing-2024", "neck-2023", "posture-thoracic-2022"],
  "note": "При тревожных расстройствах, паниках и депрессии нужна помощь специалиста; занятия могут быть дополнением, не заменой.",
  "faq": [
   ("Помогает ли йога при тревоге?", "Спокойное движение и дыхание помогают многим расслабиться и лучше чувствовать тело, но это не лечение тревожных расстройств. При сильной или длительной тревоге обратитесь к врачу или психологу, занятия можно использовать как дополнение."),
   ("Какие дыхательные практики подойдут новичку?", "Начинаем с простого: замечаем дыхание, удлиняем выдох, расслабляем рёбра и живот. Сложные техники с задержками дыхания не используем, пока вы не освоитесь, и учитываем состояние здоровья."),
   ("Нужно ли уметь медитировать?", "Нет. Практика телесная: внимание на движении и дыхании."),
   ("Как быстро появится эффект?", "Ощущения индивидуальны. Обещать результат за определённое время нельзя, но уже на первом занятии становится понятно, что вам подходит."),
  ]},
]
DIR_BY = {d["path"]: d for d in DIRS}

def chips(current=None):
    """плашки-ссылки на направления (current исключается)"""
    return '<ul class="chips">' + "".join(
        f'<li><a href="{d["path"]}"><span class="ic">{icon(d["icon"])}</span>{d["name"]}</a></li>' for d in DIRS if d["path"] != current) + "</ul>"

def bento():
    cls = ["t-a", "t-b", "t-c", "t-d", "t-e"]
    tiles = "".join(
        f'<article class="tile {c}"><span class="ic">{icon(d["icon"])}</span><div><h3>{d["name"]}</h3><p>{d["tile"]}</p>'
        f'<div class="{"on-dark" if c == "t-e" else ""} tile-more">{more(d["path"], "Подробнее")}</div></div></article>'
        for c, d in zip(cls, DIRS))
    return f'<div class="bento">{tiles}</div>'

LEVEL_P1 = ("Занимаемся <strong>от простого к сложному</strong>. Если вы никогда не пробовали йогу или йогатерапию и думаете, "
            "что у вас не получится, — получится. Начнём с дыхания и простых движений и пойдём в вашем темпе, без перегрузок и без боли.")
LEVEL_P2 = "Если практика у вас уже есть, углубим её: поработаем над техникой, контролем движения и тонким чувствованием тела."


def price_card(link=("#stoimost", "Стоимость и форматы")):
    return (f'<aside class="hero-card" aria-label="Стоимость занятий"><p class="hc-cap">Стоимость: 1 занятие, 1 час</p>'
            f'<div class="hc-row"><p>Онлайн</p>{prices_list("online")}</div>'
            f'<div class="hc-row"><p>Очно в Батуми</p>{prices_list("batumi")}</div>'
            f'<div class="hc-more">{more(*link)}</div></aside>')


# ---------- страница ----------
pages = []
LASTMOD_FILE = os.path.join(ROOT, "tools", ".lastmod.json")
try:
    LASTMOD = json.load(open(LASTMOD_FILE))
except Exception:
    LASTMOD = {}

PERSON = {
    "@type": "Person", "@id": person_id, "name": AUTHOR, "givenName": "Наталья", "familyName": "Умнова",
    "jobTitle": "Инструктор йоги и йогатерапии",
    "description": "Инструктор йоги и йогатерапии, специалист по движению. Более 10 лет преподаёт йогу и йогатерапию, ведёт индивидуальные занятия онлайн и в Батуми: боли в спине, осанка, суставы, женское здоровье, стресс и дыхание.",
    "url": abs_url("/about/"),
    "knowsAbout": ["йогатерапия", "метод Фельденкрайза", "миофасциальные упражнения", "соматические практики",
                   "работа с нервной системой", "йога для беременных", "восстановление после родов", "биомеханика движения", "осанка",
                   "боли в спине", "суставы", "женское здоровье", "тазовое дно", "дыхательные практики"],
    "knowsLanguage": "ru", "workLocation": {"@type": "City", "name": "Батуми"}, "sameAs": [u for u in (YT_URL, TG_URL, IG_URL) if u],
}
if PHOTO_W:
    PERSON["image"] = {"@type": "ImageObject", "url": abs_url(f"/assets/img/{PHOTO_FILE}"), "width": PHOTO_W, "height": PHOTO_H}
if CERTS:
    PERSON["hasCredential"] = [{
        "@type": "EducationalOccupationalCredential", "name": c["title"], "credentialCategory": "certificate",
        "recognizedBy": {"@type": "Organization", "name": c["org"]}, "dateCreated": c["issued"],
        "description": c["desc"], "image": abs_url(f"/assets/img/certificates/{c['slug']}.jpg")} for c in CERTS]
WEBSITE = {"@type": "WebSite", "@id": website_id, "name": BRAND, "alternateName": "Йогатерапия с Натальей Умновой",
           "url": DOMAIN + "/", "inLanguage": "ru", "publisher": {"@id": person_id}}

NAV = [("/about/", "Обо мне"), ("/online/", "Онлайн"), ("/batumi/", "Батуми"), ("/certificates/", "Сертификаты"),
       ("/blog/", "Статьи"), ("/contacts/", "Контакты")]
CSS_V = hashlib.md5(open(os.path.join(ROOT, "assets", "style.css"), "rb").read()).hexdigest()[:8]

def header(path):
    def links():
        return "".join(f'<li><a href="{u}"{" aria-current=page" if (path == u or (u != "/" and path.startswith(u))) else ""}>{n}</a></li>' for u, n in NAV)
    return (f'<header class="top"><div class="bar"><a class="brand" href="/" aria-label="{BRAND} — на главную">{BRAND}</a>'
            f'<nav class="menu" aria-label="Основное меню"><ul>{links()}</ul></nav>'
            f'{btn_wa("WhatsApp", "sm")}'
            f'<details class="burger"><summary>Меню</summary><nav aria-label="Меню"><ul>{links()}</ul></nav></details></div></header>')

def footer():
    nav = "".join(f'<li><a href="{u}">{n}</a></li>' for u, n in NAV)
    dirs = "".join(f'<li><a href="{d["path"]}">{d["name"]}</a></li>' for d in DIRS)
    contacts = f'<li><a href="{e(WA_URL)}" rel="noopener" target="_blank">WhatsApp</a></li>'
    if TG_URL: contacts += f'<li><a href="{e(TG_URL)}" rel="noopener" target="_blank">Telegram</a></li>'
    if FORM_KEY: contacts += '<li><a href="/contacts/#napisat">Написать</a></li>'
    soc = ""
    for url, label, ic in ((YT_URL, "YouTube", "youtube"), (IG_URL, "Instagram", "instagram")):
        if url: soc += f'<li><a href="{e(url)}" rel="noopener" target="_blank" aria-label="{label}">{icon(ic)}</a></li>'
    soc = f'<ul class="social">{soc}</ul>' if soc else ""
    return f'''<footer class="foot"><div class="wrap">
<div class="foot-grid">
<div><a class="brand" href="/">{BRAND}</a><p>{AUTHOR}. Йогатерапия для спины, осанки и здорового движения: индивидуальные занятия онлайн и в Батуми.</p></div>
<nav aria-label="Разделы сайта"><h2>Разделы</h2><ul>{nav}</ul></nav>
<nav aria-label="Направления"><h2>Направления</h2><ul>{dirs}</ul></nav>
<div><h2>Связаться</h2><ul>{contacts}</ul></div>
</div>
<div class="foot-fine"><div><p>Материалы сайта носят информационный характер и не заменяют консультацию врача. Занятия не являются медицинской услугой. При острой боли, травмах и заболеваниях сначала обратитесь к врачу.</p><p>© {TODAY[:4]} {BRAND}</p></div>{soc}</div>
</div></footer>'''

def page(path, title, desc, body, graph=(), page_type="WebPage", indexable=True, images=(), og_type="website", extra_page=None):
    url = abs_url(path)
    webpage = {"@type": page_type, "@id": url + "#webpage", "url": url, "name": title, "description": desc, "inLanguage": "ru",
               "isPartOf": {"@id": website_id}, "primaryImageOfPage": {"@type": "ImageObject", "url": abs_url(OG_IMAGE)}}
    for n in graph:
        if n.get("@type") == "BreadcrumbList": webpage["breadcrumb"] = {"@id": n["@id"]}
    if extra_page: webpage.update(extra_page)
    ld = ""
    if indexable:
        ld = '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": [WEBSITE, PERSON, webpage] + list(graph)}, ensure_ascii=False) + "</script>"
    robots = "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1" if indexable else "noindex, follow"
    verify = ""
    if GOOGLE_VERIFY: verify += f'<meta name="google-site-verification" content="{GOOGLE_VERIFY}">\n'
    if YANDEX_VERIFY: verify += f'<meta name="yandex-verification" content="{YANDEX_VERIFY}">\n'
    og = abs_url(OG_IMAGE)
    canon = f'<link rel="canonical" href="{url}">' if indexable else ""
    doc = f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="robots" content="{robots}">
{canon}
<meta name="author" content="{AUTHOR}">
<meta name="theme-color" content="#f1f4f2">
{verify}<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon-48.png" sizes="48x48" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preload" href="/assets/fonts/geologica-cyrillic.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/geologica-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/style.css?v={CSS_V}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:locale" content="ru_RU">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{og}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{AUTHOR} — йогатерапия для спины, осанки и здорового движения онлайн и в Батуми">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{og}">
{ld}
</head>
<body>
<a class="skip" href="#main">К содержанию</a>
{header(path)}
<main id="main">
{body}
</main>
{footer()}
</body>
</html>
'''
    target = os.path.join(OUT, "404.html") if path == "/404.html" else os.path.join(OUT, path.strip("/"), "index.html")
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8") as f: f.write(doc)
    if indexable:
        h = hashlib.md5(doc.replace(CSS_V, "").encode()).hexdigest()
        old = LASTMOD.get(url)
        if not old or old["hash"] != h: LASTMOD[url] = {"hash": h, "date": TODAY}
        pages.append((url, LASTMOD[url]["date"], list(images)))

PHOTO_IMG = [f"/assets/img/{PHOTO_FILE}"] if PHOTO_W else []
CERT_IMGS = [f"/assets/img/certificates/{c['slug']}.jpg" for c in CERTS]


# ===================== ГЛАВНАЯ =====================
HOME_FAQ = [
    ("Что такое йогатерапия?",
     "Йогатерапия — направление йоги, в котором упражнения подбирают под состояние и задачи конкретного человека: снять мышечное напряжение, вернуть подвижность суставам и позвоночнику, улучшить осанку и дыхание. Это не медицинское лечение, а мягкая двигательная практика, которая дополняет рекомендации врача."),
    ("Подойдут ли занятия, если я никогда не занимался йогой?",
     "Да. Занятия идут от простого к сложному и подходят для любого уровня подготовки. Начинаем с дыхания и базовых движений, темп и нагрузку подбираем под вас."),
    ("Сколько стоят занятия?",
     f"Индивидуальное онлайн-занятие стоит {prices_text('online')}. Очное занятие в Батуми — {prices_text('batumi')}."),
    ("Как проходят онлайн-занятия?",
     "Индивидуально, по видеосвязи. Наталья видит вас целиком, корректирует технику по ходу занятия и выстраивает практику под ваши цели. Нужны камера, стабильный интернет, коврик и немного свободного места."),
    ("Можно ли заниматься во время беременности?",
     "Да, если нет противопоказаний и ваш врач не возражает. Упражнения подбираются с учётом срока и самочувствия. После родов занятия помогают мягко восстановиться."),
    ("Где проходят очные занятия?",
     "В Батуми, индивидуально. Постоянной студии нет, поэтому место и время согласуем под вас. Если вы в другом городе или стране, подойдут онлайн-занятия."),
]

TRACE = '''<svg class="trace" viewBox="0 0 1200 730" preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false">
<path class="l1" pathLength="1" d="M600 740C720 430 790 700 910 470S1070 170 1230 250"/>
<path class="l2" pathLength="1" d="M660 760C780 470 850 720 970 520S1110 230 1240 300"/>
<circle cx="910" cy="470" r="5"/></svg>'''

creds = ""
if CERTS:
    pills = "".join(f"<li>{e(c['short'])}</li>" for c in CERTS)
    creds = (f'<div class="creds"><div class="creds-l">{cert_fan()}<p>Мастер и преподаватель Open Yoga, {COURSES_N} курсов по йогатерапии и биомеханике. Обучение с 2014 года.</p></div>'
             f'{more("/certificates/", "Все сертификаты")}</div>')

home_hero = f'''<section class="hero">{TRACE}<div class="wrap hero-in">
<h1>Йогатерапия для спины, осанки и здорового движения<span class="sub">индивидуальные занятия онлайн и в Батуми</span></h1>
<div class="hero-l"><p class="lead">Мягкая практика, которая помогает снять напряжение и вернуть телу подвижность. Программу подбираю под ваше тело, ваши задачи и ваш уровень подготовки.</p>
<div class="actions">{contact_row()}</div></div>
{price_card()}
</div></section>'''
home_dirs = sec('<p class="strip-t">Направления занятий</p>' + chips(), "tight strip")

home_me = sec(f'''<div class="me"><div class="me-photo">{picture(eager=True)}</div>
<div class="me-body"><h2>Обо мне</h2>
<p class="lead-sm"><strong>{AUTHOR}.</strong> Инструктор йоги и йогатерапии, специалист по движению. Более 10 лет преподаю йогу и йогатерапию, работаю со спиной, осанкой, суставами, женским здоровьем и стрессом.</p>
<p>Я не учу «правильно стоять в асанах». Я учу тело двигаться иначе: свободнее, экономнее, функциональнее, чтобы этот навык работал в обычной жизни — за рабочим столом, с ребёнком на руках, на прогулке.</p>
<p>Объединяю йогатерапию, метод Фельденкрайза, миофасциальные упражнения, соматику и работу с нервной системой. Опираюсь на современные данные анатомии и биомеханики. Помогаю будущим мамам подготовить тело к родам и мягко восстановиться после них.</p>
<p>{more("/about/", "Подробнее обо мне")}</p>
{creds}</div></div>''', "tight", "obo-mne")

home_audience = sec(sec_head("Кому подойдут занятия", "Выберите направление, которое ближе вам: программу подберём под вас.") + bento())

home_level = sec(f'''<div class="level"><div><h2>Для любого уровня, даже если вы никогда не занимались</h2><p>{LEVEL_P1}</p><p>{LEVEL_P2}</p></div>
<ol class="track"><li><b>Дыхание и простые движения</b><span>С чего начинаем, если вы новичок</span></li>
<li><b>Техника и контроль движения</b><span>Учимся двигаться точнее и свободнее</span></li>
<li><b>Тонкое чувствование тела</b><span>Практика становится осознанной и глубокой</span></li></ol></div>''', "tight")

home_steps = sec(sec_head("Как проходят занятия", "Персональная работа: от знакомства с вашим телом до заметного результата.") +
    '''<ol class="steps">
<li class="step"><b>1</b><h3>Знакомство и тесты</h3><p>Обсуждаем ваш запрос. Если нужно, проводим двигательные тесты: оцениваем мышцы, суставы и дыхание.</p></li>
<li class="step"><b>2</b><h3>Практика под ваши цели</h3><p>По результатам выстраиваю индивидуальную программу. Начинаем с базы: дыхание, замедление, внимание к ощущениям.</p></li>
<li class="step"><b>3</b><h3>Заметный прогресс</h3><p>Через некоторое время повторяем тесты, и вы сами видите, что изменилось.</p></li></ol>''' +
    f'<div class="after">{more("/online/", "Подробнее о занятиях и подготовке")}</div>')

home_plans = sec(sec_head("Форматы и стоимость", lede_html="<div><p>Стоимость одного занятия, 1 час.</p>" + contact_box() + "</div>") +
    '<div class="plans">' +
    plan("online", "Онлайн", "Индивидуально по видеосвязи из любой точки мира. Вижу вас целиком и корректирую технику по ходу занятия.", ("/online/", "Как проходят онлайн-занятия")) +
    plan("batumi", "Очно в Батуми", "Работаем один на один. Место и время подбираем под ваш график.", ("/batumi/", "Занятия в Батуми"), dark=True) +
    "</div>", "tight", "stoimost")

home_faq = sec(sec_head("Частые вопросы") + faq_html(HOME_FAQ))

page("/", f"Йогатерапия для спины, осанки и суставов онлайн и в Батуми — {AUTHOR} | {BRAND}",
     f"Индивидуальные занятия йогатерапией: боли в спине, осанка, суставы, женское здоровье, стресс и дыхание. Онлайн — {prices_text('online')}, очно в Батуми — {prices_text('batumi')}. Для новичков и опытных.",
     home_hero + home_dirs + home_me + home_audience + home_level + home_steps + home_plans + home_faq + cta_band(),
     graph=[faq_node(DOMAIN + "/", HOME_FAQ)], images=PHOTO_IMG + CERT_IMGS[:3], extra_page={"about": {"@id": person_id}})


# ===================== ОБО МНЕ =====================
cr, cr_ld = crumbs([("/", "Главная"), ("/about/", "Обо мне")])
EDU_GROUPS = [("Спина и осанка", ["lumbar-2022", "neck-2023", "posture-thoracic-2022"]),
              ("Суставы", ["tbs-2024", "shoulder-arm-2023", "feet-2024"]),
              ("Таз и женское здоровье", ["pelvis-si-2023", "pelvic-floor-2024"]),
              ("Дыхание и стресс", ["breathing-2024"])]
def _edu_row(name, slugs):
    cs = [CERT_BY[x] for x in slugs if x in CERT_BY]
    if not cs: return ""
    return f'<li><b>{name}</b><span>' + ", ".join(f'<a href="/certificates/#{c["slug"]}">{e(c["title"])}</a> ({c["hours"]} ч)' for c in cs) + "</span></li>"
edu_list = '<ul class="methods">' + "".join(_edu_row(n, sl) for n, sl in EDU_GROUPS) + "</ul>"
cert_block = ""
if CERTS:
    cert_block = (f'<div class="creds" style="margin-top:2rem">'
                  f'<div class="creds-l">{cert_fan()}<p>Мастер и преподаватель Open Yoga, {COURSES_N} курсов по йогатерапии и биомеханике. Обучение с 2014 года.</p></div>{more("/certificates/", "Все сертификаты")}</div>')
about_body = f'''<div class="wrap page-head" style="padding-bottom:0">{cr}</div>
{sec(f"""<div class="about-grid"><div class="about-photo">{picture(eager=True)}</div>
<div class="prose"><h1>{AUTHOR}</h1>
<p class="lead">Инструктор йоги и йогатерапии, специалист по движению и методу Фельденкрайза. Более 10 лет помогаю людям освободиться от скованности и напряжения, вернуть телу подвижность, а себе — радость жизни.</p>
<div class="actions">{btn_wa()}<a class="btn ghost" href="/online/">Как проходят занятия</a></div>
<h2>Мой подход</h2>
<p>Я выхожу за рамки классических асан. На занятиях соединяю методы йогатерапии, которые развивают телесный интеллект и двигательный контроль, с современным научным взглядом на анатомию, биомеханику и физическую реабилитацию.</p>
<p>Мы не просто выполняем упражнения, а учим тело двигаться иначе: функциональнее и экономнее. Этот навык вы переносите в повседневную жизнь, и самочувствие меняется не только на коврике.</p>
<p>Сложные взаимосвязи в теле объясняю простым языком. Когда понимаешь, откуда берётся дискомфорт и что с ним делать, практика становится осознанной и глубокой.</p>
<h2>Методы, с которыми я работаю</h2>
<ul class="methods">
<li><b>Йогатерапия</b><span>Упражнения, подобранные под ваше состояние и задачи.</span></li>
<li><b>Метод Фельденкрайза</b><span>Обучение лёгкому и осознанному движению. <a href="/blog/metod-feldenkraisa/">Что это за метод</a>.</span></li>
<li><b>Миофасциальные упражнения</b><span>Работа с напряжением в мышцах и фасциях.</span></li>
<li><b>Соматические практики</b><span>Замедление, тонкое чувствование тела, отпускание зажимов.</span></li>
<li><b>Работа с нервной системой и дыханием</b><span>Чтобы снизить уровень стресса и тревоги.</span></li></ul>
<h2>Беременность и восстановление после родов</h2>
<p>Помогаю будущим мамам подготовить тело к родам мягко и безопасно, с учётом срока и самочувствия. После родов помогаю бережно восстановить силу, подвижность и контакт со своим телом.</p>
<p class="fine">Занятия во время беременности — при отсутствии противопоказаний и после согласования с вашим врачом.</p>
<h2>Направления работы</h2>
{chips()}
<p>{LEVEL_P1}</p><p>{LEVEL_P2}</p>
<h2 id="obuchenie">Обучение и сертификаты</h2>
<p>Прошла обучение в Международном фонде Open Yoga ({ORG}): курс инструкторов (2014–2017, 447 часов теории и 369 часов практики), затем квалификации «Преподаватель Open Yoga» (2018) и «Мастер Open Yoga» (2021).</p>
<p>С 2022 по 2024 год прошла цикл курсов «Йогатерапия и биомеханика» в {ORG2}: {COURSES_N} курсов, всего {HOURS_N} учебных часов. По направлениям работы:</p>
{edu_list}
<p>Я в непрерывном обучении и регулярно повышаю квалификацию: изучаю новые методы работы с телом и проверяю их на практике. Поэтому со мной остаются надолго, даже достигнув результата: нам всегда есть что исследовать.</p>
{cert_block}
</div></div>""")}
{cta_band("Приходите на занятие", "Напишите в WhatsApp, расскажите о своём запросе, и мы подберём формат: онлайн или очно в Батуми.")}'''
page("/about/", f"{AUTHOR} — инструктор йоги и йогатерапии, метод Фельденкрайза",
     "Наталья Умнова: более 10 лет преподаёт йогу и йогатерапию. Метод Фельденкрайза, миофасциальные техники, соматика, йога для беременных и восстановление после родов.",
     about_body, graph=[cr_ld], page_type="ProfilePage", images=PHOTO_IMG + CERT_IMGS, extra_page={"mainEntity": {"@id": person_id}})


# ===================== СЕРТИФИКАТЫ =====================
cr, cr_ld = crumbs([("/", "Главная"), ("/certificates/", "Сертификаты")])
groups = []
for c in CERTS:
    if c["group"] not in groups: groups.append(c["group"])
def cert_card(c):
    return (f'<article class="cert" id="{c["slug"]}"><a class="img" href="/assets/img/certificates/{c["slug"]}.jpg" target="_blank" rel="noopener" '
            f'aria-label="Открыть сертификат «{e(c["title"])}» в полном размере">'
            f'<img src="/assets/img/certificates/{c["slug"]}-thumb.jpg" width="{c["tw"]}" height="{c["th"]}" loading="lazy" decoding="async" '
            f'alt="Сертификат «{e(c["title"])}», {e(c["org"])}, {c["issued"][:4]}"></a>'
            f'<div class="tx"><h3>{e(c["title"])}</h3><p class="org">{e(c["org"])}</p><p class="d">{e(c["desc"])}</p>'
            f'<p class="when">{("Объём: " + str(c["hours"]) + " ч. ") if c.get("hours") else "Обучение: " + c["period"] + ". "}Выдан <time datetime="{c["issued"]}">{ru_date(c["issued"])}</time></p></div></article>')
cert_groups = "".join(f'<section class="group"><h2>{e(g)}</h2><div class="certs">{"".join(cert_card(c) for c in CERTS if c["group"] == g)}</div></section>' for g in groups)
cert_body = f'''<div class="wrap page-head wide">{cr}<h1>Сертификаты и обучение</h1>
<p class="lead">Подтверждённое обучение {AUTHOR}: йога, йогатерапия и работа с движением, от курса инструкторов Open Yoga до цикла «Йогатерапия и биомеханика» по отделам тела. Нажмите на сертификат, чтобы открыть его в полном размере.</p></div>
{sec(cert_groups, "tight")}
{sec(f'<div class="wide-card"><h2>О моём обучении</h2><div><p>С 2014 года я учусь в Международном фонде Open Yoga ({ORG}): от курса инструкторов до квалификации мастера. С 2022 года прохожу цикл «Йогатерапия и биомеханика» в {ORG2}: {COURSES_N} курсов по отделам тела, {HOURS_N} учебных часов. На занятиях я соединяю эту базу с методом Фельденкрайза, миофасциальными и соматическими практиками и современными данными анатомии и биомеханики.</p><p>{more("/about/", "Обо мне и моём подходе")}</p></div></div>', "tight")}
{cta_band()}'''
page("/certificates/", f"Сертификаты и обучение — {AUTHOR}, йогатерапия | {BRAND}",
     f"Сертификаты {AUTHOR}: мастер и преподаватель Open Yoga, цикл «Йогатерапия и биомеханика» ({COURSES_N} курсов, {HOURS_N} часов). Обучение с 2014 года.",
     cert_body, graph=[cr_ld], page_type="CollectionPage", images=CERT_IMGS, extra_page={"about": {"@id": person_id}})


# ===================== ОНЛАЙН =====================
ONLINE_FAQ = [
    ("Что нужно для онлайн-занятия?",
     "Телефон, планшет или ноутбук с камерой, стабильный интернет, коврик и свободное место, чтобы заниматься стоя, сидя и лёжа. Одежда — удобная и облегающая, чтобы было видно положение суставов, таза и позвоночника."),
    ("Сколько стоит онлайн-занятие?", f"Индивидуальное онлайн-занятие стоит {prices_text('online')}."),
    ("Подойдут ли занятия, если я никогда не занимался йогой?",
     "Да. Занятия идут от простого к сложному: начинаем с дыхания и базовых движений, нагрузку и темп подбираем под вас. Опыт и физическая подготовка не нужны."),
    ("Как установить камеру?",
     "Так, чтобы в кадре было всё тело — от головы до стоп, а место было хорошо освещено. Во время занятия может понадобиться повернуть камеру, чтобы показать движение сбоку или спереди."),
    ("Можно ли заниматься небольшой группой?",
     "Основной формат — индивидуальные занятия. Возможность групповых онлайн-занятий уточняйте в WhatsApp."),
]
def rows(items):
    return '<div class="rows">' + "".join(f'<div class="row"><h2>{h}</h2><div class="prose">{t}</div></div>' for h, t in items) + "</div>"

cr, cr_ld = crumbs([("/", "Главная"), ("/online/", "Онлайн-занятия")])
online_service = {"@type": "Service", "@id": DOMAIN + "/online/#service",
                  "name": "Индивидуальные онлайн-занятия йогатерапией и методом Фельденкрайза",
                  "serviceType": "Персональные тренировки по йогатерапии онлайн", "provider": {"@id": person_id},
                  "areaServed": {"@type": "Place", "name": "Весь мир"}, "availableLanguage": "ru", "url": DOMAIN + "/online/",
                  "description": "Индивидуальные занятия по видеосвязи: двигательные тесты, программа под ваши цели, коррекция техники в реальном времени. Для начинающих и опытных.",
                  "offers": offers("online", "Индивидуальное онлайн-занятие")}
prep = '''<ol class="prep">
<li><b>Подключитесь за 10 минут до начала</b><span>Проверим звук, изображение и положение камеры. Мне важно хорошо видеть вас всё занятие.</span></li>
<li><b>Наденьте удобную облегающую одежду</b><span>Не слишком свободную и не сковывающую движения: мне нужно видеть положение суставов, таза и позвоночника.</span></li>
<li><b>Установите камеру так, чтобы в кадре было всё тело</b><span>От головы до стоп, при хорошем освещении. Я могу попросить повернуть камеру, чтобы посмотреть движение сбоку или спереди.</span></li>
<li><b>Подготовьте место</b><span>Расстелите коврик и освободите пространство вокруг, чтобы удобно заниматься стоя, сидя и лёжа.</span></li></ol>'''
online_body = f'''<div class="wrap page-head">{cr}<h1>Как проходят онлайн-занятия</h1>
<p class="lead">Индивидуальные тренировки по видеосвязи из любой точки мира. Я вижу вас, корректирую технику по ходу занятия и выстраиваю практику под ваши цели.</p>
{pill_prices("online")}
<div class="actions">{btn_wa()}</div></div>
{sec(rows([
 ("Начинаем с базы", "<p>Первые занятия посвящены базовым навыкам: дыханию, простым движениям, умению замедляться, наблюдать за ощущениями и переключать внимание на тело. Это фундамент, на котором строится всё остальное.</p>"),
 ("Тесты и программа под ваши цели", "<p>Если нужно, проводим двигательные тесты: оцениваем состояние мышц и суставов, дыхание. По результатам я выстраиваю практику под ваши задачи. Через некоторое время повторяем тесты, и вы своими глазами видите прогресс.</p>"),
 ("Сначала снимаем напряжение", "<p>Мой опыт работы с клиентами показывает: в основе большинства проблем в теле лежит стресс, который копится годами. Мягкие соматические практики помогают замедлиться. Уходит напряжение, тело перестаёт сопротивляться и отпускает зажимы, выравниваются перекосы — и начинаются изменения.</p>"),
 ("Практика без стресса", "<p>Для меня важно, чтобы занятия не стали для вас ещё одной обязанностью «через силу». Наша цель — регулярность, которая приносит удовольствие и устойчивый результат.</p>"),
 ("Для начинающих и опытных", f"<p>{LEVEL_P1}</p><p>{LEVEL_P2}</p>"),
 ("Почему со мной остаются надолго", "<p>Многие продолжают заниматься и после того, как достигли своей цели. Одна из причин — моё непрерывное обучение: мы вместе исследуем новые методы работы с телом, и практика не превращается в рутину.</p>"),
]), "tight")}
{sec(f'<div class="sec-head" id="podgotovka"><h2>Как подготовиться к онлайн-занятию</h2><p>Чтобы я хорошо видела вашу технику, вовремя подсказывала и давала рекомендации именно вам, подготовьтесь заранее.</p></div>{prep}<div class="prep-note"><p>Моя задача — наблюдать за вами, замечать особенности движений, корректировать технику и давать рекомендации с учётом ваших индивидуальных особенностей. Чем лучше я вас вижу, тем точнее и полезнее наша совместная работа.</p><p>Спасибо за внимательное отношение к практике. До встречи на занятии! 💚</p></div>', "tight")}
{sec(sec_head("Направления занятий", "Выберите то, что ближе вам: на каждой странице — как строится работа и ответы на вопросы.") + chips(), "tight")}
{sec(sec_head("Стоимость и запись", lede_html=contact_box()) + '<div class="plans one">' + plan("online", "Онлайн-занятие", "Индивидуально по видеосвязи, из любой точки мира.", ("/batumi/", "Живёте в Батуми? Есть очные занятия")) + "</div>", "tight", "stoimost")}
{sec(sec_head("Частые вопросы") + faq_html(ONLINE_FAQ), "tight")}
{cta_band("Найдём причину дискомфорта", "Хотите понять, откуда берутся напряжение и дискомфорт в теле и что с ними делать? Напишите в WhatsApp или Telegram: пришлю короткую анкету, и по ней спланируем первое занятие.")}'''
page("/online/", f"Онлайн-занятия йогатерапией — {prices_text('online')} | {BRAND}",
     f"Индивидуальные онлайн-занятия йогатерапией: спина, осанка, суставы, женское здоровье, стресс и дыхание. {prices_text('online')}. Как проходят занятия, как подготовиться.",
     online_body, graph=[cr_ld, online_service, faq_node(DOMAIN + "/online/", ONLINE_FAQ)], extra_page={"about": {"@id": DOMAIN + "/online/#service"}})


# ===================== БАТУМИ =====================
BATUMI_FAQ = [
    ("Где проходят занятия в Батуми?", "Работаем один на один. Постоянной студии нет, поэтому место и время согласуем под вас."),
    ("Сколько стоит очное занятие?", f"Индивидуальное занятие в Батуми стоит {prices_text('batumi')}."),
    ("Можно ли заниматься во время беременности?", "Да, если нет противопоказаний и ваш врач не возражает. Упражнения подбираются с учётом срока и самочувствия."),
]
cr, cr_ld = crumbs([("/", "Главная"), ("/batumi/", "Батуми")])
batumi_service = {"@type": "Service", "@id": DOMAIN + "/batumi/#service",
                  "name": "Индивидуальные занятия йогатерапией и методом Фельденкрайза в Батуми",
                  "serviceType": "Персональные тренировки по йогатерапии", "provider": {"@id": person_id},
                  "areaServed": {"@type": "City", "name": "Батуми", "containedInPlace": {"@type": "Country", "name": "Грузия"}},
                  "availableLanguage": "ru", "url": DOMAIN + "/batumi/", "offers": offers("batumi", "Индивидуальное занятие в Батуми")}
batumi_body = f'''<div class="wrap page-head">{cr}<h1>Индивидуальные занятия йогатерапией в Батуми</h1>
<p class="lead">Очные персональные тренировки в Батуми — для тех, кто живёт здесь постоянно или приехал на время.</p>
{pill_prices("batumi")}
<div class="actions">{btn_wa()}</div></div>
{sec(rows([
 ("Формат", "<p>Работаем один на один. Постоянной студии нет, поэтому место и время подбираем вместе, под ваш график.</p>"),
 ("Что происходит на занятии", '<p>Начинаем с вашего запроса и, если нужно, с двигательных тестов. Дальше — практика под ваши цели: йогатерапия, метод Фельденкрайза, миофасциальные и соматические упражнения, работа с дыханием. Принцип тот же, что и онлайн: <a href="/online/">как проходят занятия</a>.</p>'),
 ("Кому подойдёт", f"{chips()}<p>{LEVEL_P1}</p>"),
]), "tight")}
{sec(sec_head("Стоимость и запись", lede_html=contact_box()) + '<div class="plans one">' + plan("batumi", "Очно в Батуми", "Индивидуальное занятие один на один. Место и время подбираем под ваш график.", ("/online/", "Не в Батуми? Есть онлайн-занятия"), dark=True) + "</div>", "tight", "stoimost")}
{sec(sec_head("Частые вопросы") + faq_html(BATUMI_FAQ), "tight")}
{cta_band("Записаться на занятие в Батуми", "Расскажите, что вас беспокоит, и я предложу удобное время и место.")}'''
page("/batumi/", f"Йогатерапия в Батуми — {prices_text('batumi')} | {AUTHOR}",
     f"Индивидуальные занятия йогатерапией в Батуми: спина, осанка, суставы, женское здоровье, стресс и дыхание. {prices_text('batumi')}. Для начинающих и опытных.",
     batumi_body, graph=[cr_ld, batumi_service, faq_node(DOMAIN + "/batumi/", BATUMI_FAQ)], extra_page={"about": {"@id": DOMAIN + "/batumi/#service"}})


# ===================== НАПРАВЛЕНИЯ =====================
def dir_page(d):
    path = d["path"]; url = abs_url(path)
    cr, cr_ld = crumbs([("/", "Главная"), (path, d["name"])])
    up = lambda x: x[:1].upper() + x[1:]
    when = "<ul>" + "".join(f"<li>{e(up(x))}</li>" for x in d["when"]) + "</ul>"
    items = "".join(f'<li><a href="/certificates/#{c["slug"]}">{e(c["title"])}</a> ({c["hours"]} ч)</li>'
                    for c in (CERT_BY.get(x) for x in d["exp"]) if c)
    exp = (f'<p>Курсы цикла «Йогатерапия и биомеханика» ({ORG2}):</p><ul>{items}</ul>'
           f'<p>{more("/certificates/", "Все сертификаты")}</p>')
    others = "".join(f'<a href="{x["path"]}"><span class="ic">{icon(x["icon"])}</span><b>{x["name"]}</b><span>{x["tile"]}</span></a>'
                     for x in DIRS if x is not d)
    service = {"@type": "Service", "@id": url + "#service", "name": d["h1"], "serviceType": "Индивидуальные занятия йогатерапией",
               "provider": {"@id": person_id},
               "areaServed": [{"@type": "Place", "name": "Онлайн"},
                              {"@type": "City", "name": "Батуми", "containedInPlace": {"@type": "Country", "name": "Грузия"}}],
               "availableLanguage": "ru", "url": url, "description": d["desc"],
               "offers": offers("online", "Индивидуальное онлайн-занятие") + offers("batumi", "Индивидуальное занятие в Батуми")}
    body = f'''<div class="wrap page-head dir-head">{cr}
<div class="dir-in"><div><h1>{e(d["h1"])}</h1><p class="lead">{e(d["lead"])}</p><div class="actions">{contact_row()}</div></div>
{price_card(("/online/", "Как проходят занятия"))}</div></div>
{sec(rows([(d["when_title"], when), ("Как строится работа", f"<p>{e(d['how'])}</p>"), ("Что подтверждает опыт", exp)]), "tight")}
{sec(f'<div class="note"><h2>Важно знать</h2><p>{e(d["note"])}</p></div>', "tight")}
{sec(sec_head("Частые вопросы") + faq_html(d["faq"]), "tight")}
{sec(sec_head("Другие направления") + f'<div class="dir-more">{others}</div>', "tight")}
{cta_band()}'''
    page(path, d["title"], d["desc"] + f" Онлайн — {prices_text('online')}, в Батуми — {prices_text('batumi')}.", body,
         graph=[cr_ld, service, faq_node(url, d["faq"])], extra_page={"about": {"@id": url + "#service"}})

for _d in DIRS: dir_page(_d)


# ===================== КОНТАКТЫ =====================
cr, cr_ld = crumbs([("/", "Главная"), ("/contacts/", "Контакты")])
_cc = [(WA_URL, "WhatsApp", "whatsapp", "Запись на занятие и любые вопросы", " dark"),
       (TG_URL, "Telegram", "telegram", "Написать в мессенджер", ""),
       (IG_URL, "Instagram", "instagram", "Фото и новости", ""),
       (YT_URL, "YouTube", "youtube", "Видео с практиками и разборами", "")]
contact_cards = "".join(f'<a class="cc{k}" href="{e(u)}" rel="noopener" target="_blank"><span class="ic">{icon(i)}</span><div><h2>{n}</h2><p>{d}</p></div></a>'
                        for u, n, i, d, k in _cc if u)
contact_form = ""
if FORM_KEY:
    contact_form = sec(f'''<div class="form-wrap" id="napisat"><div><h2>Написать мне</h2><p>Расскажите о своём запросе, и я отвечу по указанному контакту.</p></div>
<div><p id="sent" class="form-ok" role="status">Спасибо, сообщение отправлено. Я отвечу вам по указанному контакту.</p>
<form class="form" action="https://api.web3forms.com/submit" method="POST">
<input type="hidden" name="access_key" value="{e(FORM_KEY)}">
<input type="hidden" name="subject" value="Сообщение с сайта yogavam.com">
<input type="hidden" name="from_name" value="Сайт yogavam.com">
<input type="hidden" name="redirect" value="{DOMAIN}/contacts/#sent">
<input type="checkbox" name="botcheck" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
<label>Имя<input type="text" name="name" required autocomplete="name"></label>
<label>Как вам ответить<input type="text" name="contact" required placeholder="Почта, Telegram или телефон"></label>
<label>Сообщение<textarea name="message" rows="5" required></textarea></label>
<button class="btn" type="submit">Отправить</button>
<p class="fine">Отправляя форму, вы соглашаетесь на обработку данных для ответа; сообщение передаётся через сервис Web3Forms.</p>
</form></div></div>''', "tight")
contacts_body = f'''<div class="wrap page-head">{cr}<h1>Контакты</h1>
<p class="lead">Проще всего написать в WhatsApp или Telegram: расскажите о своём запросе, и мы подберём формат занятий.</p></div>
{sec(f"""<div class="contact-cards">{contact_cards}</div>
<div class="prose" style="margin-top:2.5rem"><p>Я в Батуми (Грузия, UTC+4). Онлайн-занятия провожу для учеников из любых стран и часовых поясов.</p>
<p>Стоимость одного занятия (1 час):</p>
<ul><li>Онлайн — {prices_text('online')}</li><li>Очно в Батуми — {prices_text('batumi')}</li></ul></div>""", "tight")}
{contact_form}'''
page("/contacts/", f"Контакты — {AUTHOR}, йогатерапия онлайн и в Батуми",
     f"Как связаться с {AUTHOR} и записаться на индивидуальное занятие йогатерапией онлайн или в Батуми: WhatsApp, Telegram, Instagram, YouTube.",
     contacts_body, graph=[cr_ld], page_type="ContactPage")


# ===================== БЛОГ =====================
ARTICLES = [("/blog/metod-feldenkraisa/", "Метод Фельденкрайза: что это и как проходят занятия",
             "Коротко о методе Фельденкрайза: кто его создал, чем отличаются групповые и индивидуальные занятия, на что обратить внимание новичку.", "2026-10-04")]
cr, cr_ld = crumbs([("/", "Главная"), ("/blog/", "Статьи")])
cards = "".join(f'<article class="card"><time datetime="{d}">{ru_date(d)}</time><h2><a href="{u}">{e(t)}</a></h2><p>{e(s)}</p>{more(u, "Читать")}</article>' for u, t, s, d in ARTICLES)
page("/blog/", f"Статьи о йогатерапии, методе Фельденкрайза и движении | {BRAND}",
     f"Статьи {AUTHOR} о йогатерапии, методе Фельденкрайза, осознанном движении и работе с телом — простым языком.",
     f'<div class="wrap page-head">{cr}<h1>Статьи</h1><p class="lead">Простым языком о теле, движении и практике.</p></div>{sec(f"""<div class="cards">{cards}</div>""", "tight")}{cta_band()}',
     graph=[cr_ld, {"@type": "ItemList", "@id": DOMAIN + "/blog/#list", "itemListElement": [
         {"@type": "ListItem", "position": i + 1, "url": abs_url(u)} for i, (u, *_) in enumerate(ARTICLES)]}], page_type="CollectionPage")

ART_FAQ = [
    ("Метод Фельденкрайза — это лечение?", "Нет. Это педагогический метод обучения осознанному движению, он не заменяет медицинскую помощь. При болях и травмах сначала обратитесь к врачу."),
    ("Нужна ли физическая подготовка?", "Нет. Движения, как правило, небольшие и выполняются в комфортном диапазоне, поэтому метод доступен людям с разным уровнем подготовки."),
    ("Чем индивидуальное занятие отличается от группового?", "В группе ведущий направляет участников словами. На индивидуальном занятии работа строится под конкретного человека и может включать мягкие прикосновения и подсказки руками."),
]
u, t, s, d = ARTICLES[0]
cr, cr_ld = crumbs([("/", "Главная"), ("/blog/", "Статьи"), (u, t)])
article = {"@type": "Article", "@id": abs_url(u) + "#article", "headline": t, "description": s, "inLanguage": "ru",
           "datePublished": d, "dateModified": LASTMOD.get(abs_url(u), {}).get("date", d), "author": {"@id": person_id}, "publisher": {"@id": person_id},
           "mainEntityOfPage": {"@id": abs_url(u) + "#webpage"}, "image": abs_url(OG_IMAGE), "about": [{"@type": "Thing", "name": "Метод Фельденкрайза"}]}
author_box = ""
if PHOTO_W:
    author_box = (f'<a class="author" href="/about/" style="text-decoration:none">{picture("", False, "4rem")}'
                  f'<p><b>{AUTHOR}</b>Инструктор йоги и йогатерапии. Обо мне и моём подходе</p></a>')
TOC = [("kto-sozdal", "Кто создал метод"), ("dva-formata", "Два формата"), ("novichku", "На что обратить внимание новичку"),
       ("v-praktike", "Как я использую метод на своих занятиях"), ("voprosy", "Частые вопросы")]
toc_html = "".join(f'<li><a href="#{i}">{n}</a></li>' for i, n in TOC)
page(u, f"{t} | {BRAND}", s,
     f'''<div class="wrap page-head art-head">{cr}<h1>{e(t)}</h1><p class="meta">Автор: <a href="/about/" rel="author">{AUTHOR}</a>. <time datetime="{d}">{ru_date(d)}</time>, чтение около 4 минут</p>
<p class="lead"><strong>Метод Фельденкрайза — это система занятий, в которой человек учится замечать, как он двигается, и находить более лёгкие способы движения.</strong> Это обучение, а не лечение и не фитнес.</p></div>
{sec(f"""<div class="art-grid"><article class="article prose">
<h2 id="kto-sozdal">Кто создал метод</h2>
<p>Метод разработал Моше Фельденкрайз (1904–1984) — физик и инженер, занимавшийся также дзюдо. Он исследовал, как движение, внимание и привычки связаны между собой, и на этой основе построил систему занятий.</p>
<h2 id="dva-formata">Два формата</h2>
<h3>«Осознавание через движение» (групповой)</h3>
<p>Ведущий словами направляет группу через последовательность неспешных движений, обычно лёжа или сидя. Внимание — на ощущениях, а не на результате: «правильно» и «неправильно» здесь не оценивается.</p>
<h3>«Функциональная интеграция» (индивидуальный)</h3>
<p>Индивидуальное занятие, построенное под конкретного человека. Практик использует мягкие прикосновения и направляющие подсказки, помогая человеку почувствовать новые варианты движения.</p>
<h2 id="novichku">На что обратить внимание новичку</h2>
<p>Движения небольшие и медленные, усилие минимальное; цель — прислушаться к ощущениям, а не «растянуться» или «наработать» мышцы. После занятия многие отмечают, что стоять и ходить стало иначе, но это личный опыт, а не гарантированный результат.</p>
<h2 id="v-praktike">Как я использую метод на своих занятиях</h2>
<p>На персональных тренировках я сочетаю метод Фельденкрайза с йогатерапией, миофасциальными и соматическими упражнениями. Подробнее — на странице <a href="/online/">«Как проходят занятия»</a>.</p>
<div class="note"><p>Метод не заменяет медицинскую помощь. При острой боли, травме или заболевании сначала проконсультируйтесь с врачом.</p></div>
<h2 id="voprosy">Частые вопросы</h2>
{faq_html(ART_FAQ)}
{author_box}</article>
<aside class="art-side"><nav class="toc" aria-label="В статье"><h2>В статье</h2><ol>{toc_html}</ol></nav>
<div class="side-card"><h2>Записаться</h2><p>Расскажите о своём запросе, и я предложу, с чего начать.</p><div class="actions">{contact_row()}</div></div></aside></div>""", "tight")}{cta_band()}''',
     graph=[cr_ld, article, faq_node(abs_url(u), ART_FAQ)], og_type="article")


# ===================== 404 =====================
page("/404.html", f"Страница не найдена | {BRAND}", "Страница не найдена.",
     sec(f'<h1>Страница не найдена</h1><p class="lead" style="margin-top:1.25rem">Проверьте адрес или вернитесь на главную.</p><div class="actions"><a class="btn" href="/">На главную</a></div>'),
     indexable=False)


# ===================== технические файлы =====================
def w(name, text):
    p = os.path.join(OUT, name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f: f.write(text)

w("robots.txt", f"""# Разрешено всем, включая поисковые и ИИ-краулеры
User-agent: *
Allow: /

Sitemap: {DOMAIN}/sitemap.xml
""")
def sm(url, lastmod, imgs):
    im = "".join(f"<image:image><image:loc>{abs_url(i)}</image:loc></image:image>" for i in imgs)
    return f"  <url><loc>{url}</loc><lastmod>{lastmod}</lastmod>{im}</url>"
w("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
  'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n' + "\n".join(sm(*p) for p in pages) + "\n</urlset>\n")
w("llms.txt", f"""# {BRAND}

> Сайт Натальи Умновой — инструктора йоги и йогатерапии, специалиста по движению. Йогатерапия для спины, осанки и здорового движения: индивидуальные занятия онлайн (из любой страны) и очно в Батуми (Грузия). Язык: русский.

Ключевые факты:
- Более 10 лет преподаёт йогу и йогатерапию. Обучение в International Open Yoga Foundation Europe с 2014 года: курс инструкторов, преподаватель, мастер Open Yoga. С 2022 года цикл «Йогатерапия и биомеханика» в Академии йоги и йогатерапии Татьяны Дудиной: {COURSES_N} курсов, {HOURS_N} часов.
- Методы: йогатерапия, метод Фельденкрайза, миофасциальные упражнения, соматические практики, работа с нервной системой и дыханием.
- Подготовка к родам и восстановление после родов.
- Подходит для любого уровня, в том числе для тех, кто никогда не занимался.
- Стоимость одного индивидуального занятия: онлайн — {prices_text('online')}; очно в Батуми — {prices_text('batumi')}.
- Запись через WhatsApp или Telegram. Занятия не являются медицинской услугой.

## Страницы
- [Обо мне]({DOMAIN}/about/): биография, подход, методы
- [Сертификаты]({DOMAIN}/certificates/): обучение и квалификации
- [Как проходят онлайн-занятия]({DOMAIN}/online/): структура занятий, тесты, подготовка, цена, FAQ
- [Занятия в Батуми]({DOMAIN}/batumi/): очные индивидуальные занятия, цена
- [Контакты]({DOMAIN}/contacts/): WhatsApp, Telegram, Instagram, YouTube

## Направления
""" + "".join(f"- [{d['name']}]({abs_url(d['path'])}): {d['desc']}\n" for d in DIRS) + """
## Статьи
""" + "".join(f"- [{t}]({abs_url(u)}): {s}\n" for u, t, s, _ in ARTICLES))
w("site.webmanifest", json.dumps({"name": f"{BRAND} — {AUTHOR}", "short_name": BRAND, "lang": "ru", "start_url": "/", "display": "browser",
    "background_color": "#f1f4f2", "theme_color": "#f1f4f2",
    "icons": [{"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"}]},
    ensure_ascii=False, indent=1))
w("CNAME", "yogavam.com\n")
w(".nojekyll", "")
json.dump(LASTMOD, open(LASTMOD_FILE, "w"), ensure_ascii=False, indent=1)
print("OK:", len(pages), "страниц; сертификатов:", len(CERTS), "; фото:", PHOTO_W, "x", PHOTO_H)
