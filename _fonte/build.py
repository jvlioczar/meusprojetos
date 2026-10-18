#!/usr/bin/env python3
"""
Gerador do site meusprojetos.biblioverse.org

Edite os dados em DATA (categorias, projetos e textos) e rode:
    python3 build.py

Saídas:
  Dentro do repositório (este arquivo em _fonte/): o site é gerado na raiz do repositório.
  Fora do repositório: o site é gerado em dist/.
  preview/  -> versão para a pré-visualização no Claude (não vai para o GitHub)
"""
import html, json, os, shutil
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE_URL = "https://meusprojetos.biblioverse.org"
LAST_UPDATED = date(2026, 10, 18)

# ------------------------------------------------------------------
# TEXTOS DA INTERFACE
# ------------------------------------------------------------------
UI = {
  "pt": {
    "html_lang": "pt-BR", "og_locale": "pt_BR",
    "seo_title": "Julio Cesar Prava · Projetos de design, IA e intercâmbio",
    "seo_desc": "Portfólio de Julio Cesar Prava, designer gráfico brasileiro em Brisbane: projetos de design, IA, intercâmbio, pensamento crítico, livros, curadoria e guias.",
    "skip": "Pular para os projetos",
    "lang_label": "Idioma",
    "hello": "G'day, eu sou",
    "bio": "Designer gráfico, criador de conteúdo, curador e ativista. Brasileiro em Brisbane, com mais de 14 anos de design e um monte de projetos sobre ética, IA, intercâmbio e boas listas.",
    "socials": "Redes sociais",
    "stats": [("14+", "anos de design"), ("30+", "projetos"), ("17", "bibliotecas")],
    "avatar_alt": "Ilustração de Julio: cabelo preto, bigode, barba castanha e moletom azul",
    "shortcuts": "Atalhos para categorias",
    "filter_label": "Filtrar por categoria",
    "all": "Todos",
    "project_one": "projeto", "project_many": "projetos",
    "wip": "Em construção", "writing": "Em escrita",
    "invite_title": "Quer fazer parte?",
    "invite_text": "Muitos desses projetos são colaborativos e estão sempre crescendo. Se você quer sugerir um link, ajudar na curadoria de uma biblioteca, traduzir, revisar ou criar algo junto, me chama.",
    "invite_ig": "Chamar no Instagram",
    "invite_li": "Conectar no LinkedIn",
    "place": "Brisbane, Austrália",
    "updated": "Última atualização",
    "months": ["janeiro","fevereiro","março","abril","maio","junho","julho","agosto","setembro","outubro","novembro","dezembro"],
    "job": "Designer gráfico",
  },
  "en": {
    "html_lang": "en-AU", "og_locale": "en_AU",
    "seo_title": "Julio Cesar Prava · Design, AI and study abroad projects",
    "seo_desc": "Portfolio of Julio Cesar Prava, a Brazilian graphic designer in Brisbane: design, AI, study abroad, critical thinking, books, curation and guides.",
    "skip": "Skip to projects",
    "lang_label": "Language",
    "hello": "G'day, I'm",
    "bio": "Graphic designer, content creator, curator and activist. A Brazilian in Brisbane with 14+ years in design and a whole bunch of projects on ethics, AI, study abroad and good lists.",
    "socials": "Social media",
    "stats": [("14+", "years in design"), ("30+", "projects"), ("17", "libraries")],
    "avatar_alt": "Illustration of Julio: black hair, moustache, brown beard and a blue hoodie",
    "shortcuts": "Category shortcuts",
    "filter_label": "Filter by category",
    "all": "All",
    "project_one": "project", "project_many": "projects",
    "wip": "Under construction", "writing": "Still writing",
    "invite_title": "Want to get involved?",
    "invite_text": "Lots of these projects are collaborative and always growing. If you'd like to suggest a link, help curate a library, translate, proofread or build something together, flick me a message.",
    "invite_ig": "Message me on Instagram",
    "invite_li": "Connect on LinkedIn",
    "place": "Brisbane, Australia",
    "updated": "Last updated",
    "months": ["January","February","March","April","May","June","July","August","September","October","November","December"],
    "job": "Graphic designer",
  },
}

SOCIALS = [
  ("Instagram", "https://instagram.com/sencientista"),
  ("LinkedIn", "https://linkedin.com/in/juliocesarprava"),
  ("Behance", "https://behance.net/juliocesarprava"),
]
SAME_AS = [
  "https://instagram.com/sencientista", "https://instagram.com/gdayjulio", "https://www.tiktok.com/@gdayjulio",
  "https://www.youtube.com/@gdayjulio", "https://linkedin.com/in/juliocesarprava",
  "https://behance.net/juliocesarprava", "https://biblioverse.org",
]

# ------------------------------------------------------------------
# CATEGORIAS  (dark=True: texto escuro sobre a cor)
# ------------------------------------------------------------------
CATEGORIES = [
  dict(id="design", color="--c-design", dark=True,
       pt=("Design", None, "Bibliotecas, blogs e inspiração para quem trabalha com design."),
       en=("Design", None, "Libraries, blogs and inspo for anyone who works in design.")),
  dict(id="ia", color="--c-ia",
       pt=("Inteligência Artificial", "IA", "Ferramentas e a história da inteligência artificial."),
       en=("Artificial Intelligence", "AI", "AI tools and the history behind them.")),
  dict(id="inter", color="--c-inter",
       pt=("Intercâmbio e Idiomas", "Intercâmbio", "Tudo para quem quer estudar, morar e trabalhar na Austrália."),
       en=("Study Abroad & Languages", "Study Abroad", "Everything you need to study, live and work in Australia.")),
  dict(id="pens", color="--c-pens",
       pt=("Pensamento Crítico", None, "Testes, publicações e bibliotecas para pensar melhor e com mais coerência."),
       en=("Critical Thinking", None, "Quizzes, publications and libraries to help you think more clearly and consistently.")),
  dict(id="livro", color="--c-livro",
       pt=("Livros", None, "Um livro publicado e dois a caminho."),
       en=("Books", None, "One book out, two on the way.")),
  dict(id="cur", color="--c-cur", dark=True,
       pt=("Curadoria", None, "Hubs e coleções com curadoria humana."),
       en=("Curation", None, "Hand-picked hubs and collections, curated by real people.")),
  dict(id="guia", color="--c-guia",
       pt=("Guias e Diretórios", None, "Diretórios práticos para viver bem em Brisbane."),
       en=("Guides & Directories", None, "Practical directories for making the most of Brisbane.")),
  dict(id="hom", color="--c-hom",
       pt=("Homenagens", None, "Memória e afeto em forma de site."),
       en=("Tributes", None, "Memory and love, in website form.")),
  dict(id="out", color="--c-out",
       pt=("Outros", None, "Bibliotecas temáticas, blogs de estética e projetos que estão nascendo."),
       en=("Other", None, "Themed libraries, aesthetics blogs and a few projects still taking shape.")),
]

