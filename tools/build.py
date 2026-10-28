#!/usr/bin/env python3
"""Генератор статического сайта yogavam.com.
Запуск: python3 build.py  -> пишет готовый сайт в ./site/
Всё, что надо менять руками, — в блоке НАСТРОЙКИ ниже.
"""
import json, os, shutil, html, datetime, urllib.parse

# ===================== НАСТРОЙКИ =====================
DOMAIN = "https://yogavam.com"
BRAND = "Yogavam"
AUTHOR = "Наталья Умнова"
AUTHOR_FIRST = "Наталья"
WA_NUMBER = "995599018912"
YT_URL = "https://www.youtube.com/@yogaumnova"
PHOTO = "/assets/img/natalya-umnova.jpg"    # портрет 4:5, ~900×1125, до 250 КБ
PHOTO_W, PHOTO_H = 941, 882
OG_IMAGE = "/assets/img/og.jpg"             # 1200×630
GOOGLE_VERIFY = ""                          # содержимое google-site-verification, если не через DNS
YANDEX_VERIFY = ""                          # содержимое yandex-verification
# Сертификаты: файлы класть в /assets/img/certificates/. Пока список пуст — галерея не выводится.
ORG = "International Open Yoga Foundation Europe"
CERTS = [
    {"file": "open-yoga-instructor-2017.jpg", "title": "Курс инструкторов Open Yoga (2014–2017), 816 часов", "alt": "Open Yoga Instructor's Course", "org": ORG, "year": "2017"},
    {"file": "open-yoga-teacher-2018.jpg", "title": "Преподаватель Open Yoga (2014–2018)", "alt": "Open Yoga Teacher", "org": ORG, "year": "2018"},
    {"file": "open-yoga-master-2021.jpg", "title": "Мастер Open Yoga (2014–2021)", "alt": "Open Yoga Master", "org": ORG, "year": "2021"},
]
TODAY = datetime.date.today().isoformat()
OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # корень репозитория
# =====================================================

WA_TEXT = f"Здравствуйте, {AUTHOR_FIRST}! Хочу узнать о занятиях."
WA_URL = f"https://wa.me/{WA_NUMBER}?text=" + urllib.parse.quote(WA_TEXT)
PLACEHOLDER = lambda s: "TODO" in s
e = html.escape

pages = []  # (url, lastmod, [images])



NAV = [("/about/", "Обо мне"), ("/online/", "Онлайн-занятия"), ("/batumi/", "Батуми"),
       ("/blog/", "Статьи"), ("/contacts/", "Контакты")]

person_id = DOMAIN + "/#person"
website_id = DOMAIN + "/#website"

def abs_url(p): return DOMAIN + p

PERSON = {
    "@type": "Person", "@id": person_id, "name": AUTHOR,
    "givenName": "Наталья", "familyName": "Умнова",
    "jobTitle": "Инструктор йоги и йогатерапии",
    "description": "Инструктор йоги и йогатерапии, специалист по движению и методу Фельденкрайза. Более 10 лет преподаёт йогу и йогатерапию, ведёт индивидуальные занятия онлайн и в Батуми, помогает будущим мамам подготовиться к родам и восстановиться после них.",
    "url": abs_url("/about/"),
    "image": {"@type": "ImageObject", "url": abs_url(PHOTO), "width": PHOTO_W, "height": PHOTO_H},
    "knowsAbout": ["йогатерапия", "метод Фельденкрайза", "миофасциальные упражнения", "соматические практики",
                   "работа с нервной системой", "йога для беременных", "восстановление после родов",
                   "биомеханика движения", "осанка"],
    "knowsLanguage": "ru",
    "workLocation": {"@type": "City", "name": "Батуми"},
}
if not PLACEHOLDER(YT_URL):
    PERSON["sameAs"] = [YT_URL]
if CERTS:
    PERSON["hasCredential"] = [{
        "@type": "EducationalOccupationalCredential", "name": c["title"], "credentialCategory": "certificate",
        **({"recognizedBy": {"@type": "Organization", "name": c["org"]}} if c.get("org") else {}),
        **({"dateCreated": c["year"]} if c.get("year") else {}),
        "image": abs_url("/assets/img/certificates/" + c["file"])} for c in CERTS]

WEBSITE = {"@type": "WebSite", "@id": website_id, "name": BRAND, "alternateName": "Йогатерапия с Натальей Умновой",
           "url": DOMAIN + "/", "inLanguage": "ru", "publisher": {"@id": person_id}}

def faq_node(url, qa):
    return {"@type": "FAQPage", "@id": url + "#faq", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in qa]}

def faq_html(qa):
    return "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in qa)

