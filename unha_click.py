import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
import hashlib
from datetime import datetime, date, timedelta
import qrcode
import io
import base64

def gerar_hash(texto):
    return hashlib.sha256(texto.encode()).hexdigest()

HASH_ADMIN = gerar_hash("admin" + str(123))
HASH_DEMO = gerar_hash(str(1) + str(2) + str(3) + str(4))
COMISSAO = 0.20
DIAS_RECEBER = 2
TEMPO_ACEITE_HORAS = 1
CHAVE_PIX_DONO = "11999999999"

st.set_page_config(page_title="Unha Click", page_icon="UC", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* {font-family: 'Inter', sans-serif !important;}
:root {--bg: #FAFAFA; --card: #FFFFFF; --text: #1A1A2E; --muted: #6B7280; --light: #9CA3AF; --border: #F0F0F0; --accent: #C48B9F; --gold: #B8860B; --gold-bg: #FFF8E7; --green: #10B981; --blue: #6366F1;}
.stApp {background-color: var(--bg) !important;}
.marca {text-align:center; padding:60px 0 20px 0;}
.marca h1 {font-size:32px; font-weight:800; color:var(--text); letter-spacing:-1px; margin:0;}
.marca p {font-size:13px; color:var(--light); letter-spacing:2px; text-transform:uppercase; margin:6px 0 0 0; font-weight:400;}
.header {background:var(--card); padding:36px 24px 28px 24px; border-bottom:1px solid var(--border); margin:-6rem -1rem 2rem -1rem;}
.header h1 {color:var(--text) !important; font-size:26px !important; margin:0 !important; font-weight:800 !important; letter-spacing:-0.5px;}
.header p {color:var(--muted) !important; font-size:14px !important; margin:6px 0 0 0 !important; font-weight:400;}
.header-dark {background:var(--text); padding:36px 24px 28px 24px; margin:-6rem -1rem 2rem -1rem;}
.header-dark h1 {color:white !important; font-size:26px !important; margin:0 !important; font-weight:800 !important;}
.header-dark p {color:var(--light) !important; font-size:14px !important; margin:6px 0 0 0 !important;}
.card {background:var(--card); border-radius:16px; padding:20px; margin:10px 0; border:1px solid var(--border); transition:all 0.2s;}
.card:hover {border-color:var(--accent); box-shadow:0 4px 12px rgba(196,139,159,0.06);}
.card-gold {background:var(--gold-bg); border-radius:16px; padding:20px; margin:10px 0; border:1px solid rgba(184,134,11,0.12);}
.kpi {background:var(--card); border-radius:16px; padding:20px; text-align:center; border:1px solid var(--border);}
.kpi-v {font-size:28px; font-weight:800; margin:6px 0 2px 0; letter-spacing:-1px;}
.kpi-l {font-size:11px; color:var(--light); font-weight:600; text-transform:uppercase; letter-spacing:0.5px;}
.tag {display:inline-block; padding:3px 10px; border-radius:6px; font-size:11px; font-weight:600; letter-spacing:0.2px;}
.tag-pendente {background:#FEF3C7; color:#92400E;}
.tag-confirmado {background:#D1FAE5; color:#065F46;}
.tag-concluido {background:#DBEAFE; color:#1E40AF;}
.tag-cancelado {background:#FEE2E2; color:#991B1B;}
.tag-aguardando {background:#EDE9FE; color:#5B21B6;}
.tag-pago {background:#D1FAE5; color:#065F46;}
.stars {color:var(--gold); font-size:13px; letter-spacing:1px;}
.av {width:44px; height:44px; border-radius:12px; display:flex; align-items:center; justify-content:center; font-size:17px; font-weight:700; color:white;}
.sep {height:1px; background:var(--border); margin:20px 0;}
.stitle {font-size:12px; font-weight:700; color:var(--light); text-transform:uppercase; letter-spacing:0.8px; margin:28px 0 14px 0;}
.stButton > button {border-radius:12px !important; font-weight:600 !important; padding:10px 20px !important; font-size:13px !important; transition:all 0.15s !important;}
.stButton > button:hover {transform:translateY(-1px) !important;}
.stButton > button[data-testid="baseButton-primary"] {background:#1A1A2E !important; color:white !important; border:none !important;}
div[data-testid="stTextInput"] > div > div > input {border-radius:12px !important; border:1.5px solid var(--border) !important; padding:12px 16px !important; font-size:14px !important;}
div[data-testid="stTextInput"] > div > div > input:focus {border-color:var(--accent) !important; box-shadow:0 0 0 3px rgba(196,139,159,0.06) !important;}
.demo-box {background:#F9FAFB; border-radius:12px; padding:14px; margin-top:36px; border:1px solid var(--border); text-align:center;}
.demo-box p {margin:0; font-size:12px; color:var(--muted); line-height:1.8;}
.demo-box .label {font-size:10px; color:var(--light); font-weight:600; letter-spacing:0.5px; text-transform:uppercase; margin-bottom:6px;}
</style>""", unsafe_allow_html=True)

def get_conn():
    db = st.secrets["database"]
    return psycopg2.connect(host=db["host"], port=db["port"], dbname=db["dbname"], user=db["user"], password=db["password"], cursor_factory=RealDictCursor)

def query(sql, params=None):
    try:
        c = get_conn(); cur = c.cursor(); cur.execute(sql, params); r = cur.fetchall(); c.commit(); cur.close(); c.close(); return r
    except Exception as e:
        st.error(f"Erro no banco: {e}"); return []

def execute(sql, params=None):
    try:
        c = get_conn(); cur = c.cursor(); cur.execute(sql, params); c.commit(); cur.close(); c.close()
    except Exception as e:
        st.error(f"Erro no banco: {e}")

def execute_ret(sql, params=None):
    try:
        c = get_conn(); cur = c.cursor(); cur.execute(sql, params); r = cur.fetchone(); c.commit(); cur.close(); c.close(); return r
    except Exception as e:
        st.error(f"Erro no banco: {e}"); return None

def ir(tela, **kw):
    st.session_state.tela = tela
    for k, v in kw.items(): st.session_state[k] = v

def sair():
    for k in list(st.session_state.keys()): del st.session_state[k]

def estrelas(n):
    n = int(n or 5)
    return "\u2605" * n + "\u2606" * (5 - n)

def tag_st(status):
    nm = {"pendente":"Pendente","confirmado":"Confirmado","concluido":"Conclu\u00eddo","cancelado":"Cancelado","aguardando_aceite":"Aguardando"}
    cs = status.replace("aguardando_aceite","aguardando")
    return '<span class="tag tag-' + cs + '">' + nm.get(status,status) + '</span>'

def nome_pg(fp):
    nm = {"pix":"PIX","cartao_credito":"Cart\u00e3o de Cr\u00e9dito","cartao_debito":"Cart\u00e3o de D\u00e9bito","dinheiro":"Dinheiro"}
    return nm.get(fp,fp)

def gerar_pix_qrcode(valor, descricao="Unha Click"):
    payload = f"00020126580014br.gov.bcb.pix0136{CHAVE_PIX_DONO}520400005303986540{valor:.2f}5802BR5913UNHA CLICK6009SAO PAULO62070503***6304"
    img = qrcode.make(payload)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    return b64

@st.cache_resource
def init_db():
    try:
        c = get_conn(); cur = c.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS usuarios (id SERIAL PRIMARY KEY, nome TEXT NOT NULL, telefone TEXT UNIQUE NOT NULL, email TEXT, senha TEXT NOT NULL, tipo TEXT DEFAULT 'cliente', endereco TEXT, bairro TEXT, cidade TEXT, estado TEXT DEFAULT 'SP', avaliacao_media REAL DEFAULT 5.0, total_avaliacoes INTEGER DEFAULT 0, especialidades TEXT, bio TEXT, chave_pix TEXT, ativo INTEGER DEFAULT 1, data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        cur.execute("""CREATE TABLE IF NOT EXISTS servicos (id SERIAL PRIMARY KEY, nome TEXT NOT NULL, descricao TEXT, preco REAL NOT NULL, duracao_min INTEGER DEFAULT 60, categoria TEXT DEFAULT 'maos', ativo INTEGER DEFAULT 1)""")
        cur.execute("""CREATE TABLE IF NOT EXISTS agendamentos (id SERIAL PRIMARY KEY, cliente_id INTEGER REFERENCES usuarios(id), manicure_id INTEGER, servico_id INTEGER REFERENCES servicos(id), data TEXT, horario TEXT, endereco_atendimento TEXT, complemento TEXT, valor_total REAL, valor_manicure REAL, valor_comissao REAL, status TEXT DEFAULT 'pendente', forma_pagamento TEXT DEFAULT 'pix', observacoes TEXT, data_liberacao_manicure TEXT, pago INTEGER DEFAULT 0, avaliacao_nota INTEGER, avaliacao_comentario TEXT, data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        cur.execute("""CREATE TABLE IF NOT EXISTS disponibilidade (id SERIAL PRIMARY KEY, manicure_id INTEGER, dia_semana INTEGER, hora_inicio TEXT DEFAULT '08:00', hora_fim TEXT DEFAULT '18:00', ativo INTEGER DEFAULT 1)""")
        cur.execute("""CREATE TABLE IF NOT EXISTS notificacoes (id SERIAL PRIMARY KEY, usuario_id INTEGER, titulo TEXT, mensagem TEXT, tipo TEXT DEFAULT 'info', lida INTEGER DEFAULT 0, data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        cur.execute("""CREATE TABLE IF NOT EXISTS transacoes (id SERIAL PRIMARY KEY, agendamento_id INTEGER, tipo TEXT, valor REAL, destinatario_id INTEGER, forma_pagamento TEXT, status TEXT DEFAULT 'pendente', data_prevista_liberacao TEXT, data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        cur.execute("""CREATE TABLE IF NOT EXISTS favoritas (id SERIAL PRIMARY KEY, cliente_id INTEGER, manicure_id INTEGER, UNIQUE(cliente_id, manicure_id))""")
        c.commit()
        cur.execute("DELETE FROM disponibilidade"); cur.execute("DELETE FROM transacoes"); cur.execute("DELETE FROM notificacoes"); cur.execute("DELETE FROM favoritas"); cur.execute("DELETE FROM agendamentos"); cur.execute("DELETE FROM servicos"); cur.execute("DELETE FROM usuarios"); c.commit()
        for srv in [("Esmalta\u00e7\u00e3o Simples","Acabamento cl\u00e1ssico e impec\u00e1vel",35.0,40,"maos"),("Esmalta\u00e7\u00e3o em Gel","Gel importado de longa dura\u00e7\u00e3o",60.0,50,"maos"),("Unha Decorada","Nail art exclusiva e personalizada",80.0,70,"maos"),("Francesinha","Cl\u00e1ssica e sofisticada",45.0,50,"maos"),("Alongamento Fibra","Fibra de vidro premium",120.0,90,"maos"),("Pedicure Completa","Hidrata\u00e7\u00e3o profunda + esmalta\u00e7\u00e3o",50.0,60,"pes"),("Spa dos P\u00e9s","Esfoliacao + hidrata\u00e7\u00e3o + massagem",70.0,75,"pes"),("Combo M\u00e3os + P\u00e9s","Esmalta\u00e7\u00e3o completa",75.0,90,"combo"),("Combo VIP","Gel + Spa + Hidrata\u00e7\u00e3o completa",130.0,120,"combo"),("Combo Noiva","Pacote exclusivo para noivas",200.0,150,"combo")]:
            cur.execute("INSERT INTO servicos (nome,descricao,preco,duracao_min,categoria) VALUES (%s,%s,%s,%s,%s)", srv)
        cur.execute("INSERT INTO usuarios (nome,telefone,email,senha,tipo) VALUES (%s,%s,%s,%s,%s)", ("Fernando Jr","11999999999","fernando@unhaclick.com",HASH_ADMIN,"admin"))
        cur.execute("INSERT INTO usuarios (nome,telefone,email,senha,tipo,especialidades,bio,chave_pix) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id", ("Camila Oliveira","11988887777","camila@unhaclick.com",HASH_DEMO,"manicure","Gel, Fibra, Decora\u00e7\u00e3o, Francesinha","Especialista em nail art h\u00e1 5 anos. Atendimento premium.","11988887777"))
        mid = cur.fetchone()["id"]
        for dia in range(0, 6):
            cur.execute("INSERT INTO disponibilidade (manicure_id,dia_semana,hora_inicio,hora_fim) VALUES (%s,%s,%s,%s)", (mid, dia, "08:00", "18:00"))
        cur.execute("INSERT INTO usuarios (nome,telefone,email,senha,tipo,endereco,bairro,cidade) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", ("Maria Santos","11977776666","maria@demo.com",HASH_DEMO,"cliente","Rua das Flores, [CREDIT_DEBIT_CARD_CVV]","Centro","S\u00e3o Paulo"))
        c.commit(); cur.close(); c.close(); return True
    except Exception as e:
        return False

init_db()

def tela_login():
    st.markdown('<div class="marca"><h1>unha click</h1><p>beleza sob demanda</p></div>', unsafe_allow_html=True)
    st.markdown("")
    tel = st.text_input("Telefone", placeholder="11999999999")
    senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")
    st.markdown("")
    c1, c2 = st.columns(2)
    with c1:
        btn = st.button("Entrar", use_container_width=True, type="primary")
    with c2:
        if st.button("Criar conta", use_container_width=True):
            ir("cadastro"); st.rerun()
    if btn:
        if not tel or not senha:
            st.error("Preencha todos os campos."); return
        h = gerar_hash(senha)
        r = query("SELECT * FROM usuarios WHERE telefone=%s AND senha=%s AND ativo=1", (tel, h))
        if r:
            u = r
            st.session_state.user_id = u["id"]
            st.session_state.user_nome = u["nome"]
            st.session_state.user_tipo = u["tipo"]
            destino = {"admin":"admin","manicure":"manicure_home"}.get(u["tipo"], "cliente_home")
            ir(destino); st.rerun()
        else:
            st.error("Telefone ou senha incorretos.")
    st.markdown('<div class="demo-box"><p class="label">Contas demo</p><p>Admin: 11999999999 / admin[CREDIT_DEBIT_CARD_CVV]<br>Profissional: 11988887777 / [CREDIT_DEBIT_CARD_CVV]4<br>Cliente: 11977776666 / [CREDIT_DEBIT_CARD_CVV]4</p></div>', unsafe_allow_html=True)

def tela_cadastro():
    st.markdown('<div class="header"><h1>Criar conta</h1><p>Junte-se ao Unha Click</p></div>', unsafe_allow_html=True)
    if st.button("Voltar"): ir("login"); st.rerun()
    nome = st.text_input("Nome completo")
    tel = st.text_input("Telefone")
    email = st.text_input("E-mail (opcional)")
    senha = st.text_input("Senha", type="password")
    senha2 = st.text_input("Confirmar senha", type="password")
    tipo = st.radio("Voc\u00ea \u00e9:", ["Cliente", "Profissional"], horizontal=True)
    if st.button("Criar minha conta", use_container_width=True, type="primary"):
        if not nome or not tel or not senha:
            st.error("Preencha nome, telefone e senha."); return
        if senha != senha2:
            st.error("As senhas n\u00e3o conferem."); return
        tipo_db = "cliente" if tipo == "Cliente" else "manicure"
        h = gerar_hash(senha)
        try:
            execute("INSERT INTO usuarios (nome,telefone,email,senha,tipo) VALUES (%s,%s,%s,%s,%s)", (nome, tel, email, h, tipo_db))
            st.success("Conta criada! Fa\u00e7a login."); ir("login"); st.rerun()
        except:
            st.error("Telefone j\u00e1 cadastrado.")

def tela_cliente_home():
    p = st.session_state.user_nome.split()
    pri = p.pop(0) if p else st.session_state.user_nome
    st.markdown('<div class="header"><h1>Ol\u00e1, ' + pri + '</h1><p>O que vamos fazer hoje?</p></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Agendamentos", use_container_width=True): ir("meus_agendamentos"); st.rerun()
    with c2:
        if st.button("Meu perfil", use_container_width=True): ir("perfil"); st.rerun()
    with c3:
        if st.button("Sair", use_container_width=True): sair(); st.rerun()
    st.markdown('<p class="stitle">Servi\u00e7os dispon\u00edveis</p>', unsafe_allow_html=True)
    tabs = st.tabs(["M\u00e3os", "P\u00e9s", "Combos"])
    cats = ["maos", "pes", "combo"]
    for i, cat in enumerate(cats):
        with tabs[i]:
            servicos = query("SELECT * FROM servicos WHERE categoria=%s AND ativo=1", (cat,))
            for s in servicos:
                st.markdown('<div class="card"><div style="display:flex; justify-content:space-between; align-items:center;"><div><strong style="font-size:15px; color:var(--text);">' + str(s["nome"]) + '</strong><br><span style="color:var(--muted); font-size:13px;">' + str(s["descricao"]) + '</span><br><span style="color:var(--light); font-size:12px;">~' + str(s["duracao_min"]) + ' min</span></div><div><strong style="color:var(--text); font-size:20px;">R$ ' + f'{s["preco"]:.0f}' + '</strong></div></div></div>', unsafe_allow_html=True)
                if st.button("Agendar", key="srv_" + str(s["id"]), use_container_width=True, type="primary"):
                    ir("escolher_manicure", servico_id=s["id"]); st.rerun()

def tela_escolher_manicure():
    st.markdown('<div class="header"><h1>Escolher profissional</h1><p>Selecione quem vai cuidar de voc\u00ea</p></div>', unsafe_allow_html=True)
    if st.button("Voltar"): ir("cliente_home"); st.rerun()
    favs = query("SELECT manicure_id FROM favoritas WHERE cliente_id=%s", (st.session_state.user_id,))
    fav_ids = [f["manicure_id"] for f in favs]
    manicures = query("SELECT u.*, (SELECT COUNT(*) FROM agendamentos a WHERE a.manicure_id=u.id AND a.status='concluido') as total_atend FROM usuarios u WHERE u.tipo='manicure' AND u.ativo=1 ORDER BY u.avaliacao_media DESC")
    if not manicures:
        st.info("Nenhuma profissional dispon\u00edvel."); return
    st.markdown('<p class="stitle">Profissionais dispon\u00edveis</p>', unsafe_allow_html=True)
    cores = ["#1A1A2E","#0f3460","#533483","#e94560","#16213e","#7B2D8E","#1B5E20","#BF360C"]
    for idx, m in enumerate(manicures):
        letra = str(m["nome"])[:1].upper()
        pri = str(m["nome"]).split().pop(0)
        cor = cores[idx % len(cores)]
        fav = " | FAVORITA" if m["id"] in fav_ids else ""
        st.markdown('<div class="card"><div style="display:flex; align-items:center; gap:14px;"><div class="av" style="background:' + cor + ';">' + letra + '</div><div style="flex:1;"><strong style="font-size:15px; color:var(--text);">' + str(m["nome"]) + '</strong><span style="color:var(--gold); font-size:11px;">' + fav + '</span><br><span class="stars">' + estrelas(m["avaliacao_media"] or 5) + '</span> <span style="color:var(--light); font-size:11px;">' + str(m["total_avaliacoes"] or 0) + ' avalia\u00e7\u00f5es | ' + str(m["total_atend"]) + ' atendimentos</span><br><span style="color:var(--muted); font-size:12px; font-style:italic;">' + str(m["bio"] or "") + '</span></div></div></div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Agendar com " + pri, key="man_" + str(m["id"]), use_container_width=True, type="primary"):
                ir("agendar", manicure_id=m["id"]); st.rerun()
        with c2:
            if m["id"] not in fav_ids:
                if st.button("Favoritar", key="fav_" + str(m["id"]), use_container_width=True):
                    execute("INSERT INTO favoritas (cliente_id, manicure_id) VALUES (%s,%s) ON CONFLICT DO NOTHING", (st.session_state.user_id, m["id"])); st.rerun()

def tela_agendar():
    sl = query("SELECT * FROM servicos WHERE id=%s", (st.session_state.servico_id,))
    ml = query("SELECT * FROM usuarios WHERE id=%s", (st.session_state.manicure_id,))
    if not sl or not ml: st.error("Erro."); ir("cliente_home"); st.rerun(); return
    srv = sl; man = ml
    st.markdown('<div class="header"><h1>Agendar</h1><p>' + str(srv["nome"]) + ' com ' + str(man["nome"]) + '</p></div>', unsafe_allow_html=True)
    if st.button("Voltar"): ir("escolher_manicure"); st.rerun()
    vt = srv["preco"]; dur = srv["duracao_min"]
    st.markdown('<div class="card-gold" style="text-align:center;"><h3 style="margin:0; color:var(--text);">' + str(srv["nome"]) + '</h3><p style="color:var(--muted); margin:4px 0 10px 0;">~' + str(dur) + ' minutos</p><p style="font-size:28px; font-weight:800; color:var(--text); margin:0;">R$ ' + f'{vt:.2f}' + '</p></div>', unsafe_allow_html=True)
    disps = query("SELECT * FROM disponibilidade WHERE manicure_id=%s AND ativo=1", (st.session_state.manicure_id,))
    dias_sem = set(d["dia_semana"] for d in disps)
    hoje = date.today()
    agendados = query("SELECT a.data, a.horario, s.duracao_min FROM agendamentos a JOIN servicos s ON a.servico_id=s.id WHERE a.manicure_id=%s AND a.status IN ('pendente','confirmado') AND a.data >= %s", (st.session_state.manicure_id, hoje.strftime("%d/%m/%Y")))
    dias_disp = [hoje + timedelta(days=i) for i in range(1,31) if (hoje + timedelta(days=i)).weekday() in dias_sem]
    st.markdown('<p class="stitle">Data</p>', unsafe_allow_html=True)
    opcoes = {}
    for d in dias_disp[:20]:
        opcoes[d.strftime("%d/%m/%Y (%a)")] = d
    data_str = st.selectbox("Data dispon\u00edvel:", list(opcoes.keys()))
    data_sel = opcoes.get(data_str)
    horario_sel = None
    if data_sel:
        ds = [d for d in disps if d["dia_semana"] == data_sel.weekday()]
        if ds:
            di = ds
            pi = di["hora_inicio"].split(":"); pf = di["hora_fim"].split(":")
            ini = int(pi)*60+int(pi); fim = int(pf)*60+int(pf)
            dbr = data_sel.strftime("%d/%m/%Y")
            ocp = set()
            for ag in agendados:
                if ag["data"] == dbr:
                    ph = ag["horario"].split(":"); base = int(ph)*60+int(ph)
                    for off in range(0, ag["duracao_min"], 30): ocp.add(base+off)
            livres = []
            cur = ini
            while cur + dur <= fim:
                ok = all((cur+off) not in ocp for off in range(0, dur, 30))
                if ok: livres.append(f"{cur//60:02d}:{cur%60:02d}")
                cur += 30
            st.markdown('<p class="stitle">Hor\u00e1rio</p>', unsafe_allow_html=True)
            if livres:
                horario_sel = st.selectbox("Hor\u00e1rios dispon\u00edveis:", livres)
            else:
                st.warning("Sem hor\u00e1rios nesta data.")
    st.markdown('<p class="stitle">Local</p>', unsafe_allow_html=True)
    endereco = st.text_input("Endere\u00e7o completo")
    complemento = st.text_input("Complemento (apto, bloco...)")
    st.markdown('<p class="stitle">Pagamento</p>', unsafe_allow_html=True)
    fpg = st.radio("Forma:", ["PIX", "Cart\u00e3o de Cr\u00e9dito", "Cart\u00e3o de D\u00e9bito", "Dinheiro"], horizontal=True)
    fmap = {"PIX":"pix","Cart\u00e3o de Cr\u00e9dito":"cartao_credito","Cart\u00e3o de D\u00e9bito":"cartao_debito","Dinheiro":"dinheiro"}
    obs = st.text_area("Observa\u00e7\u00f5es (opcional)")
    st.markdown('<div class="sep"></div>', unsafe_allow_html=True)
    st.markdown('<div class="card" style="border:1.5px solid var(--text);"><p style="font-size:11px; font-weight:700; color:var(--light); text-transform:uppercase; letter-spacing:0.5px; margin:0 0 10px 0;">Resumo</p><p style="color:var(--text); font-size:14px; margin:0; line-height:2.2;"><strong>Servi\u00e7o:</strong> ' + str(srv["nome"]) + '<br><strong>Profissional:</strong> ' + str(man["nome"]) + '<br><strong>Data:</strong> ' + str(data_str) + '<br><strong>Hor\u00e1rio:</strong> ' + str(horario_sel or "-") + '<br><strong>Pagamento:</strong> ' + str(fpg) + '</p><div class="sep"></div><p style="font-size:28px; font-weight:800; color:var(--text); text-align:center; margin:0;">R$ ' + f'{vt:.2f}' + '</p></div>', unsafe_allow_html=True)
    if st.button("Confirmar agendamento", use_container_width=True, type="primary"):
        if not horario_sel: st.error("Selecione um hor\u00e1rio."); return
        if not endereco: st.error("Informe o endere\u00e7o."); return
        dbr = data_sel.strftime("%d/%m/%Y")
        dlib = (data_sel + timedelta(days=DIAS_RECEBER)).strftime("%d/%m/%Y")
        fp = fmap.get(fpg, "pix")
        vm = vt * (1 - COMISSAO)
        vc = vt * COMISSAO
        res = execute_ret("INSERT INTO agendamentos (cliente_id,manicure_id,servico_id,data,horario,endereco_atendimento,complemento,valor_total,valor_manicure,valor_comissao,forma_pagamento,observacoes,data_liberacao_manicure,status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id", (st.session_state.user_id, st.session_state.manicure_id, st.session_state.servico_id, dbr, horario_sel, endereco, complemento, vt, vm, vc, fp, obs, dlib, "pendente"))
        if res:
            aid = res["id"]
            execute("INSERT INTO transacoes (agendamento_id,tipo,valor,destinatario_id,forma_pagamento,data_prevista_liberacao) VALUES (%s,%s,%s,%s,%s,%s)", (aid, "pagamento", vt, st.session_state.manicure_id, fp, dlib))
            execute("INSERT INTO notificacoes (usuario_id,titulo,mensagem,tipo) VALUES (%s,%s,%s,%s)", (st.session_state.manicure_id, "Novo agendamento", "Agendamento para " + dbr + " \u00e0s " + horario_sel, "agendamento"))
            st.session_state.ultimo_ag = aid
            st.session_state.valor_pagar = vt
            st.session_state.forma_pg = fp
            ir("pagamento"); st.rerun()

def tela_pagamento():
    aid = st.session_state.get("ultimo_ag")
    vt = st.session_state.get("valor_pagar", 0)
    fp = st.session_state.get("forma_pg", "pix")
    rl = query("SELECT a.*, s.nome as sn, u.nome as mn FROM agendamentos a JOIN servicos s ON a.servico_id=s.id JOIN usuarios u ON a.manicure_id=u.id WHERE a.id=%s", (aid,))
    if not rl: ir("cliente_home"); st.rerun(); return
    ag = rl
    st.markdown('<div class="header"><h1>Pagamento</h1><p>Finalize seu agendamento</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="card" style="text-align:center;"><p style="font-size:11px; color:var(--light); text-transform:uppercase; font-weight:600; letter-spacing:0.5px; margin:0;">Valor total</p><p style="font-size:36px; font-weight:800; color:var(--text); margin:8px 0;">R$ ' + f'{vt:.2f}' + '</p><p style="color:var(--muted); font-size:13px; margin:0;">' + str(ag["sn"]) + ' com ' + str(ag["mn"]) + '</p></div>', unsafe_allow_html=True)
    if fp == "pix":
        st.markdown('<p class="stitle">Pague via PIX</p>', unsafe_allow_html=True)
        qr_b64 = gerar_pix_qrcode(vt, "Unha Click - " + str(ag["sn"]))
        st.markdown('<div class="card" style="text-align:center; padding:30px;"><p style="color:var(--muted); font-size:13px; margin:0 0 16px 0;">Escaneie o QR Code com o app do seu banco</p><img src="data:image/png;base64,' + qr_b64 + '" style="width:220px; height:220px; border-radius:12px; border:1px solid var(--border);"><p style="color:var(--light); font-size:12px; margin:16px 0 0 0;">Chave PIX: ' + CHAVE_PIX_DONO + '</p><p style="color:var(--light); font-size:12px; margin:4px 0 0 0;">Valor: R$ ' + f'{vt:.2f}' + '</p></div>', unsafe_allow_html=True)
        pix_code = f"00020126580014br.gov.bcb.pix0136{CHAVE_PIX_DONO}520400005303986540{vt:.2f}5802BR5913UNHA CLICK6009SAO PAULO62070503***6304"
        st.code(pix_code, language=None)
        st.markdown('<p style="color:var(--light); font-size:11px; text-align:center;">Copie o c\u00f3digo acima para Pix Copia e Cola</p>', unsafe_allow_html=True)
    elif fp in ("cartao_credito", "cartao_debito"):
        tipo_cartao = "Cr\u00e9dito" if fp == "cartao_credito" else "D\u00e9bito"
        st.markdown('<p class="stitle">Cart\u00e3o de ' + tipo_cartao + '</p>', unsafe_allow_html=True)
        st.markdown('<div class="card"><p style="color:var(--muted); font-size:13px; margin:0 0 16px 0;">Dados do cart\u00e3o</p></div>', unsafe_allow_html=True)
        num = st.text_input("N\u00famero do cart\u00e3o", placeholder="0000 0000 0000 0000")
        c1, c2 = st.columns(2)
        with c1: val = st.text_input("Validade", placeholder="MM/AA")
        with c2: cvv = st.text_input("CVV", placeholder="[CREDIT_DEBIT_CARD_CVV]", type="password")
        titular = st.text_input("Nome no cart\u00e3o", placeholder="Como est\u00e1 no cart\u00e3o")
    else:
        st.markdown('<div class="card" style="text-align:center;"><p style="color:var(--muted); font-size:14px; margin:0;">Pagamento em dinheiro ser\u00e1 feito no momento do atendimento.</p></div>', unsafe_allow_html=True)
    st.markdown("")
    if st.button("Confirmar pagamento", use_container_width=True, type="primary"):
        execute("UPDATE agendamentos SET pago=1, status='confirmado' WHERE id=%s", (aid,))
        execute("UPDATE transacoes SET status='pago' WHERE agendamento_id=%s", (aid,))
        execute("INSERT INTO notificacoes (usuario_id,titulo,mensagem,tipo) VALUES (%s,%s,%s,%s)", (ag["manicure_id"], "Pagamento confirmado", "R$ " + f'{vt:.2f}' + " recebido via " + nome_pg(fp), "pagamento"))
        ir("confirmacao"); st.rerun()

def tela_confirmacao():
    aid = st.session_state.get("ultimo_ag")
    rl = query("SELECT a.*, s.nome as sn, u.nome as mn FROM agendamentos a JOIN servicos s ON a.servico_id=s.id JOIN usuarios u ON a.manicure_id=u.id WHERE a.id=%s", (aid,))
    if not rl: ir("cliente_home"); st.rerun(); return
    ag = rl
    st.markdown('<div style="text-align:center; padding:60px 0 20px 0;"><div style="width:64px; height:64px; background:#D1FAE5; border-radius:50%; display:flex; align-items:center; justify-content:center; margin:0 auto 20px auto;"><span style="color:#065F46; font-size:28px; font-weight:800;">\u2713</span></div><h2 style="color:var(--text); font-weight:800; margin:0;">Tudo certo!</h2><p style="color:var(--muted); font-size:14px; margin:8px 0 0 0;">Seu agendamento foi confirmado e o pagamento processado.</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="card" style="border:1.5px solid var(--border);"><p style="color:var(--text); font-size:14px; margin:0; line-height:2.2;"><strong>Servi\u00e7o:</strong> ' + str(ag["sn"]) + '<br><strong>Profissional:</strong> ' + str(ag["mn"]) + '<br><strong>Data:</strong> ' + str(ag["data"]) + '<br><strong>Hor\u00e1rio:</strong> ' + str(ag["horario"]) + '<br><strong>Local:</strong> ' + str(ag["endereco_atendimento"]) + '<br><strong>Pagamento:</strong> ' + nome_pg(ag["forma_pagamento"]) + ' ' + tag_st("confirmado") + '</p><div class="sep"></div><p style="font-size:28px; font-weight:800; color:var(--text); text-align:center; margin:0;">R$ ' + f'{ag["valor_total"]:.2f}' + '</p></div>', unsafe_allow_html=True)
    if st.button("Voltar ao in\u00edcio", use_container_width=True, type="primary"):
        ir("cliente_home"); st.rerun()

def tela_meus_agendamentos():
    st.markdown('<div class="header"><h1>Meus agendamentos</h1></div>', unsafe_allow_html=True)
    if st.button("Voltar"): ir("cliente_home"); st.rerun()
    ags = query("SELECT a.*, s.nome as sn, u.nome as mn FROM agendamentos a JOIN servicos s ON a.servico_id=s.id JOIN usuarios u ON a.manicure_id=u.id WHERE a.cliente_id=%s ORDER BY a.data_criacao DESC LIMIT 20", (st.session_state.user_id,))
    if not ags:
        st.markdown('<p style="color:var(--light); text-align:center; padding:60px 0;">Nenhum agendamento ainda.</p>', unsafe_allow_html=True)
    else:
        for ag in ags:
            pago_tag = ' <span class="tag tag-pago">PAGO</span>' if ag["pago"] == 1 else ""
            st.markdown('<div class="card"><div style="display:flex; justify-content:space-between; align-items:center;"><div><strong style="color:var(--text);">' + str(ag["sn"]) + '</strong><br><span style="color:var(--muted); font-size:13px;">com ' + str(ag["mn"]) + '</span><br><span style="color:var(--light); font-size:12px;">' + str(ag["data"]) + ' \u00e0s ' + str(ag["horario"]) + '</span></div><div style="text-align:right;">' + tag_st(ag["status"]) + pago_tag + '<br><strong style="color:var(--text); font-size:18px;">R$ ' + f'{ag["valor_total"]:.2f}' + '</strong></div></div></div>', unsafe_allow_html=True)
            if ag["status"] == "concluido" and ag["avaliacao_nota"] is None:
                if st.button("Avaliar", key="av_" + str(ag["id"]), use_container_width=True):
                    ir("avaliar", avaliando_id=ag["id"]); st.rerun()

def tela_avaliar():
    aid = st.session_state.get("avaliando_id")
    rl = query("SELECT a.*, s.nome as sn, u.nome as mn FROM agendamentos a JOIN servicos s ON a.servico_id=s.id JOIN usuarios u ON a.manicure_id=u.id WHERE a.id=%s", (aid,))
    if not rl: ir("cliente_home"); st.rerun(); return
    ag = rl
    st.markdown('<div class="header"><h1>Avaliar</h1><p>' + str(ag["sn"]) + ' com ' + str(ag["mn"]) + '</p></div>', unsafe_allow_html=True)
    if st.button("Voltar"): ir("meus_agendamentos"); st.rerun()
    st.markdown('<p class="stitle">Como foi sua experi\u00eancia?</p>', unsafe_allow_html=True)
    nota = st.slider("Nota:", 1, 5, 5)
    txt = {1:"P\u00e9ssimo",2:"Ruim",3:"Regular",4:"Bom",5:"Excelente"}
    st.markdown('<h2 style="text-align:center; color:var(--text); font-weight:800;">' + txt[nota] + '</h2>', unsafe_allow_html=True)
    comentario = st.text_area("Conte como foi (opcional)")
    if st.button("Enviar avalia\u00e7\u00e3o", use_container_width=True, type="primary"):
        execute("UPDATE agendamentos SET avaliacao_nota=%s, avaliacao_comentario=%s WHERE id=%s", (nota, comentario, aid))
        mr = query("SELECT AVG(avaliacao_nota) as media, COUNT(*) as total FROM agendamentos WHERE manicure_id=%s AND avaliacao_nota IS NOT NULL", (ag["manicure_id"],))
        if mr:
            execute("UPDATE usuarios SET avaliacao_media=%s, total_avaliacoes=%s WHERE id=%s", (mr["media"] or 5, mr["total"] or 0, ag["manicure_id"]))
        execute("INSERT INTO favoritas (cliente_id, manicure_id) VALUES (%s,%s) ON CONFLICT DO NOTHING", (st.session_state.user_id, ag["manicure_id"]))
        st.success("Avalia\u00e7\u00e3o enviada!"); ir("cliente_home"); st.rerun()

def tela_perfil():
    rl = query("SELECT * FROM usuarios WHERE id=%s", (st.session_state.user_id,))
    if not rl: ir("cliente_home"); st.rerun(); return
    u = rl
    st.markdown('<div class="header"><h1>Meu perfil</h1></div>', unsafe_allow_html=True)
    if st.button("Voltar"): ir("cliente_home"); st.rerun()
    letra = str(u["nome"])[:1].upper()
    st.markdown('<div class="card" style="text-align:center; padding:30px;"><div class="av" style="background:var(--text); width:72px; height:72px; font-size:28px; border-radius:20px; margin:0 auto 16px auto;">' + letra + '</div><h2 style="margin:0; color:var(--text); font-weight:800;">' + str(u["nome"]) + '</h2><div class="sep"></div><p style="color:var(--muted); font-size:14px; line-height:2; margin:0; text-align:left;"><strong>Telefone:</strong> ' + str(u["telefone"]) + '<br><strong>E-mail:</strong> ' + str(u["email"] or "N\u00e3o informado") + '<br><strong>Endere\u00e7o:</strong> ' + str(u["endereco"] or "N\u00e3o informado") + '</p></div>', unsafe_allow_html=True)

def tela_manicure_home():
    hoje = date.today().strftime("%d/%m/%Y")
    p = st.session_state.user_nome.split()
    pri = p.pop(0) if p else st.session_state.user_nome
    st.markdown('<div class="header"><h1>Ol\u00e1, ' + pri + '</h1><p>Painel da profissional</p></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Notifica\u00e7\u00f5es", use_container_width=True): pass
    with c2:
        if st.button("Sair", use_container_width=True): sair(); st.rerun()
    mes = date.today().strftime("%m/%Y")
    gr = query("SELECT COALESCE(SUM(valor_manicure),0) as g, COUNT(*) as t FROM agendamentos WHERE manicure_id=%s AND status='concluido' AND data LIKE %s", (st.session_state.user_id, "%" + mes))
    g = gr if gr else {"g":0,"t":0}
    rr = query("SELECT COALESCE(SUM(valor_manicure),0) as v FROM agendamentos WHERE manicure_id=%s AND status='concluido' AND pago=1 AND data_liberacao_manicure > %s", (st.session_state.user_id, hoje))
    r = rr if rr else {"v":0}
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="kpi"><div class="kpi-l">Ganhos do m\u00eas</div><div class="kpi-v" style="color:var(--green);">R$ ' + f'{g["g"]:.2f}' + '</div><div class="kpi-l">' + str(g["t"]) + ' atendimentos</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="kpi"><div class="kpi-l">A receber</div><div class="kpi-v" style="color:var(--text);">R$ ' + f'{r["v"]:.2f}' + '</div><div class="kpi-l">Libera\u00e7\u00e3o em ' + str(DIAS_RECEBER) + ' dias</div></div>', unsafe_allow_html=True)
    pend = query("SELECT a.*, s.nome as sn, u.nome as cn FROM agendamentos a JOIN servicos s ON a.servico_id=s.id JOIN usuarios u ON a.cliente_id=u.id WHERE a.manicure_id=%s AND a.status='pendente' ORDER BY a.data_criacao DESC", (st.session_state.user_id,))
    if pend:
        st.markdown('<p class="stitle">Aguardando sua confirma\u00e7\u00e3o</p>', unsafe_allow_html=True)
        for ag in pend:
            pago_tag = ' <span class="tag tag-pago">PAGO</span>' if ag["pago"] == 1 else ""
            st.markdown('<div class="card-gold"><strong style="color:var(--text);">' + str(ag["sn"]) + '</strong>' + pago_tag + '<br><span style="color:var(--muted); font-size:13px;">Cliente: ' + str(ag["cn"]) + '</span><br><span style="color:var(--light); font-size:12px;">' + str(ag["data"]) + ' \u00e0s ' + str(ag["horario"]) + ' | ' + str(ag["endereco_atendimento"] or "-") + '</span><br><strong style="color:var(--green);">Voc\u00ea recebe: R$ ' + f'{ag["valor_manicure"]:.2f}' + '</strong></div>', unsafe_allow_html=True)
            x1, x2 = st.columns(2)
            with x1:
                if st.button("Aceitar", key="ac_" + str(ag["id"]), use_container_width=True, type="primary"):
                    execute("UPDATE agendamentos SET status='confirmado' WHERE id=%s", (ag["id"],))
                    execute("INSERT INTO notificacoes (usuario_id,titulo,mensagem,tipo) VALUES (%s,%s,%s,%s)", (ag["cliente_id"], "Agendamento aceito", str(ag["sn"]) + " confirmado para " + str(ag["data"]), "agendamento"))
                    st.rerun()
            with x2:
                if st.button("Recusar", key="rc_" + str(ag["id"]), use_container_width=True):
                    execute("UPDATE agendamentos SET status='cancelado' WHERE id=%s", (ag["id"],))
                    execute("INSERT INTO notificacoes (usuario_id,titulo,mensagem,tipo) VALUES (%s,%s,%s,%s)", (ag["cliente_id"], "Recusado", "Procure outra profissional.", "agendamento"))
                    st.rerun()
    st.markdown('<p class="stitle">Hoje (' + hoje + ')</p>', unsafe_allow_html=True)
    hag = query("SELECT a.*, s.nome as sn, u.nome as cn FROM agendamentos a JOIN servicos s ON a.servico_id=s.id JOIN usuarios u ON a.cliente_id=u.id WHERE a.manicure_id=%s AND a.data=%s AND a.status='confirmado' ORDER BY a.horario", (st.session_state.user_id, hoje))
    if not hag:
        st.markdown('<p style="color:var(--light); text-align:center; padding:20px;">Nenhum atendimento hoje.</p>', unsafe_allow_html=True)
    else:
        for ag in hag:
            st.markdown('<div class="card"><strong style="color:var(--text);">' + str(ag["horario"]) + '</strong> ' + tag_st(ag["status"]) + '<br><span style="color:var(--muted); font-size:13px;">' + str(ag["sn"]) + ' | ' + str(ag["cn"]) + '</span><br><span style="color:var(--light); font-size:12px;">' + str(ag["endereco_atendimento"] or "-") + '</span><br><strong style="color:var(--green);">R$ ' + f'{ag["valor_manicure"]:.2f}' + '</strong></div>', unsafe_allow_html=True)
            if st.button("Concluir", key="cc_" + str(ag["id"]), use_container_width=True, type="primary"):
                execute("UPDATE agendamentos SET status='concluido' WHERE id=%s", (ag["id"],))
                execute("INSERT INTO notificacoes (usuario_id,titulo,mensagem,tipo) VALUES (%s,%s,%s,%s)", (ag["cliente_id"], "Conclu\u00eddo", "Avalie sua experi\u00eancia!", "avaliacao"))
                st.rerun()
    st.markdown('<p class="stitle">Pr\u00f3ximos</p>', unsafe_allow_html=True)
    prx = query("SELECT a.*, s.nome as sn, u.nome as cn FROM agendamentos a JOIN servicos s ON a.servico_id=s.id JOIN usuarios u ON a.cliente_id=u.id WHERE a.manicure_id=%s AND a.status='confirmado' AND a.data > %s ORDER BY a.data, a.horario LIMIT 10", (st.session_state.user_id, hoje))
    if not prx:
        st.markdown('<p style="color:var(--light); text-align:center;">Nenhum agendamento futuro.</p>', unsafe_allow_html=True)
    else:
        for ag in prx:
            st.markdown('<div class="card"><strong style="color:var(--text);">' + str(ag["data"]) + ' \u00e0s ' + str(ag["horario"]) + '</strong><br><span style="color:var(--muted); font-size:13px;">' + str(ag["sn"]) + ' | ' + str(ag["cn"]) + '</span><br><strong style="color:var(--green);">R$ ' + f'{ag["valor_manicure"]:.2f}' + '</strong></div>', unsafe_allow_html=True)

def tela_admin():
    st.markdown('<div class="header-dark"><h1>Painel administrativo</h1><p>Unha Click</p></div>', unsafe_allow_html=True)
    if st.button("Sair"): sair(); st.rerun()
    stats = query("SELECT (SELECT COUNT(*) FROM usuarios WHERE tipo='cliente') as cli, (SELECT COUNT(*) FROM usuarios WHERE tipo='manicure') as man, (SELECT COUNT(*) FROM agendamentos) as ag, (SELECT COALESCE(SUM(valor_total),0) FROM agendamentos WHERE status='concluido') as fat, (SELECT COALESCE(SUM(valor_comissao),0) FROM agendamentos WHERE status='concluido') as com")
    s = stats if stats else {"cli":0,"man":0,"ag":0,"fat":0,"com":0}
    c1, c2 = st.columns(2)
    with c1: st.markdown('<div class="kpi"><div class="kpi-l">Clientes</div><div class="kpi-v" style="color:var(--text);">' + str(s["cli"]) + '</div></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="kpi"><div class="kpi-l">Profissionais</div><div class="kpi-v" style="color:var(--text);">' + str(s["man"]) + '</div></div>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3: st.markdown('<div class="kpi"><div class="kpi-l">Agendamentos</div><div class="kpi-v" style="color:var(--blue);">' + str(s["ag"]) + '</div></div>', unsafe_allow_html=True)
    with c4: st.markdown('<div class="kpi"><div class="kpi-l">Faturamento</div><div class="kpi-v" style="color:var(--green);">R$ ' + f'{s["fat"]:.0f}' + '</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="card-gold" style="text-align:center; margin-top:12px;"><p class="kpi-l" style="margin:0 0 4px 0;">Sua comiss\u00e3o (20%)</p><p style="font-size:32px; font-weight:800; color:var(--gold); margin:0;">R$ ' + f'{s["com"]:.2f}' + '</p></div>', unsafe_allow_html=True)
    st.markdown('<p class="stitle">\u00daltimos agendamentos</p>', unsafe_allow_html=True)
    ult = query("SELECT a.*, s.nome as sn, u1.nome as cn, u2.nome as mn FROM agendamentos a JOIN servicos s ON a.servico_id=s.id JOIN usuarios u1 ON a.cliente_id=u1.id JOIN usuarios u2 ON a.manicure_id=u2.id ORDER BY a.data_criacao DESC LIMIT 10")
    for a in ult:
        pago_tag = ' <span class="tag tag-pago">PAGO</span>' if a["pago"] == 1 else ""
        st.markdown('<div class="card"><div style="display:flex; justify-content:space-between; align-items:center;"><div><strong style="color:var(--text);">' + str(a["sn"]) + '</strong><br><span style="color:var(--muted); font-size:13px;">' + str(a["cn"]) + ' \u2192 ' + str(a["mn"]) + '</span><br><span style="color:var(--light); font-size:12px;">' + str(a["data"]) + ' \u00e0s ' + str(a["horario"]) + '</span></div><div style="text-align:right;">' + tag_st(a["status"]) + pago_tag + '<br><strong style="color:var(--text);">R$ ' + f'{a["valor_total"]:.2f}' + '</strong></div></div></div>', unsafe_allow_html=True)

telas = {"login":tela_login, "cadastro":tela_cadastro, "cliente_home":tela_cliente_home, "escolher_manicure":tela_escolher_manicure, "agendar":tela_agendar, "pagamento":tela_pagamento, "confirmacao":tela_confirmacao, "meus_agendamentos":tela_meus_agendamentos, "avaliar":tela_avaliar, "perfil":tela_perfil, "manicure_home":tela_manicure_home, "admin":tela_admin}
t = st.session_state.get("tela", "login")
if t in telas: telas[t]()
else: tela_login()