# ------------------------------------------------------------------
# PROJETOS
#   status: None (ativo) | "wip" (em construção) | "writing" (em escrita)
#   url: None quando ainda não há link
#   tags: lista de (pt, en)
# ------------------------------------------------------------------
def P(cat, name, url, desc, status=None, tags=()):
    return dict(cat=cat, name=name, url=url, desc=desc, status=status, tags=list(tags))

T = {
  "pub": ("Publicado", "Published"), "altaes": ("Estética alternativa", "Alternative aesthetics"),
  "aes": ("Estética", "Aesthetics"), "code": ("Programação", "Coding"), "music": ("Música", "Music"),
  "data": ("Dados", "Data"), "web3": ("Web3", "Web3"), "games": ("Games", "Gaming"),
  "prod": ("Produtividade", "Productivity"), "career": ("Carreira", "Careers"),
}

PROJECTS = [
  # Design
  P("design", ("Biblioteca de Design", "Design Library"), "https://design.biblioverse.org",
    ("Diretório de sites e ferramentas úteis para designers.", "A directory of handy sites and tools for designers.")),
  P("design", ("Brazuca Design", "Brazuca Design"), "https://brazuca.design.blog",
    ("Blog sobre design gráfico feito por um brasileiro.", "A graphic design blog by a Brazilian designer.")),
  P("design", ("Pôsteres", "Posters"), "https://posteres.tumblr.com",
    ("Inspiração para pôsteres de eventos.", "Inspiration for event posters.")),
  P("design", ("Biblioteca de Fotografia", "Photography Library"), "https://photography.biblioverse.org",
    ("Recursos, apps e referências para fotografia.", "Resources, apps and references for photography."), "wip"),
  P("design", ("Biblioteca de Mídia Impressa", "Print Media Library"), "https://print.biblioverse.org",
    ("Revistas, jornais, gráficas e o universo do impresso.", "Magazines, newspapers, printers and the world of print."), "wip"),

  # IA
  P("ia", ("Biblioteca de IAs", "AI Library"), "https://ai.biblioverse.org",
    ("As principais ferramentas de inteligência artificial, organizadas por uso.", "The top AI tools, sorted by what they do.")),
  P("ia", ("Timeline da IA", "AI Timeline"), "https://aihistory.biblioverse.org",
    ("Linha do tempo interativa com os marcos da história da IA.", "An interactive timeline of the big milestones in AI history.")),

  # Intercâmbio e Idiomas
  P("inter", ("Brasileiros na Austrália", "Brazilians in Australia"), "https://brasileirosnaaustralia.biblioverse.org",
    ("Criadores, agências, apps e guia de chegada para quem vem para a Austrália.", "Creators, agencies, apps and an arrival guide for anyone moving to Australia.")),
  P("inter", ("Austrália Para Todos", "Australia For Everyone"), "https://australiaparatodos.wordpress.com",
    ("Conteúdo sobre a Austrália para o público brasileiro.", "Content about Australia for a Brazilian audience.")),
  P("inter", ("Austrália vs Brasil", "Australia vs Brazil"), "https://australiavsbrasil.biblioverse.org",
    ("Infográfico interativo comparando os dois países com índices oficiais.", "An interactive infographic comparing both countries using official data.")),
  P("inter", ("G'day Julio", "G'day Julio"), "https://instagram.com/gdayjulio",
    ("Dicas, reflexões e humor sobre estudar, trabalhar e viver na Austrália.", "Tips, reflections and a laugh or two about studying, working and living in Australia.")),
  P("inter", ("Biblioteca de Idiomas", "Language Library"), "https://language.biblioverse.org",
    ("Apps, canais e métodos para aprender idiomas.", "Apps, channels and methods for learning languages.")),
  P("inter", ("Biblioteca de Viagem", "Travel Library"), "https://travel.biblioverse.org",
    ("Ferramentas para planejar viagens e intercâmbio.", "Tools for planning trips and study abroad.")),

  # Pensamento crítico
  P("pens", ("Teste de Visão Moral", "Moral Outlook Test"), "https://ethicstest.biblioverse.org",
    ("Teste bilíngue que mapeia sua visão ética e moral.", "A bilingual quiz that maps your ethical and moral outlook.")),
  P("pens", ("Teste de Coerência", "Coherence Test"), "https://coherencetest.biblioverse.org",
    ("Teste sobre coerência lógica e contradições entre crenças e ações.", "A quiz on logical consistency and the gaps between beliefs and actions.")),
  P("pens", ("Novo Iluminismo", "Novo Iluminismo"), "https://medium.com/novo-iluminismo",
    ("Publicação no Medium sobre pensamento crítico e racionalidade moral.", "A Medium publication on critical thinking and moral reasoning (in Portuguese).")),
  P("pens", ("Veganismo-S", "Veganismo-S"), "https://medium.com/veganismo-s",
    ("Publicação no Medium sobre veganismo com base em evidências.", "A Medium publication on evidence-based veganism (in Portuguese).")),
  P("pens", ("Biblioteca de Racionalidade", "Rationality Library"), "https://thinking.biblioverse.org",
    ("Livros e recursos sobre pensamento crítico e vieses.", "Books and resources on critical thinking and cognitive biases.")),
  P("pens", ("Biblioteca de Filosofia", "Philosophy Library"), "https://philosophy.biblioverse.org",
    ("Correntes, autores e referências da filosofia.", "Schools of thought, thinkers and key references in philosophy.")),
  P("pens", ("Política Para Iniciantes", "Politics for Beginners"), "https://politicaparainiciantes.biblioverse.org",
    ("Conceitos e ideias políticas explicados para quem está começando.", "Political ideas and concepts explained for people just starting out."), "wip"),

  # Livros
  P("livro", ("Meu Mundo em Listas", "Meu Mundo em Listas"), None,
    ("Meu livro publicado, organizado em listas.", "My published book, told through lists (in Portuguese)."), tags=[T["pub"]]),
  P("livro", ("Veganismo Baseado em Evidências", "Veganismo Baseado em Evidências"), None,
    ("Racionalidade, especismo e vieses no movimento vegano.", "Evidence-based veganism: rationality, speciesism and biases in the vegan movement."), "writing"),
  P("livro", ("10 Anos Sem Matar Animais", "10 Anos Sem Matar Animais"), None,
    ("Memórias de uma década de veganismo.", "Ten years without killing animals: a memoir of a decade of veganism."), "writing"),

  # Curadoria
  P("cur", ("BiblioVerse", "BiblioVerse"), "https://biblioverse.org",
    ("A biblioteca de tudo: hub de bibliotecas temáticas com curadoria humana.", "The library of everything: a hub of themed libraries curated by real people.")),
  P("cur", ("Biblioteca de Redes Sociais", "Social Media Library"), "https://social.biblioverse.org",
    ("Plataformas, ferramentas e recursos para criadores.", "Platforms, tools and resources for creators.")),
  P("cur", ("Biblioteca de Listas", "Lists Library"), "https://list.biblioverse.org",
    ("As melhores listas e rankings, reunidos em um só lugar.", "The best lists and rankings, all in one place."), "wip"),

  # Guias e Diretórios
  P("guia", ("Brisbane Vegan Guide", "Brisbane Vegan Guide"), "https://brisbaneveganguide.com",
    ("Restaurantes e grupos veganos em Brisbane.", "Vegan restaurants and groups around Brisbane.")),
  P("guia", ("Brasileiros em Brisbane", "Brazilians in Brisbane"), "https://brasileirosembrisbane.biblioverse.org",
    ("Diretório para estudantes de intercâmbio e imigrantes em Brisbane.", "A directory for international students and migrants in Brisbane.")),
  P("guia", ("Brissy Op Shops", "Brissy Op Shops"), None,
    ("Guia para descobrir os brechós (op shops) de Brisbane.", "Your guide to finding Brisbane's best op shops."), "wip"),

  # Homenagens
  P("hom", ("Arli Prado", "Arli Prado"), "https://arliprado.com.br",
    ("Memorial em homenagem à minha mãe.", "A memorial for my mum.")),

  # Outros
  P("out", ("IV", "IV"), "https://inkvillains.tumblr.com",
    ("Tumblr de estética alternativa.", "A Tumblr of alternative aesthetics."), tags=[T["altaes"]]),
  P("out", ("BBIE", "BBIE"), "https://blackbeautyiseverywhere.tumblr.com",
    ("Tumblr que celebra a beleza negra em todo lugar.", "A Tumblr celebrating Black beauty everywhere."), tags=[T["aes"]]),
  P("out", ("Biblioteca de Programação", "Coding Library"), "https://code.biblioverse.org",
    ("Linguagens, cursos e ferramentas para aprender a programar.", "Languages, courses and tools for learning to code."), tags=[T["code"]]),
  P("out", ("Biblioteca de Games", "Gaming Library"), "https://games.biblioverse.org",
    ("Plataformas, jogos e o universo dos games.", "Platforms, games and all things gaming."), tags=[T["games"]]),
  P("out", ("Biblioteca de Música", "Music Library"), "https://music.biblioverse.org",
    ("Apps, gêneros, gravadoras e conceitos fundamentais da música.", "Apps, genres, record labels and music fundamentals."), "wip", [T["music"]]),
  P("out", ("My Music Taste", "My Music Taste"), "https://mymusictaste.biblioverse.org",
    ("Meus gostos musicais em forma de infográfico.", "My taste in music, as an infographic."), "wip", [T["music"]]),
  P("out", ("Biblioteca de Dados", "Data Library"), "https://data.biblioverse.org",
    ("Fontes de dados, visualização e análise.", "Data sources, visualisation and analysis."), "wip", [T["data"]]),
  P("out", ("Biblioteca de Web3", "Web3 Library"), "https://web3.biblioverse.org",
    ("Blockchain, carteiras e o ecossistema descentralizado.", "Blockchain, wallets and the decentralised ecosystem."), "wip", [T["web3"]]),
  P("out", ("Biblioteca de Organização", "Organisation Library"), "https://management.biblioverse.org",
    ("Apps e métodos de produtividade e gestão.", "Apps and methods for productivity and management."), "wip", [T["prod"]]),
  P("out", ("Biblioteca de Emprego", "Jobs Library"), "https://job.biblioverse.org",
    ("Sites de vagas, currículo e carreira.", "Job boards, resumes and career tips."), "wip", [T["career"]]),
  P("out", ("App de organização", "Organisation app"), None,
    ("Nome secreto. Um app para deixar a rotina mais organizada.", "Secret name. An app to make everyday life more organised."), "wip", [T["prod"]]),
  P("out", ("Teoria Musical", "Music Theory"), None,
    ("Nome secreto. Teoria musical explicada de um jeito novo.", "Secret name. Music theory explained in a fresh way."), "wip", [T["music"]]),
]