def crumbs(items):
    vis = " / ".join([f'<a href="{u}">{e(n)}</a>' for u, n in items[:-1]] + [e(items[-1][1])])
    node = {"@type": "BreadcrumbList", "@id": abs_url(items[-1][0]) + "#breadcrumb", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": abs_url(u)} for i, (u, n) in enumerate(items)]}
    return f'<nav class="crumbs" aria-label="Навигация">{vis}</nav>', node

def cta(primary="Записаться в WhatsApp", second=("/online/", "Как проходят занятия")):
    s = f'<a class="btn" href="{e(WA_URL)}" rel="noopener" target="_blank">{primary}</a>'
    if second:
        s += f'<a class="btn alt" href="{second[0]}">{second[1]}</a>'
    return f'<div class="actions">{s}</div>'

def cta_box(title, text):
    return f'<aside class="cta-box"><h2>{title}</h2><p>{text}</p>{cta(second=None)}</aside>'

def photo_img(cls="portrait", eager=True):
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<img class="{cls}" src="{PHOTO}" width="{PHOTO_W}" height="{PHOTO_H}" {load} decoding="async" '
            f'alt="{AUTHOR} — инструктор йоги и йогатерапии">')

def certs_gallery(limit=None):
    items = CERTS[:limit] if limit else CERTS
    if not items: return ""
    figs = ""
    for c in items:
        full = "/assets/img/certificates/" + c["file"]
        thumb = full.replace(".jpg", "-thumb.jpg")
        alt = f'Сертификат {c.get("alt", c["title"])}, {c["org"]}, {c["year"]}, {AUTHOR}'
        figs += (f'<figure><a href="{full}" target="_blank" rel="noopener"><img src="{thumb}" width="600" height="826" '
                 f'loading="lazy" decoding="async" alt="{e(alt)}"></a>'
                 f'<figcaption><strong>{e(c["title"])}</strong><br>{e(c["org"])} · {e(c["year"])}</figcaption></figure>')
    return f'<div class="certs">{figs}</div>'