# ------------------------------------------------------------------
# CSS
# ------------------------------------------------------------------
CSS = r"""
/* Layout: light page, colored category tiles open each section, followed by a 5-column grid of compact rounded cards. */
:root{
  color-scheme:light;
  --bg:#F3F2F8; --surface:#FFFFFF; --ink:#16141F; --muted:#5E5B6E; --line:#E3E1EC;
  --c-design:#F2661B; --c-ia:#5B3FD1; --c-inter:#0E855C; --c-pens:#DB2877; --c-cur:#FFC21F;
  --c-hom:#8B3A62; --c-guia:#1463F3; --c-out:#3E4460; --c-livro:#C62F3A;
  --font-display:"Gabarito","Trebuchet MS",system-ui,sans-serif;
  --font-body:"Figtree",system-ui,-apple-system,"Segoe UI",sans-serif;
  --r-lg:32px; --r-md:20px; --r-sm:999px;
}
*{box-sizing:border-box}
[hidden]{display:none!important}
html{scroll-behavior:smooth; -webkit-text-size-adjust:100%}
img{max-width:100%}
body{
  margin:0; background:var(--bg); color:var(--ink);
  font-family:var(--font-body); font-size:16px; line-height:1.55;
  padding-left:max(16px, env(safe-area-inset-left, 0px));
  padding-right:max(16px, env(safe-area-inset-right, 0px));
  padding-block:0 48px;
}
a{color:inherit}
:focus-visible{outline:3px solid var(--c-ia); outline-offset:3px; border-radius:12px}
.sr-only{position:absolute!important; width:1px; height:1px; padding:0; margin:-1px; overflow:hidden; clip:rect(0,0,0,0); white-space:nowrap; border:0}
.skip{position:absolute; left:16px; top:-60px; z-index:20; background:var(--ink); color:var(--surface); padding:10px 16px; border-radius:var(--r-sm); font-weight:700; text-decoration:none}
.skip:focus{top:12px}
.wrap{max-width:1240px; margin:0 auto; display:flex; flex-direction:column; gap:20px}

/* Top bar */
.topbar{display:flex; justify-content:flex-end; padding-top:16px}
.lang{display:flex; padding:4px; gap:2px; background:var(--surface); border:1.5px solid var(--line); border-radius:var(--r-sm)}
.lang a{font:700 13px/1 var(--font-body); letter-spacing:.06em; text-decoration:none; padding:8px 12px; border-radius:var(--r-sm); color:var(--muted)}
.lang a[aria-current="true"]{background:var(--ink); color:var(--surface)}
.lang a:not([aria-current="true"]):hover{color:var(--ink)}

/* Hero */
.hero{display:grid; grid-template-columns:1.7fr 1fr; gap:16px}
.hero-main{
  background:var(--surface); border:1.5px solid var(--line);
  border-radius:var(--r-lg); padding:40px clamp(24px,4vw,48px) 0;
  display:grid; grid-template-columns:minmax(0,1fr) 260px; column-gap:24px;
  position:relative; overflow:hidden; min-width:0;
}
.intro{display:flex; flex-direction:column; gap:12px; padding-bottom:40px; min-width:0; container-type:inline-size}
.hello{font-weight:600; font-size:14px; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); margin:0}
.hero h1{font-family:var(--font-display); font-weight:900; font-size:34px; font-size:clamp(24px,7.4cqi,52px); line-height:1.05; margin:0; letter-spacing:-.02em; white-space:nowrap}
.caret{display:inline-block; width:.08em; height:.85em; background:var(--ink); margin-left:.04em; vertical-align:-.05em; animation:blink 1s steps(1) infinite}
.caret.done{animation:blink3 .8s linear 3 forwards}
@keyframes blink{50%{opacity:0}}
@keyframes blink3{0%,49%{opacity:1}50%,100%{opacity:0}}
.bio{margin:0; max-width:46ch; font-size:17px; color:var(--muted)}
.socials{display:flex; flex-wrap:wrap; gap:8px; margin-top:8px; padding:0; list-style:none}
.socials a{display:inline-block; text-decoration:none; font-weight:600; font-size:14px; padding:8px 16px; border-radius:var(--r-sm); border:1.5px solid var(--ink); background:var(--surface)}
.socials a:hover{background:var(--ink); color:var(--surface)}
.me{position:relative; align-self:end; height:290px; margin:0}
.me img{position:absolute; bottom:0; left:50%; transform:translateX(-50%); width:220px; height:auto; display:block}
.stats{list-style:none; margin:0; padding:0}
.stat{position:absolute; z-index:1; color:#fff; padding:8px 14px; border-radius:16px; font:600 13px/1.2 var(--font-body); box-shadow:0 6px 16px rgba(22,20,31,.18)}
.stat b{display:block; font:900 24px/1 var(--font-display); font-variant-numeric:tabular-nums}
.stat-1{background:var(--c-design); color:var(--ink); top:8px; left:0; transform:rotate(-6deg)}
.stat-2{background:var(--c-ia); top:96px; right:0; transform:rotate(5deg)}
.stat-3{background:var(--c-inter); bottom:36px; left:0; transform:rotate(-3deg)}

.hero-tiles{display:grid; grid-template-columns:1fr 1fr; gap:16px; margin:0; padding:0; list-style:none}
.tile{
  height:100%; border-radius:var(--r-md); padding:18px; color:#fff;
  display:flex; flex-direction:column; justify-content:space-between; gap:12px;
  min-height:120px; text-decoration:none;
  font-family:var(--font-display); font-weight:800; font-size:20px; line-height:1.05;
  transition:transform .2s ease;
}
.tile:hover{transform:translateY(-3px)}
.tile small{font-family:var(--font-body); font-weight:600; font-size:13px}
.tile.dark-text{color:var(--ink)}

/* Filter */
.filter{
  position:sticky; top:env(safe-area-inset-top, 0px); z-index:5;
  background:color-mix(in srgb, var(--bg) 88%, transparent);
  -webkit-backdrop-filter:blur(10px); backdrop-filter:blur(10px);
  margin-inline:-8px; padding:6px 8px;
  display:flex; flex-wrap:wrap; gap:6px;
}
body::before{content:""; position:fixed; inset:0 0 auto; height:env(safe-area-inset-top, 0px); z-index:10; background:var(--bg)}
.filter button{
  flex:none; font:600 14px var(--font-body); color:var(--ink);
  background:var(--surface); border:1.5px solid var(--line);
  padding:8px 14px; border-radius:var(--r-sm); cursor:pointer;
  display:flex; align-items:center; gap:7px;
}
.filter button i{width:9px; height:9px; border-radius:50%; background:var(--dot,var(--ink))}
.filter button[aria-pressed="true"]{background:var(--ink); color:var(--surface); border-color:var(--ink)}
@media (max-width:699px){
  .filter{
    flex-wrap:nowrap; overflow-x:auto; scrollbar-width:none; overscroll-behavior-x:contain; padding-right:32px;
    -webkit-mask-image:linear-gradient(to right,#000 calc(100% - 32px),transparent);
            mask-image:linear-gradient(to right,#000 calc(100% - 32px),transparent);
  }
  .filter::-webkit-scrollbar{display:none}
}

/* Sections */
#projetos{display:flex; flex-direction:column; gap:36px}
.section{display:flex; flex-direction:column; gap:20px; scroll-margin-top:var(--filter-h,72px)}
.sec-head{
  background:var(--c); color:#fff; border-radius:var(--r-lg);
  padding:22px clamp(22px,3.5vw,36px); min-height:112px;
  display:flex; justify-content:space-between; align-items:flex-end; gap:16px; flex-wrap:wrap;
}
.sec-head.dark-text{color:var(--ink)}
.sec-head > div{min-width:0}
.sec-head h2{font-family:var(--font-display); font-weight:900; margin:0; font-size:clamp(30px,4.6vw,52px); line-height:1; letter-spacing:-.015em; text-wrap:balance}
.sec-head p{margin:8px 0 0; max-width:52ch; font-size:16px}
.count{font-weight:700; font-size:14px; background:rgba(255,255,255,.22); padding:8px 14px; border-radius:var(--r-sm); font-variant-numeric:tabular-nums}
.sec-head.dark-text .count{background:rgba(22,20,31,.1)}

.grid{display:grid; grid-template-columns:repeat(5,minmax(0,1fr)); gap:14px; margin:0; padding:0; list-style:none}
@media (max-width:1100px){.grid{grid-template-columns:repeat(4,minmax(0,1fr))}}
@media (max-width:880px){.grid{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media (max-width:640px){.grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:420px){.grid{grid-template-columns:1fr}}
.grid > li{display:flex; min-width:0}
.card{
  flex:1; background:var(--surface); border-radius:var(--r-md);
  padding:18px; display:flex; flex-direction:column; gap:8px;
  border:1.5px solid var(--line); min-width:0; position:relative;
  transition:transform .2s ease, border-color .2s ease;
}
.card:hover{transform:translateY(-3px); border-color:var(--c)}
.tags{display:flex; flex-wrap:wrap; gap:6px}
.tag{font-size:11px; font-weight:700; letter-spacing:.04em; text-transform:uppercase; padding:4px 9px; border-radius:var(--r-sm); background:color-mix(in srgb, var(--c) 14%, var(--surface)); color:var(--ink)}
.tag.wip{background:transparent; border:1.5px dashed var(--muted); color:var(--muted); padding:3px 8px}
.card h3{margin:0; font-family:var(--font-display); font-weight:800; font-size:19px; line-height:1.15; overflow-wrap:anywhere}
.card h3 a{text-decoration:none}
.card h3 a::after{content:""; position:absolute; inset:0; border-radius:var(--r-md)}
.card h3 a:focus-visible{outline:none}
.card:has(a:focus-visible){outline:3px solid var(--c-ia); outline-offset:3px}
.card h3 .arrow{display:inline-block; transition:transform .2s ease; color:var(--c)}
.card:hover h3 .arrow{transform:translate(3px,-3px)}
.card p{margin:0; color:var(--muted); font-size:14.5px; line-height:1.5}
.card .url{margin-top:auto; padding-top:4px; font-size:12.5px; font-weight:600; color:var(--muted); overflow-wrap:anywhere}
.card.is-wip{background:transparent; border-style:dashed}

/* Invite + footer */
.invite{
  margin-top:28px; background:var(--c-cur); color:var(--ink); border-radius:var(--r-lg);
  padding:32px clamp(22px,4vw,48px); display:grid; grid-template-columns:minmax(0,1fr) auto; gap:20px 32px; align-items:end;
}
.invite h2{margin:0 0 8px; font:900 clamp(30px,4.4vw,48px)/1 var(--font-display); letter-spacing:-.015em}
.invite p{margin:0; max-width:58ch; font-size:17px}
.invite-actions{display:flex; flex-wrap:wrap; gap:10px}
.btn{display:inline-block; text-decoration:none; font-weight:700; font-size:15px; padding:12px 20px; border-radius:var(--r-sm); border:2px solid var(--ink)}
.btn-dark{background:var(--ink); color:#fff}
.btn-dark:hover{background:transparent; color:var(--ink)}
.btn-line{background:transparent}
.btn-line:hover{background:var(--ink); color:#fff}
footer{border-top:1.5px solid var(--line); padding-top:20px; margin-top:8px; display:flex; justify-content:space-between; flex-wrap:wrap; gap:12px; color:var(--muted); font-size:14px}

@media (max-width:1060px){
  .hero{grid-template-columns:1fr}
  .hero-tiles{grid-template-columns:repeat(4,minmax(0,1fr))}
}
@media (max-width:760px){ .invite{grid-template-columns:1fr} }
@media (max-width:680px){
  .hero-main{grid-template-columns:1fr; padding-top:28px}
  .intro{padding-bottom:8px}
  .me{width:100%; max-width:300px; justify-self:center; height:270px}
  .hero-tiles{grid-template-columns:1fr 1fr; gap:12px}
  .tile{min-height:96px; font-size:18px}
  .sec-head{padding:20px; min-height:0; border-radius:24px}
  .sec-head p{font-size:15px}
  .invite{border-radius:24px; padding:24px 20px}
}
@media (max-width:420px){
  .stat{padding:6px 10px; font-size:12px}
  .stat b{font-size:20px}
  .me{height:250px}
  .me img{width:200px}
}
@media (prefers-reduced-motion:reduce){
  html{scroll-behavior:auto}
  *{transition:none!important}
  .caret{animation:none}
}
""".strip()

# ------------------------------------------------------------------
# JS (filtros, atalhos, animação do nome, escolha de idioma)
# ------------------------------------------------------------------
JS = r"""
(function(){
  var filter = document.getElementById("filter");
  var sections = document.getElementById("projetos");

  function setFilterH(){ document.documentElement.style.setProperty("--filter-h", (filter.offsetHeight + 12) + "px"); }
  setFilterH();
  window.addEventListener("resize", setFilterH);

  function applyFilter(f, target){
    filter.querySelectorAll("button").forEach(function(b){ b.setAttribute("aria-pressed", b.dataset.f === f ? "true" : "false"); });
    sections.querySelectorAll(".section").forEach(function(s){ s.hidden = f !== "all" && s.dataset.cat !== f; });
    var active = filter.querySelector('[data-f="' + f + '"]');
    if(active && filter.scrollWidth > filter.clientWidth){
      filter.scrollLeft = active.offsetLeft - filter.clientWidth / 2 + active.offsetWidth / 2;
    }
    var el = target || sections;
    var top = el.getBoundingClientRect().top + window.scrollY - filter.offsetHeight - 8;
    if(target || window.scrollY > top) window.scrollTo({ top: top, behavior: "smooth" });
  }

  filter.addEventListener("click", function(e){
    var b = e.target.closest("button"); if(!b) return;
    applyFilter(b.dataset.f);
  });

  document.getElementById("atalhos").addEventListener("click", function(e){
    var a = e.target.closest("a[data-f]"); if(!a) return;
    e.preventDefault();
    var t = document.getElementById(a.dataset.f);
    applyFilter("all", t);
    if(history.replaceState) history.replaceState(null, "", "#" + a.dataset.f);
  });

  // Guarda a escolha de idioma quando a pessoa usa o seletor
  document.querySelectorAll(".lang a[hreflang]").forEach(function(a){
    a.addEventListener("click", function(){
      try { localStorage.setItem("jcp-lang", a.dataset.lang); } catch(err){}
    });
  });

  // Animação do nome: "Prado da Silva" vira "Prava"
  var el = document.getElementById("name"), caret = document.getElementById("caret");
  var FULL = "Julio Cesar Prado da Silva", KEEP = "Julio Cesar Pra", FINAL = "Julio Cesar Prava";
  // Ajusta o tamanho para o nome completo caber em uma linha, sem pular de linha na animação
  var h1 = el.parentNode;
  function fit(){
    h1.style.fontSize = "";
    var probe = document.createElement("span");
    probe.style.cssText = "position:absolute;visibility:hidden;white-space:nowrap";
    probe.textContent = FULL;
    h1.appendChild(probe);
    var w = probe.getBoundingClientRect().width, avail = h1.clientWidth;
    if(w > avail){ h1.style.fontSize = Math.floor(parseFloat(getComputedStyle(h1).fontSize) * avail / w * 0.98) + "px"; }
    h1.removeChild(probe);
  }
  fit();
  if(document.fonts && document.fonts.ready) document.fonts.ready.then(fit);
  window.addEventListener("resize", fit);
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if(reduce){ el.textContent = FINAL; caret.hidden = true; return; }
  var text = FULL;
  function step(fn, ms){ setTimeout(fn, ms); }
  function erase(){
    if(text.length > KEEP.length){ text = text.slice(0, -1); el.textContent = text; step(erase, 70); }
    else step(type, 350);
  }
  function type(){
    if(text.length < FINAL.length){ text = FINAL.slice(0, text.length + 1); el.textContent = text; step(type, 140); }
    else {
      caret.addEventListener("animationend", function(){ caret.hidden = true; }, { once: true });
      caret.classList.add("done");
    }
  }
  step(erase, 1400);
})();
""".strip()