def page(path, title, desc, body, graph=(), page_type="WebPage", indexable=True, images=(), og_type="website",
         extra_page=None):
    url = abs_url(path)
    nav = "".join(f'<li><a href="{u}"{" aria-current=page" if path.startswith(u) else ""}>{n}</a></li>' for u, n in NAV)
    webpage = {"@type": page_type, "@id": url + "#webpage", "url": url, "name": title, "description": desc,
               "inLanguage": "ru", "isPartOf": {"@id": website_id}, "dateModified": TODAY,
               "primaryImageOfPage": {"@type": "ImageObject", "url": abs_url(images[0] if images else OG_IMAGE)}}
    for n in graph:
        if n.get("@type") == "BreadcrumbList": webpage["breadcrumb"] = {"@id": n["@id"]}
    if extra_page: webpage.update(extra_page)
    nodes = ([WEBSITE, PERSON] + [webpage] + list(graph)) if indexable else []
    ld = f'<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@graph": nodes}, ensure_ascii=False)}</script>' if nodes else ""
    robots = "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1" if indexable else "noindex, follow"
    verify = ""
    if GOOGLE_VERIFY: verify += f'<meta name="google-site-verification" content="{GOOGLE_VERIFY}">\n'
    if YANDEX_VERIFY: verify += f'<meta name="yandex-verification" content="{YANDEX_VERIFY}">\n'
    og_img = abs_url(OG_IMAGE)
    doc = f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="robots" content="{robots}">
{f'<link rel="canonical" href="{url}">' if indexable else ''}
<meta name="author" content="{AUTHOR}">
<meta name="theme-color" content="#2f5d50">
{verify}<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon-48.png" sizes="48x48" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="stylesheet" href="/assets/style.css">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:locale" content="ru_RU">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{og_img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{AUTHOR} — йогатерапия и метод Фельденкрайза онлайн и в Батуми">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{og_img}">
{ld}
</head>
<body>
<a class="skip" href="#main">К содержанию</a>
<header class="site"><div class="wrap">
<a class="brand" href="/">{BRAND}</a>
<nav aria-label="Основное меню"><ul>{nav}</ul></nav>
</div></header>
<main id="main"><div class="wrap">
{body}
</div></main>
<footer class="site"><div class="wrap">
<p><strong>{AUTHOR}</strong> — йогатерапия и метод Фельденкрайза, онлайн и в Батуми</p>
<p><a href="{e(WA_URL)}" rel="noopener" target="_blank">WhatsApp</a> · <a href="{YT_URL}" rel="noopener" target="_blank">YouTube</a> · <a href="/blog/">Статьи</a> · <a href="/contacts/">Контакты</a></p>
<p class="small">Материалы сайта носят информационный характер и не заменяют консультацию врача. Занятия не являются медицинской услугой. При острой боли, травмах и заболеваниях сначала обратитесь к врачу.</p>
<p class="small">© {TODAY[:4]} {BRAND}</p>
</div></footer>
</body>
</html>
'''
    target = os.path.join(OUT, path.strip("/"), "index.html") if path != "/404.html" else os.path.join(OUT, "404.html")
    os.makedirs(os.path.dirname(target), exist_ok=True)
    with open(target, "w", encoding="utf-8") as f:
        f.write("\n".join(l for l in doc.split("\n") if l.strip() != "" or False))
    if indexable:
        pages.append((url, TODAY, list(images)))

# ---------- Общие тексты ----------
LEVELS_P = ('<p>Занимаемся <strong>от простого к сложному</strong>. Если вы никогда не пробовали йогу или йогатерапию '
            'и думаете, что «это не для меня» и «у меня не получится», — получится. Начнём с дыхания и простых движений '
            'и пойдём в вашем темпе, без перегрузок и без боли.</p>'
            '<p>Если практика у вас уже есть, углубим её: поработаем над техникой, контролем движения '
            'и тонким чувствованием тела.</p>')

FOR_WHOM = ('<ul class="checks">'
            '<li>чувствуете скованность, боли в мышцах или суставах;</li>'
            '<li>хотите разобраться с напряжением в спине и шее, улучшить осанку;</li>'
            '<li>много сидите и мало двигаетесь;</li>'
            '<li>часто тревожитесь и устаёте от постоянного внутреннего напряжения;</li>'
            '<li>готовитесь к родам или восстанавливаетесь после них.</li></ul>')

# ---------- ГЛАВНАЯ ----------
HOME_FAQ = [
    ("Что такое йогатерапия?",
     "Йогатерапия — направление йоги, в котором упражнения подбирают под состояние и задачи конкретного человека: снять мышечное напряжение, вернуть подвижность суставам и позвоночнику, улучшить осанку и дыхание. Это не медицинское лечение, а мягкая двигательная практика, которая дополняет рекомендации врача."),
    ("Подойдут ли занятия, если я никогда не занимался йогой?",
     "Да. Занятия идут от простого к сложному и подходят для любого уровня подготовки. Начинаем с дыхания и базовых движений, темп и нагрузку подбираем под вас."),
    ("Как проходят онлайн-занятия?",
     "Индивидуально, по видеосвязи. Наталья видит вас целиком, корректирует технику по ходу занятия и выстраивает практику под ваши цели. Нужны камера, стабильный интернет, коврик и немного свободного места."),
    ("Можно ли заниматься во время беременности?",
     "Да, если нет противопоказаний и ваш врач не возражает. Упражнения подбираются с учётом срока и самочувствия. После родов занятия помогают мягко восстановиться."),
    ("Где проходят очные занятия?",
     "В Батуми, индивидуально. Постоянной студии нет, поэтому место и время согласуем под вас. Если вы в другом городе или стране, подойдут онлайн-занятия."),
]
certs_teaser = ""
if CERTS:
    certs_teaser = f'<section><h2>Сертификаты и обучение</h2>{certs_gallery(4)}<p><a href="/about/#sertifikaty">Все сертификаты</a></p></section>'

page("/", "Йогатерапия онлайн и в Батуми — Наталья Умнова | Yogavam",
     "Индивидуальные занятия йогатерапией и методом Фельденкрайза онлайн и в Батуми. Для новичков и опытных: спина, суставы, осанка, стресс, подготовка к родам.",
f'''<section class="hero">
<p class="eyebrow">{AUTHOR} · йогатерапия и метод Фельденкрайза</p>
<h1>Йогатерапия и метод Фельденкрайза: индивидуальные занятия онлайн и в Батуми</h1>
<p class="lead">Мягкая практика, которая снимает напряжение, возвращает телу подвижность и радость движения. Программу подбираю под ваше тело, ваши задачи и ваш уровень подготовки.</p>
{cta()}
</section>
<section class="about" id="obo-mne">
{photo_img()}
<div>
<h2>Обо мне</h2>
<p class="role"><strong>{AUTHOR}</strong> — инструктор йоги и йогатерапии, специалист по движению и методу Фельденкрайза. Более 10 лет преподаю и помогаю восстанавливать женское здоровье.</p>
<p>Я не учу «правильно стоять в асанах». Я учу тело двигаться иначе: свободнее, экономнее, функциональнее, чтобы этот навык работал в обычной жизни — за рабочим столом, с ребёнком на руках, на прогулке.</p>
<p>На занятиях объединяю йогатерапию, метод Фельденкрайза, миофасциальные упражнения, соматику и работу с нервной системой. Опираюсь на современные данные анатомии, биомеханики и физической реабилитации и объясняю их простым языком: вы понимаете, что происходит в теле и почему.</p>
<p>Помогаю будущим мамам подготовить тело к родам и мягко восстановиться после них.</p>
<p>Постоянно учусь и повышаю квалификацию, поэтому в практике всегда есть место новому.</p>
<p><a href="/about/">Подробнее обо мне</a> · <a href="/about/#sertifikaty">Обучение и сертификаты</a></p>
</div>
</section>
<section>
<h2>Кому подойдут занятия</h2>
<p>Приходите, если вы:</p>
{FOR_WHOM}
</section>
<section>
<h2>Подойдёт для любого уровня — даже если вы никогда не занимались</h2>
{LEVELS_P}
</section>
<section>
<h2>Как проходят занятия</h2>
<ol class="steps">
<li><strong>Знакомство и тесты.</strong> Обсуждаем ваш запрос. Если нужно, проводим двигательные тесты: оцениваем мышцы, суставы и дыхание.</li>
<li><strong>Практика под ваши цели.</strong> По результатам выстраиваю индивидуальную программу. Начинаем с базы: дыхание, замедление, внимание к ощущениям.</li>
<li><strong>Заметный прогресс.</strong> Через некоторое время повторяем тесты, и вы сами видите, что изменилось.</li>
</ol>
<p><a href="/online/">Подробнее о занятиях и подготовке к онлайн-тренировке</a></p>
</section>
{certs_teaser}
<section>
<h2>Форматы занятий</h2>
<div class="grid">
<div class="card"><h3>Онлайн, индивидуально</h3><p>Персональные тренировки по видеосвязи из любой точки мира. Вижу вас целиком и корректирую технику в моменте.</p><p><a href="/online/">Как проходят онлайн-занятия</a></p></div>
<div class="card"><h3>Очно в Батуми</h3><p>Индивидуальная работа один на один. Место и время подбираем под ваш график.</p><p><a href="/batumi/">Занятия в Батуми</a></p></div>
<div class="card"><h3>Статьи</h3><p>Простым языком о теле, движении, методе Фельденкрайза и йогатерапии.</p><p><a href="/blog/">Читать статьи</a></p></div>
</div>
</section>
<section>
<h2>Частые вопросы</h2>
{faq_html(HOME_FAQ)}
</section>
{cta_box("Сделайте первый шаг", "Напишите мне в WhatsApp и расскажите, что вас беспокоит. Я отвечу и предложу формат первого занятия.")}
''', graph=[faq_node(DOMAIN + "/", HOME_FAQ)], images=[PHOTO] + [f"/assets/img/certificates/{c['file']}" for c in CERTS[:4]],
     extra_page={"about": {"@id": person_id}})

# ---------- ОБО МНЕ ----------
cr, cr_ld = crumbs([("/", "Главная"), ("/about/", "Обо мне")])
page("/about/", "Наталья Умнова — инструктор йоги и йогатерапии, метод Фельденкрайза",
     "Наталья Умнова: более 10 лет преподаёт йогу и йогатерапию. Метод Фельденкрайза, миофасциальные техники, соматика, йога для беременных и восстановление после родов.",
f'''{cr}
<section class="about about-page">
{photo_img()}
<div>
<h1>{AUTHOR}</h1>
<p class="lead">Инструктор йоги и йогатерапии, специалист по движению и методу Фельденкрайза. Более 10 лет помогаю людям освободиться от скованности и напряжения, вернуть телу подвижность, а себе — радость жизни.</p>
{cta(second=("/online/", "Как проходят занятия"))}
</div>
</section>
<div class="read">
<h2>Мой подход</h2>
<p>Я выхожу за рамки классических асан. На занятиях соединяю методы йогатерапии, которые развивают телесный интеллект и двигательный контроль, с современным научным взглядом на анатомию, биомеханику и физическую реабилитацию.</p>
<p>Мы не просто выполняем упражнения, а учим тело двигаться иначе: функциональнее и экономнее. Этот навык вы переносите в повседневную жизнь, и самочувствие меняется не только на коврике.</p>
<p>Сложные взаимосвязи в теле объясняю простым языком. Когда понимаешь, откуда берётся дискомфорт и что с ним делать, практика становится осознанной и глубокой.</p>
<h2>Методы, с которыми я работаю</h2>
<ul>
<li><strong>Йогатерапия</strong> — упражнения, подобранные под ваше состояние и задачи.</li>
<li><strong>Метод Фельденкрайза</strong> — обучение лёгкому и осознанному движению. <a href="/blog/metod-feldenkraisa/">Что это за метод</a>.</li>
<li><strong>Миофасциальные упражнения</strong> — работа с напряжением в мышцах и фасциях.</li>
<li><strong>Соматические практики</strong> — замедление, тонкое чувствование тела, отпускание зажимов.</li>
<li><strong>Работа с нервной системой и дыханием</strong> — чтобы снизить уровень стресса и тревоги.</li>
</ul>
<h2>Беременность и восстановление после родов</h2>
<p>Помогаю будущим мамам подготовить тело к родам мягко и безопасно, с учётом срока и самочувствия. После родов помогаю бережно восстановить силу, подвижность и контакт со своим телом.</p>
<p class="small">Занятия во время беременности — при отсутствии противопоказаний и после согласования с вашим врачом.</p>
<h2>Кому подойдут персональные тренировки</h2>
<p>Приглашаю вас, если вы:</p>
{FOR_WHOM}
{LEVELS_P}
<h2 id="sertifikaty">Обучение и сертификаты</h2>
<p>Прошла обучение в Международном фонде Open Yoga (International Open Yoga Foundation Europe): курс инструкторов (2014–2017, 447 часов теории и 369 часов практики), затем квалификации Open Yoga Teacher (2018) и Open Yoga Master (2021). Сертификаты подтверждаются на сайте фонда.</p>
<p>Я нахожусь в непрерывном обучении и регулярно повышаю квалификацию: изучаю новые методы работы с телом и проверяю их на практике. Поэтому со мной остаются надолго, даже достигнув результата: нам всегда есть что исследовать.</p>
</div>
{certs_gallery()}
{cta_box("Приходите на занятие", "Напишите в WhatsApp, расскажите о своём запросе, и мы подберём формат: онлайн или очно в Батуми.")}
''', graph=[cr_ld], page_type="ProfilePage", images=[PHOTO] + [f"/assets/img/certificates/{c['file']}" for c in CERTS],
     extra_page={"mainEntity": {"@id": person_id}})

# ---------- ОНЛАЙН / КАК ПРОХОДЯТ ЗАНЯТИЯ ----------
ONLINE_FAQ = [
    ("Что нужно для онлайн-занятия?",
     "Телефон, планшет или ноутбук с камерой, стабильный интернет, коврик и свободное место, чтобы заниматься стоя, сидя и лёжа. Одежда — удобная и облегающая, чтобы было видно положение суставов, таза и позвоночника."),
    ("Подойдут ли занятия, если я никогда не занимался йогой?",
     "Да. Занятия идут от простого к сложному: начинаем с дыхания и базовых движений, нагрузку и темп подбираем под вас. Опыт и физическая подготовка не нужны."),
    ("Как установить камеру?",
     "Так, чтобы в кадре было всё тело — от головы до стоп, а место было хорошо освещено. Во время занятия может понадобиться повернуть камеру, чтобы показать движение сбоку или спереди."),
    ("Можно ли заниматься небольшой группой?",
     "Основной формат — индивидуальные занятия. Возможность групповых онлайн-занятий уточняйте в WhatsApp."),
]
cr, cr_ld = crumbs([("/", "Главная"), ("/online/", "Онлайн-занятия")])
online_service = {"@type": "Service", "@id": DOMAIN + "/online/#service",
                  "name": "Индивидуальные онлайн-занятия йогатерапией и методом Фельденкрайза",
                  "serviceType": "Персональные тренировки по йогатерапии онлайн", "provider": {"@id": person_id},
                  "areaServed": {"@type": "Place", "name": "Весь мир"}, "availableLanguage": "ru",
                  "url": DOMAIN + "/online/",
                  "description": "Индивидуальные занятия по видеосвязи: двигательные тесты, программа под ваши цели, коррекция техники в реальном времени. Для начинающих и опытных."}
page("/online/", "Как проходят онлайн-занятия йогатерапией — индивидуально | Yogavam",
     "Индивидуальные онлайн-занятия йогатерапией и методом Фельденкрайза: с чего начинаем, тесты и программа под ваши цели, как подготовиться к занятию.",
f'''{cr}
<div class="read">
<h1>Как проходят онлайн-занятия</h1>
<p class="lead">Индивидуальные тренировки по видеосвязи из любой точки мира. Я вижу вас, корректирую технику по ходу занятия и выстраиваю практику под ваши цели.</p>
<h2>Начинаем с базы</h2>
<p>Первые занятия посвящены базовым навыкам: дыханию, простым движениям, умению замедляться, наблюдать за ощущениями и переключать внимание на тело. Это фундамент, на котором строится всё остальное.</p>
<h2>Тесты и программа под ваши цели</h2>
<p>Если нужно, проводим двигательные тесты: оцениваем состояние мышц и суставов, дыхание. По результатам я выстраиваю практику под ваши задачи. Через некоторое время повторяем тесты, и вы своими глазами видите прогресс.</p>
<h2>Почему мы начинаем со снятия напряжения</h2>
<p>Мой опыт работы с клиентами показывает: в основе большинства проблем в теле лежит стресс, который копится годами. Мягкие соматические практики помогают замедлиться. Уходит напряжение, тело перестаёт сопротивляться и отпускает зажимы, выравниваются перекосы — и начинаются изменения.</p>
<h2>Практика без стресса</h2>
<p>Для меня важно, чтобы занятия не стали для вас ещё одной обязанностью «через силу». Наша цель — регулярность, которая приносит удовольствие и устойчивый результат.</p>
<h2>Для начинающих и опытных</h2>
{LEVELS_P}
<h2>Почему со мной остаются надолго</h2>
<p>Многие продолжают заниматься и после того, как достигли своей цели. Одна из причин — моё непрерывное обучение: мы вместе исследуем новые методы работы с телом, и практика не превращается в рутину.</p>
<h2 id="podgotovka">Как подготовиться к онлайн-занятию</h2>
<p>Чтобы я хорошо видела, как вы выполняете упражнения, вовремя подсказывала и давала рекомендации именно вам, подготовьтесь заранее:</p>
<ol class="prep">
<li><strong>Подключитесь за 10 минут до начала.</strong> Проверим звук, изображение и положение камеры: мне важно хорошо видеть вас всё занятие.</li>
<li><strong>Наденьте удобную облегающую одежду.</strong> Не слишком свободную и не сковывающую движения: мне нужно видеть положение суставов, таза и позвоночника.</li>
<li><strong>Установите камеру так, чтобы в кадре было всё тело</strong> — от головы до стоп. Выберите хорошо освещённое место. Во время занятия я могу попросить повернуть камеру, чтобы посмотреть движение сбоку или спереди.</li>
<li><strong>Подготовьте место.</strong> Расстелите коврик и освободите пространство вокруг, чтобы удобно заниматься стоя, сидя и лёжа.</li>
</ol>
<p>Моя задача — наблюдать за вами, замечать особенности движений, корректировать технику и давать рекомендации с учётом ваших индивидуальных особенностей. Чем лучше я вас вижу, тем точнее и полезнее наша совместная работа.</p>
<p>Спасибо за внимательное отношение к практике. До встречи на занятии! 💚</p>
<h2>Стоимость и запись</h2>
<p>Стоимость и удобное время обсудим в <a href="{e(WA_URL)}" rel="noopener" target="_blank">WhatsApp</a>. Живёте в Батуми или приехали ненадолго? Есть <a href="/batumi/">очные занятия</a>.</p>
<h2>Частые вопросы</h2>
{faq_html(ONLINE_FAQ)}
</div>
{cta_box("Найдём причину дискомфорта", "Хотите понять, откуда берутся боль, напряжение и дискомфорт в теле, и избавиться от них? Напишите мне в WhatsApp: пришлю короткую анкету, и по ней мы спланируем первое занятие.")}
''', graph=[cr_ld, online_service, faq_node(DOMAIN + "/online/", ONLINE_FAQ)], extra_page={"about": {"@id": DOMAIN + "/online/#service"}})

# ---------- БАТУМИ ----------
cr, cr_ld = crumbs([("/", "Главная"), ("/batumi/", "Батуми")])
batumi_service = {"@type": "Service", "@id": DOMAIN + "/batumi/#service",
                  "name": "Индивидуальные занятия йогатерапией и методом Фельденкрайза в Батуми",
                  "serviceType": "Персональные тренировки по йогатерапии", "provider": {"@id": person_id},
                  "areaServed": {"@type": "City", "name": "Батуми", "containedInPlace": {"@type": "Country", "name": "Грузия"}},
                  "availableLanguage": "ru", "url": DOMAIN + "/batumi/"}
page("/batumi/", "Йогатерапия в Батуми — индивидуальные занятия | Наталья Умнова",
     "Индивидуальные занятия йогатерапией и методом Фельденкрайза в Батуми: персонально, в удобное время. Для начинающих и опытных, для беременных и после родов.",
f'''{cr}
<div class="read">
<h1>Индивидуальные занятия йогатерапией в Батуми</h1>
<p class="lead">Очные персональные тренировки в Батуми — для тех, кто живёт здесь постоянно или приехал на время.</p>
<h2>Формат</h2>
<p>Работаем один на один. Постоянной студии нет, поэтому место и время подбираем вместе, под ваш график.</p>
<h2>Что происходит на занятии</h2>
<p>Начинаем с вашего запроса и, если нужно, с двигательных тестов. Дальше — практика под ваши цели: йогатерапия, метод Фельденкрайза, миофасциальные и соматические упражнения, работа с дыханием. Подробнее о структуре — на странице <a href="/online/">«Как проходят занятия»</a>: очно мы работаем по тому же принципу.</p>
<h2>Кому подойдёт</h2>
{FOR_WHOM}
{LEVELS_P}
<h2>Запись</h2>
<p>Напишите в <a href="{e(WA_URL)}" rel="noopener" target="_blank">WhatsApp</a>: обсудим запрос, место и время. Если вы не в Батуми, подойдут <a href="/online/">онлайн-занятия</a>.</p>
</div>
{cta_box("Записаться на занятие в Батуми", "Расскажите, что вас беспокоит, и я предложу удобное время и место.")}
''', graph=[cr_ld, batumi_service], extra_page={"about": {"@id": DOMAIN + "/batumi/#service"}})

# ---------- КОНТАКТЫ ----------
cr, cr_ld = crumbs([("/", "Главная"), ("/contacts/", "Контакты")])
page("/contacts/", "Контакты — Наталья Умнова, йогатерапия онлайн и в Батуми",
     "Как связаться с Натальей Умновой и записаться на индивидуальное занятие йогатерапией онлайн или в Батуми: WhatsApp и YouTube.",
f'''{cr}
<div class="read">
<h1>Контакты</h1>
<p class="lead">Проще всего написать в WhatsApp: расскажите о своём запросе, и мы подберём формат занятий.</p>
{cta(primary="Написать в WhatsApp", second=(YT_URL, "YouTube-канал"))}
<p>Я в Батуми (Грузия, UTC+4). Онлайн-занятия провожу для учеников из любых стран и часовых поясов.</p>
</div>
''', graph=[cr_ld], page_type="ContactPage")

# ---------- БЛОГ ----------
ARTICLES = [("/blog/metod-feldenkraisa/", "Метод Фельденкрайза: что это и как проходят занятия",
             "Коротко о методе Фельденкрайза: кто его создал, чем отличаются групповые и индивидуальные занятия, на что обратить внимание новичку.",
             "2026-10-04")]
cr, cr_ld = crumbs([("/", "Главная"), ("/blog/", "Статьи")])
cards = "".join(f'<div class="card"><h2 class="h3"><a href="{u}">{e(t)}</a></h2><p class="meta"><time datetime="{d}">{d}</time></p><p>{e(s)}</p></div>' for u, t, s, d in ARTICLES)
page("/blog/", "Статьи о йогатерапии, методе Фельденкрайза и движении | Yogavam",
     "Статьи Натальи Умновой о йогатерапии, методе Фельденкрайза, осознанном движении и работе с телом — простым языком.",
f'''{cr}
<h1>Статьи</h1>
<p class="lead">Простым языком о теле, движении и практике.</p>
<div class="grid">{cards}</div>
''', graph=[cr_ld, {"@type": "ItemList", "@id": DOMAIN + "/blog/#list", "itemListElement": [
    {"@type": "ListItem", "position": i + 1, "url": abs_url(u)} for i, (u, *_ ) in enumerate(ARTICLES)]}],
     page_type="CollectionPage")

# ---------- СТАТЬЯ ----------
ART_FAQ = [
    ("Метод Фельденкрайза — это лечение?", "Нет. Это педагогический метод обучения осознанному движению, он не заменяет медицинскую помощь. При болях и травмах сначала обратитесь к врачу."),
    ("Нужна ли физическая подготовка?", "Нет. Движения, как правило, небольшие и выполняются в комфортном диапазоне, поэтому метод доступен людям с разным уровнем подготовки."),
    ("Чем индивидуальное занятие отличается от группового?", "В группе ведущий направляет участников словами. На индивидуальном занятии работа строится под конкретного человека и может включать мягкие прикосновения и подсказки руками."),
]
u, t, s, d = ARTICLES[0]
cr, cr_ld = crumbs([("/", "Главная"), ("/blog/", "Статьи"), (u, t)])
article = {"@type": "Article", "@id": abs_url(u) + "#article", "headline": t, "description": s, "inLanguage": "ru",
           "datePublished": d, "dateModified": TODAY, "author": {"@id": person_id}, "publisher": {"@id": person_id},
           "mainEntityOfPage": {"@id": abs_url(u) + "#webpage"}, "image": abs_url(OG_IMAGE),
           "about": [{"@type": "Thing", "name": "Метод Фельденкрайза"}]}
page(u, t + " | Yogavam", s,
f'''{cr}
<article class="read">
<h1>{e(t)}</h1>
<p class="meta">Автор: <a href="/about/" rel="author">{AUTHOR}</a>, инструктор йоги и йогатерапии · <time datetime="{d}">{d}</time> · чтение ~4 мин</p>
<p class="lead"><strong>Метод Фельденкрайза — это система занятий, в которой человек учится замечать, как он двигается, и находить более лёгкие способы движения.</strong> Это обучение, а не лечение и не фитнес.</p>
<h2>Кто создал метод</h2>
<p>Метод разработал Моше Фельденкрайз (1904–1984) — физик и инженер, занимавшийся также дзюдо. Он исследовал, как движение, внимание и привычки связаны между собой, и на этой основе построил систему занятий.</p>
<h2>Два формата</h2>
<h3>«Осознавание через движение» (групповой)</h3>
<p>Ведущий словами направляет группу через последовательность неспешных движений, обычно лёжа или сидя. Внимание — на ощущениях, а не на результате: «правильно» и «неправильно» здесь не оценивается.</p>
<h3>«Функциональная интеграция» (индивидуальный)</h3>
<p>Индивидуальное занятие, построенное под конкретного человека. Практик использует мягкие прикосновения и направляющие подсказки, помогая человеку почувствовать новые варианты движения.</p>
<h2>На что обратить внимание новичку</h2>
<p>Движения небольшие и медленные, усилие минимальное; цель — прислушаться к ощущениям, а не «растянуться» или «наработать» мышцы. После занятия многие отмечают, что стоять и ходить стало иначе, но это личный опыт, а не гарантированный результат.</p>
<h2>Как я использую метод на своих занятиях</h2>
<p>На персональных тренировках я сочетаю метод Фельденкрайза с йогатерапией, миофасциальными и соматическими упражнениями. Подробнее — на странице <a href="/online/">«Как проходят занятия»</a>.</p>
<div class="note">Метод не заменяет медицинскую помощь. При острой боли, травме или заболевании сначала проконсультируйтесь с врачом.</div>
<h2>Частые вопросы</h2>
{faq_html(ART_FAQ)}
</article>
{cta()}
''', graph=[cr_ld, article, faq_node(abs_url(u), ART_FAQ)], og_type="article")

# ---------- 404 ----------
page("/404.html", "Страница не найдена | Yogavam", "Страница не найдена.",
     '<h1>Страница не найдена</h1><p>Проверьте адрес или перейдите <a href="/">на главную</a>.</p>', indexable=False)

# ---------- ТЕХНИЧЕСКИЕ ФАЙЛЫ ----------
def w(name, text):
    p = os.path.join(OUT, name); os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f: f.write(text)

w("robots.txt", f"""# Разрешено всем, включая поисковые и ИИ-краулеры (Googlebot, Bingbot, YandexBot, OAI-SearchBot, PerplexityBot, ClaudeBot и др.)
User-agent: *
Allow: /

Sitemap: {DOMAIN}/sitemap.xml
""")

def sm_entry(url, lastmod, imgs):
    im = "".join(f"<image:image><image:loc>{abs_url(i)}</image:loc></image:image>" for i in imgs)
    return f"  <url><loc>{url}</loc><lastmod>{lastmod}</lastmod>{im}</url>"
w("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
  'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n' + "\n".join(sm_entry(*p) for p in pages) + "\n</urlset>\n")

w("llms.txt", f"""# {BRAND}

> Сайт Натальи Умновой — инструктора йоги и йогатерапии, специалиста по движению и методу Фельденкрайза. Индивидуальные занятия онлайн (из любой страны) и очно в Батуми (Грузия). Язык: русский.

Ключевые факты:
- Более 10 лет преподаёт йогу и йогатерапию.
- Методы: йогатерапия, метод Фельденкрайза, миофасциальные упражнения, соматические практики, работа с нервной системой и дыханием.
- Опирается на современные данные анатомии, биомеханики и физической реабилитации.
- Подготовка к родам и восстановление после родов.
- Подходит для любого уровня, в том числе для тех, кто никогда не занимался.
- Запись через WhatsApp, онлайн-бронирования нет. Занятия не являются медицинской услугой.

## Страницы
- [Обо мне]({DOMAIN}/about/): биография, подход, методы, обучение и сертификаты
- [Как проходят онлайн-занятия]({DOMAIN}/online/): структура занятий, тесты, подготовка к онлайн-занятию, FAQ
- [Занятия в Батуми]({DOMAIN}/batumi/): очные индивидуальные занятия
- [Контакты]({DOMAIN}/contacts/): WhatsApp, YouTube

## Статьи
""" + "".join(f"- [{t}]({abs_url(u)}): {s}\n" for u, t, s, _ in ARTICLES))

w("site.webmanifest", json.dumps({"name": f"{BRAND} — {AUTHOR}", "short_name": BRAND, "lang": "ru",
    "start_url": "/", "display": "browser", "background_color": "#faf7f2", "theme_color": "#2f5d50",
    "icons": [{"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"},
              {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"}]}, ensure_ascii=False, indent=1))
w("CNAME", "yogavam.com\n")
w(".nojekyll", "")

if PLACEHOLDER(WA_NUMBER) or PLACEHOLDER(YT_URL):
    print("ВНИМАНИЕ: не заполнены WA_NUMBER / YT_URL")
print("OK:", len(pages), "страниц ->", OUT)