# Detecta o idioma do aparelho no primeiro acesso (roda antes da página aparecer)
def lang_detect_script(page_lang, other_href):
    return (
      "<script>(function(){try{var k='jcp-lang',s=localStorage;s.setItem('jcp-t','1');s.removeItem('jcp-t');"
      "if(/bot|crawl|spider|slurp|lighthouse|preview|headless/i.test(navigator.userAgent))return;"
      "var p=s.getItem(k);if(!p){var l=((navigator.languages&&navigator.languages[0])||navigator.language||'').toLowerCase();"
      "p=l.indexOf('pt')===0?'pt':'en';s.setItem(k,p);}"
      f"if(p!=='{page_lang}')location.replace('{other_href}'+location.hash);"
      "}catch(e){}})();</script>"
    )

# ------------------------------------------------------------------
# RENDER
# ------------------------------------------------------------------
e = lambda s: html.escape(s, quote=True)

def fmt_date(d, lang):
    m = UI[lang]["months"][d.month - 1]
    return f"{d.day} de {m} de {d.year}" if lang == "pt" else f"{d.day} {m} {d.year}"

def ordered(cat_id):
    items = [p for p in PROJECTS if p["cat"] == cat_id]
    return sorted(items, key=lambda p: (p["status"] is not None, PROJECTS.index(p)))

def host(url):
    return url.split("//", 1)[1].split("/", 1)[0].removeprefix("www.")

def li(i, lang):  # índice do idioma nas tuplas
    return 0 if lang == "pt" else 1

def render_card(p, lang):
    u = UI[lang]; k = li(None, lang)
    name, desc = p["name"][k], p["desc"][k]
    chips = "".join(f'<span class="tag">{e(t[k])}</span>' for t in p["tags"])
    if p["status"] == "wip": chips += f'<span class="tag wip">{e(u["wip"])}</span>'
    if p["status"] == "writing": chips += f'<span class="tag wip">{e(u["writing"])}</span>'
    if p["url"]:
        title = f'<a href="{e(p["url"])}" target="_blank" rel="noopener">{e(name)} <span class="arrow" aria-hidden="true">↗</span></a>'
        url = f'<span class="url">{e(host(p["url"]))}</span>'
    else:
        title, url = e(name), ""
    cls = "card is-wip" if p["status"] else "card"
    tags = f'<div class="tags">{chips}</div>' if chips else ""
    return f'<li><article class="{cls}">{tags}<h3>{title}</h3><p>{e(desc)}</p>{url}</article></li>'

def count_label(n, lang):
    u = UI[lang]
    return f'{n} {u["project_one"] if n == 1 else u["project_many"]}'

def render_body(lang, links):
    u = UI[lang]; k = li(None, lang)
    pt_cur = "true" if lang == "pt" else "false"
    en_cur = "true" if lang == "en" else "false"
    socials = "".join(f'<li><a href="{e(h)}" target="_blank" rel="noopener me">{e(n)}</a></li>' for n, h in SOCIALS)
    stats = "".join(f'<li class="stat stat-{i+1}"><b>{e(a)}</b>{e(b)}</li>' for i, (a, b) in enumerate(u["stats"]))
    tiles = "".join(
        f'<li><a class="tile{" dark-text" if c.get("dark") else ""}" href="#{c["id"]}" data-f="{c["id"]}" style="background:var({c["color"]})">'
        f'{e(c[lang][0])}<small>{count_label(len(ordered(c["id"])), lang)}</small></a></li>'
        for c in CATEGORIES[:4])
    chips = f'<button type="button" data-f="all" aria-pressed="true">{e(u["all"])}</button>' + "".join(
        f'<button type="button" data-f="{c["id"]}" aria-pressed="false" aria-controls="{c["id"]}" style="--dot:var({c["color"]})"'
        + (f' title="{e(c[lang][0])}"' if c[lang][1] else "")
        + f'><i aria-hidden="true"></i>{e(c[lang][1] or c[lang][0])}</button>'
        for c in CATEGORIES)
    secs = []
    for c in CATEGORIES:
        items = ordered(c["id"])
        if not items: continue
        dark = " dark-text" if c.get("dark") else ""
        secs.append(
          f'<section class="section" id="{c["id"]}" data-cat="{c["id"]}" style="--c:var({c["color"]})" aria-labelledby="h-{c["id"]}">'
          f'<div class="sec-head{dark}"><div><h2 id="h-{c["id"]}">{e(c[lang][0])}</h2><p>{e(c[lang][2])}</p></div>'
          f'<span class="count">{count_label(len(items), lang)}</span></div>'
          f'<ul class="grid">{"".join(render_card(p, lang) for p in items)}</ul></section>')
    d = LAST_UPDATED
    return f"""<a class="skip" href="#projetos">{e(u["skip"])}</a>
<div class="wrap">
  <div class="topbar">
    <nav class="lang" aria-label="{e(u["lang_label"])}">
      <a href="{links["pt"]}" hreflang="pt-BR" lang="pt-BR" data-lang="pt" aria-current="{pt_cur}">PT</a>
      <a href="{links["en"]}" hreflang="en-AU" lang="en-AU" data-lang="en" aria-current="{en_cur}">EN</a>
    </nav>
  </div>
  <header class="hero">
    <div class="hero-main">
      <div class="intro">
        <p class="hello">{e(u["hello"])}</p>
        <h1><span class="sr-only">Julio Cesar Prava</span><span id="name" aria-hidden="true">Julio Cesar Prado da Silva</span><span class="caret" id="caret" aria-hidden="true"></span></h1>
        <p class="bio">{e(u["bio"])}</p>
        <ul class="socials" aria-label="{e(u["socials"])}">{socials}</ul>
      </div>
      <figure class="me">
        <img src="{links["img"]}avatar.webp" alt="{e(u["avatar_alt"])}" width="444" height="520" fetchpriority="high" decoding="async">
        <ul class="stats">{stats}</ul>
      </figure>
    </div>
    <ul class="hero-tiles" id="atalhos" aria-label="{e(u["shortcuts"])}">{tiles}</ul>
  </header>
  <nav class="filter" id="filter" aria-label="{e(u["filter_label"])}">{chips}</nav>
  <main id="projetos">{"".join(secs)}</main>
  <section class="invite" aria-labelledby="h-invite">
    <div><h2 id="h-invite">{e(u["invite_title"])}</h2><p>{e(u["invite_text"])}</p></div>
    <div class="invite-actions">
      <a class="btn btn-dark" href="https://instagram.com/sencientista" target="_blank" rel="noopener">{e(u["invite_ig"])}</a>
      <a class="btn btn-line" href="https://linkedin.com/in/juliocesarprava" target="_blank" rel="noopener">{e(u["invite_li"])}</a>
    </div>
  </section>
  <footer>
    <span>Julio Cesar Prava · {e(u["place"])}</span>
    <span>{e(u["updated"])}: <time datetime="{d.isoformat()}">{fmt_date(d, lang)}</time></span>
  </footer>
</div>
<script>{JS}</script>"""

def json_ld(lang, url):
    u = UI[lang]
    data = {
      "@context": "https://schema.org",
      "@type": "ProfilePage",
      "url": url,
      "name": u["seo_title"],
      "description": u["seo_desc"],
      "inLanguage": u["html_lang"],
      "dateModified": LAST_UPDATED.isoformat(),
      "mainEntity": {
        "@type": "Person",
        "@id": SITE_URL + "/#julio",
        "name": "Julio Cesar Prava",
        "alternateName": "Julio Cesar Prado da Silva",
        "jobTitle": u["job"],
        "image": SITE_URL + "/og-image.png",
        "url": SITE_URL + "/",
        "homeLocation": {"@type": "Place", "name": "Brisbane, Queensland, Australia"},
        "nationality": {"@type": "Country", "name": "Brazil"},
        "knowsLanguage": ["pt-BR", "en"],
        "knowsAbout": ["Graphic design", "Prepress", "Artificial intelligence", "Critical thinking", "Veganism", "Study abroad in Australia"],
        "sameAs": SAME_AS,
      },
    }
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + "</script>"

FONTS = '''<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Gabarito:wght@800;900&family=Figtree:wght@400;600;700&display=swap">'''

def page_github(lang):
    u = UI[lang]
    url = SITE_URL + ("/" if lang == "pt" else "/en/")
    links = {"pt": "/", "en": "/en/", "img": "/"}
    other = "/en/" if lang == "pt" else "/"
    return f"""<!doctype html>
<html lang="{u["html_lang"]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(u["seo_title"])}</title>
<meta name="description" content="{e(u["seo_desc"])}">
<meta name="author" content="Julio Cesar Prava">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="theme-color" content="#F3F2F8">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="pt-BR" href="{SITE_URL}/">
<link rel="alternate" hreflang="en-AU" href="{SITE_URL}/en/">
<link rel="alternate" hreflang="en" href="{SITE_URL}/en/">
<link rel="alternate" hreflang="x-default" href="{SITE_URL}/">
<link rel="icon" href="/favicon.png" type="image/png" sizes="64x64">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:type" content="profile">
<meta property="og:site_name" content="Julio Cesar Prava">
<meta property="og:title" content="{e(u["seo_title"])}">
<meta property="og:description" content="{e(u["seo_desc"])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE_URL}/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Julio Cesar Prava">
<meta property="og:locale" content="{u["og_locale"]}">
<meta property="og:locale:alternate" content="{UI["en" if lang == "pt" else "pt"]["og_locale"]}">
<meta property="profile:first_name" content="Julio Cesar">
<meta property="profile:last_name" content="Prava">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(u["seo_title"])}">
<meta name="twitter:description" content="{e(u["seo_desc"])}">
<meta name="twitter:image" content="{SITE_URL}/og-image.png">
{lang_detect_script(lang, other)}
{FONTS}
<style>
{CSS}
</style>
{json_ld(lang, url)}
</head>
<body>
{render_body(lang, links)}
</body>
</html>
"""

def page_preview(lang):
    # Pré-visualização no Claude: a página PT é envolvida pelo próprio visualizador; a EN é um arquivo à parte
    if lang == "pt":
        links = {"pt": "index.html", "en": "en/index.html", "img": ""}
        return f"""<title>Julio Cesar Prava</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="description" content="{e(UI["pt"]["seo_desc"])}">
{lang_detect_script("pt", "en/index.html")}
{FONTS}
<style>
{CSS}
</style>
{render_body("pt", links)}
"""
    links = {"pt": "../index.html", "en": "index.html", "img": "../"}
    return f"""<!doctype html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Julio Cesar Prava</title>
{lang_detect_script("en", "../index.html")}
{FONTS}
<style>
{CSS}
</style>
</head>
<body>
{render_body("en", links)}
</body>
</html>
"""

def page_404():
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Página não encontrada · Julio Cesar Prava</title>
<meta name="robots" content="noindex">
<link rel="icon" href="/favicon.png" type="image/png">
{FONTS}
<style>
{CSS}
.nf{{min-height:80vh; display:grid; place-items:center; text-align:center}}
.nf h1{{font:900 clamp(40px,8vw,88px)/1 var(--font-display); margin:0 0 12px}}
.nf p{{color:var(--muted); margin:0 0 24px}}
</style>
</head>
<body>
<main class="nf"><div>
<h1>404</h1>
<p>Esta página não existe. <span lang="en-AU">This page doesn't exist.</span></p>
<p><a class="btn btn-dark" href="/">Ver projetos</a> <a class="btn btn-line" href="/en/" lang="en-AU">See projects</a></p>
</div></main>
</body>
</html>
"""

def sitemap():
    d = LAST_UPDATED.isoformat()
    alt = (f'<xhtml:link rel="alternate" hreflang="pt-BR" href="{SITE_URL}/"/>'
           f'<xhtml:link rel="alternate" hreflang="en-AU" href="{SITE_URL}/en/"/>'
           f'<xhtml:link rel="alternate" hreflang="x-default" href="{SITE_URL}/"/>')
    urls = "".join(f"<url><loc>{SITE_URL}{p}</loc><lastmod>{d}</lastmod>{alt}</url>" for p in ("/", "/en/"))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">'
            f"{urls}</urlset>\n")

# ------------------------------------------------------------------
# IMAGENS (compartilhamento e ícones), geradas a partir do avatar
# ------------------------------------------------------------------
def make_images(out):
    from PIL import Image, ImageDraw, ImageFont
    av = Image.open(os.path.join(ROOT, "assets", "avatar.webp")).convert("RGBA")
    bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    reg = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

    og = Image.new("RGB", (1200, 630), "#F3F2F8")
    d = ImageDraw.Draw(og)
    d.rounded_rectangle((40, 40, 1160, 590), 48, fill="#FFFFFF", outline="#E3E1EC", width=3)
    d.text((100, 120), "G'DAY, EU SOU", font=ImageFont.truetype(bold, 28), fill="#5E5B6E")
    d.text((96, 165), "Julio Cesar", font=ImageFont.truetype(bold, 84), fill="#16141F")
    d.text((96, 260), "Prava", font=ImageFont.truetype(bold, 84), fill="#16141F")
    d.text((100, 380), "Design · IA · Intercâmbio · Livros", font=ImageFont.truetype(reg, 30), fill="#5E5B6E")
    colors = ["#F2661B", "#5B3FD1", "#0E855C", "#DB2877", "#C62F3A", "#FFC21F", "#1463F3"]
    for i, c in enumerate(colors):
        d.rounded_rectangle((100 + i * 62, 460, 148 + i * 62, 508), 14, fill=c)
    a = av.copy(); a.thumbnail((440, 516))
    og.paste(a, (1160 - a.width - 40, 590 - a.height), a)
    og.save(os.path.join(out, "og-image.png"), optimize=True)

    # Ícones: rosto do avatar sobre amarelo
    face = av.crop((40, 0, av.width - 40, av.width - 80))
    for size, name in ((64, "favicon.png"), (180, "apple-touch-icon.png")):
        bg = Image.new("RGBA", (size, size), "#FFC21F")
        f = face.copy(); f.thumbnail((int(size * .92), int(size * .92)))
        bg.paste(f, ((size - f.width) // 2, size - f.height), f)
        bg.convert("RGB").save(os.path.join(out, name), optimize=True)

# ------------------------------------------------------------------
def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f: f.write(text)

def main():
    in_repo = os.path.basename(ROOT) == "_fonte"
    dist = os.path.dirname(ROOT) if in_repo else os.path.join(ROOT, "dist")
    prev = os.path.join(ROOT, "preview")
    shutil.rmtree(prev, ignore_errors=True); os.makedirs(prev)
    if not in_repo:
        shutil.rmtree(dist, ignore_errors=True); os.makedirs(dist)
    write(os.path.join(dist, "index.html"), page_github("pt"))
    write(os.path.join(dist, "en", "index.html"), page_github("en"))
    write(os.path.join(dist, "404.html"), page_404())
    write(os.path.join(dist, "sitemap.xml"), sitemap())
    write(os.path.join(dist, "robots.txt"), f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n")
    write(os.path.join(dist, "CNAME"), "meusprojetos.biblioverse.org\n")
    shutil.copy(os.path.join(ROOT, "assets", "avatar.webp"), dist)
    make_images(dist)
    write(os.path.join(prev, "index.html"), page_preview("pt"))
    write(os.path.join(prev, "en", "index.html"), page_preview("en"))
    shutil.copy(os.path.join(ROOT, "assets", "avatar.webp"), prev)
    with open(os.path.join(ROOT, "check.js"), "w") as f: f.write(JS)
    print("ok:", dist)

if __name__ == "__main__":
    main()
