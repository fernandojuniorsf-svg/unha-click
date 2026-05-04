
import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
import hashlib
from datetime import datetime, date, timedelta

def gerar_hash(texto):
    return hashlib.sha256(texto.encode()).hexdigest()

HASH_ADMIN = gerar_hash("admin123")
HASH_DEMO = gerar_hash(str(1234))
COMISSAO = 0.20
DIAS_RECEBER = 2
TEMPO_ACEITE_HORAS = 1

st.set_page_config(page_title="Unha Click", page_icon="\u2022", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
* {font-family: 'Inter', sans-serif !important;}
:root {--rosa: #C48B9F; --rosa-light: #F5E6EC; --gold: #B8860B; --gold-light: #FFF8E7; --bg: #FAFAFA; --card-bg: #FFFFFF; --text: #1A1A2E; --text-light: #6B7280; --border: #F0F0F0; --success: #10B981; --warning: #F59E0B; --danger: #EF4444; --info: #6366F1;}
.stApp {background-color: var(--bg) !important;}
.header-unha {background: var(--card-bg); padding: 40px 24px 30px 24px; border-bottom: 1px solid var(--border); margin: -6rem -1rem 2rem -1rem; text-align:left;}
.header-unha h1 {color: var(--text) !important; font-size:28px !important; margin:0 !important; font-weight:800 !important; letter-spacing: -0.5px;}
.header-unha p {color: var(--text-light) !important; font-size:14px !important; margin:6px 0 0 0 !important; font-weight:400;}
.card {background: var(--card-bg); border-radius: 16px; padding: 20px; margin: 10px 0; border: 1px solid var(--border); transition: all 0.2s ease;}
.card:hover {border-color: var(--rosa); box-shadow: 0 4px 12px rgba(196,139,159,0.08);}
.card-destaque {background: var(--gold-light); border-radius: 16px; padding: 20px; margin: 10px 0; border: 1px solid rgba(184,134,11,0.15);}
.kpi-box {background: var(--card-bg); border-radius: 16px; padding: 24px; text-align:center; border: 1px solid var(--border);}
.kpi-valor {font-size: 32px; font-weight: 800; margin: 8px 0 4px 0; letter-spacing: -1px;}
.kpi-label {font-size: 12px; color: var(--text-light); font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;}
.tag {display:inline-block; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 600; letter-spacing: 0.3px;}
.tag-pendente {background: #FEF3C7; color: #92400E;}
.tag-confirmado {background: #D1FAE5; color: #065F46;}
.tag-concluido {background: #DBEAFE; color: #1E40AF;}
.tag-cancelado {background: #FEE2E2; color: #991B1B;}
.tag-aguardando {background: #EDE9FE; color: #5B21B6;}
.estrelas-box {color: var(--gold); font-size: 14px; letter-spacing: 1px;}
.stButton > button {border-radius: 12px !important; font-weight: 600 !important; padding: 10px 20px !important; font-size: 14px !important; transition: all 0.15s ease !important; letter-spacing: -0.2px;}
.stButton > button:hover {transform: translateY(-1px) !important;}
.stButton > button[data-testid="baseButton-primary"] {background: var(--text) !important; color: white !important; border: none !important;}
.stButton > button[data-testid="baseButton-secondary"] {background: transparent !important; color: var(--text) !important; border: 1.5px solid var(--border) !important;}
div[data-testid="stTextInput"] > div > div > input {border-radius: 12px !important; border: 1.5px solid var(--border) !important; padding: 12px 16px !important; font-size: 14px !important;}
div[data-testid="stTextInput"] > div > div > input:focus {border-color: var(--rosa) !important; box-shadow: 0 0 0 3px rgba(196,139,159,0.08) !important;}
.avatar {width: 48px; height: 48px; border-radius: 12px; display:flex; align-items:center; justify-content:center; font-size:18px; font-weight:700; color:white;}
.divider {height: 1px; background: var(--border); margin: 24px 0;}
.section-title {font-size: 13px; font-weight: 700; color: var(--text-light); text-transform: uppercase; letter-spacing: 0.8px; margin: 32px 0 16px 0;}
</style>""", unsafe_allow_html=True)

def get_new_connection():
    db = st.secrets["database"]
    return psycopg2.connect(host=db["host"], port=db["port"], dbname=db["dbname"], user=db["user"], password=db["password"], cursor_factory=RealDictCursor)

def query(sql, params=None):
    try:
        conn = get_new_connection()
        cur = conn.cursor()
        cur.execute(sql, params)
        resultado = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        return resultado
    except Exception as e:
        st.error(f"Erro no banco: {e}")
        return []

def execute(sql, params=None):
    try:
        conn = get_new_connection()
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        st.error(f"Erro no banco: {e}")

def execute_returning(sql, params=None):
    try:
        conn = get_new_connection()
        cur = conn.cursor()
        cur.execute(sql, params)
        resultado = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return resultado
    except Exception as e:
        st.error(f"Erro no banco: {e}")
        return None

def ir_para(tela, **kwargs):
    st.session_state.tela = tela
    for k, v in kwargs.items():
        st.session_state[k] = v

def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]

def estrelas(nota):
    n = int(nota or 5)
    cheia = "\u2605"
    vazia = "\u2606"
    return cheia * n + vazia * (5 - n)

def tag_status(status):
    nomes = {"pendente": "Pendente", "confirmado": "Confirmado", "concluido": "Conclu\u00eddo", "cancelado": "Cancelado", "aguardando_aceite": "Aguardando"}
    css = status.replace("aguardando_aceite", "aguardando")
    return '<span class="tag tag-' + css + '">' + nomes.get(status, status) + '</span>'

def nome_pagamento(fp):
    nomes = {"pix": "PIX", "cartao_credito": "Cart\u00e3o de Cr\u00e9dito", "cartao_debito": "Cart\u00e3o de D\u00e9bito", "dinheiro": "Dinheiro"}
    return nomes.get(fp, fp)

@st.cache_resource
def inicializar_banco():
    try:
        conn = get_new_connection()
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS usuarios (id SERIAL PRIMARY KEY, nome TEXT NOT NULL, telefone TEXT UNIQUE NOT NULL, email TEXT, senha TEXT NOT NULL, tipo TEXT DEFAULT 'cliente', endereco TEXT, bairro TEXT, cidade TEXT, estado TEXT DEFAULT 'SP', foto TEXT, avaliacao_media REAL DEFAULT 5.0, total_avaliacoes INTEGER DEFAULT 0, especialidades TEXT, bio TEXT, chave_pix TEXT, banco TEXT, ativo INTEGER DEFAULT 1, data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        cur.execute("""CREATE TABLE IF NOT EXISTS servicos (id SERIAL PRIMARY KEY, nome TEXT NOT NULL, descricao TEXT, preco REAL NOT NULL, duracao_min INTEGER DEFAULT 60, categoria TEXT DEFAULT 'maos', icone TEXT DEFAULT 'maos', ativo INTEGER DEFAULT 1)""")
        cur.execute("""CREATE TABLE IF NOT EXISTS agendamentos (id SERIAL PRIMARY KEY, cliente_id INTEGER REFERENCES usuarios(id), manicure_id INTEGER, servico_id INTEGER REFERENCES servicos(id), data TEXT, horario TEXT, endereco_atendimento TEXT, bairro TEXT, complemento TEXT, valor_total REAL, valor_manicure REAL, valor_comissao REAL, cupom_codigo TEXT, status TEXT DEFAULT 'pendente', forma_pagamento TEXT DEFAULT 'pix', observacoes TEXT, data_liberacao_manicure TEXT, pago INTEGER DEFAULT 0, avaliacao_nota INTEGER, avaliacao_comentario TEXT, favorita INTEGER DEFAULT 0, aberto_para_todas INTEGER DEFAULT 0, hora_limite_aceite TIMESTAMP, data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        cur.execute("""CREATE TABLE IF NOT EXISTS disponibilidade (id SERIAL PRIMARY KEY, manicure_id INTEGER, dia_semana INTEGER, hora_inicio TEXT DEFAULT '08:00', hora_fim TEXT DEFAULT '18:00', ativo INTEGER DEFAULT 1)""")
        cur.execute("""CREATE TABLE IF NOT EXISTS notificacoes (id SERIAL PRIMARY KEY, usuario_id INTEGER, titulo TEXT, mensagem TEXT, tipo TEXT DEFAULT 'info', lida INTEGER DEFAULT 0, data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        cur.execute("""CREATE TABLE IF NOT EXISTS transacoes (id SERIAL PRIMARY KEY, agendamento_id INTEGER, tipo TEXT, valor REAL, destinatario_id INTEGER, forma_pagamento TEXT, status TEXT DEFAULT 'pendente', data_prevista_liberacao TEXT, data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        cur.execute("""CREATE TABLE IF NOT EXISTS favoritas (id SERIAL PRIMARY KEY, cliente_id INTEGER, manicure_id INTEGER, UNIQUE(cliente_id, manicure_id))""")
        conn.commit()
        cur.execute("DELETE FROM disponibilidade")
        cur.execute("DELETE FROM transacoes")
        cur.execute("DELETE FROM notificacoes")
        cur.execute("DELETE FROM favoritas")
        cur.execute("DELETE FROM agendamentos")
        cur.execute("DELETE FROM servicos")
        cur.execute("DELETE FROM usuarios")
        conn.commit()
        servicos_data = [
            ("Esmalta\u00e7\u00e3o Simples","Acabamento cl\u00e1ssico e impec\u00e1vel",35.0,40,"maos"),
            ("Esmalta\u00e7\u00e3o em Gel","Gel importado de longa dura\u00e7\u00e3o",60.0,50,"maos"),
            ("Unha Decorada","Nail art exclusiva e personalizada",80.0,70,"maos"),
            ("Francesinha","Cl\u00e1ssica e sofisticada",45.0,50,"maos"),
            ("Alongamento Fibra","Fibra de vidro premium",120.0,90,"maos"),
            ("Pedicure Completa","Hidrata\u00e7\u00e3o profunda + esmalta\u00e7\u00e3o",50.0,60,"pes"),
            ("Spa dos P\u00e9s","Esfoliacao + hidrata\u00e7\u00e3o + massagem",70.0,75,"pes"),
            ("Combo M\u00e3os + P\u00e9s","Esmalta\u00e7\u00e3o completa",75.0,90,"combo"),
            ("Combo VIP","Gel + Spa + Hidrata\u00e7\u00e3o completa",130.0,120,"combo"),
            ("Combo Noiva","Pacote exclusivo para noivas",200.0,150,"combo"),
        ]
        for srv in servicos_data:
            cur.execute("INSERT INTO servicos (nome,descricao,preco,duracao_min,categoria) VALUES (%s,%s,%s,%s,%s)", srv)
        senha_admin = HASH_ADMIN
        cur.execute("INSERT INTO usuarios (nome,telefone,email,senha,tipo) VALUES (%s,%s,%s,%s,%s)", ("Fernando Jr","11999999999","fernando@unhaclick.com",senha_admin,"admin"))
        senha_mani = HASH_DEMO
        cur.execute("INSERT INTO usuarios (nome,telefone,email,senha,tipo,especialidades,bio,chave_pix) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id", ("Camila Oliveira","11988887777","camila@unhaclick.com",senha_mani,"manicure","Gel, Fibra, Decora\u00e7\u00e3o, Francesinha","Especialista em nail art h\u00e1 5 anos. Atendimento premium na sua casa.","11988887777"))
        mid = cur.fetchone()["id"]
        for dia in range(0, 6):
            cur.execute("INSERT INTO disponibilidade (manicure_id,dia_semana,hora_inicio,hora_fim) VALUES (%s,%s,%s,%s)", (mid, dia, "08:00", "18:00"))
        senha_cli = HASH_DEMO
        cur.execute("INSERT INTO usuarios (nome,telefone,email,senha,tipo,endereco,bairro,cidade) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", ("Maria Santos","11977776666","maria@demo.com",senha_cli,"cliente","Rua das Flores, 123","Centro","S\u00e3o Paulo"))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        return False

inicializar_banco()

def tela_login():
    st.markdown('<div style="display:flex; flex-direction:column; align-items:center; padding: 80px 0 30px 0;"><div style="width:64px; height:64px; background:#1A1A2E; border-radius:16px; display:flex; align-items:center; justify-content:center; margin-bottom:20px;"><span style="color:white; font-size:24px; font-weight:800;">UC</span></div><h1 style="color:#1A1A2E; font-size:28px; font-weight:800; margin:0; letter-spacing:-0.5px;">Unha Click</h1><p style="color:#6B7280; font-size:14px; margin:8px 0 0 0;">Beleza na ponta dos dedos</p></div>', unsafe_allow_html=True)
    st.markdown("")
    tel = st.text_input("Telefone", placeholder="11999999999")
    senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")
    st.markdown("")
    col1, col2 = st.columns(2)
    with col1:
        login_btn = st.button("Entrar", use_container_width=True, type="primary")
    with col2:
        if st.button("Criar conta", use_container_width=True):
            ir_para("cadastro")
            st.rerun()
    if login_btn:
        if not tel or not senha:
            st.error("Preencha todos os campos.")
            return
        s = gerar_hash(senha)
        resultado = query("SELECT * FROM usuarios WHERE telefone=%s AND senha=%s AND ativo=1", (tel, s))
        if resultado:
            user = resultado[0]
            st.session_state.user_id = user["id"]
            st.session_state.user_nome = user["nome"]
            st.session_state.user_tipo = user["tipo"]
            if user["tipo"] == "admin":
                ir_para("admin")
            elif user["tipo"] == "manicure":
                ir_para("manicure_home")
            else:
                ir_para("cliente_home")
            st.rerun()
        else:
            st.error("Telefone ou senha incorretos.")
    st.markdown('<div style="background:#F9FAFB; border-radius:12px; padding:16px; margin-top:40px; border: 1px solid #F0F0F0;"><p style="color:#9CA3AF; font-size:11px; margin:0; text-align:center; font-weight:500;">CONTAS DEMO</p><p style="color:#6B7280; font-size:12px; margin:8px 0 0 0; text-align:center; line-height:1.8;">Admin: 11999999999 / admin123<br>Profissional: 11988887777 / 1234<br>Cliente: 11977776666 / 1234</p></div>', unsafe_allow_html=True)

def tela_cadastro():
    st.markdown('<div class="header-unha"><h1>Criar conta</h1><p>Junte-se ao Unha Click</p></div>', unsafe_allow_html=True)
    if st.button("Voltar"):
        ir_para("login")
        st.rerun()
    nome = st.text_input("Nome completo")
    tel = st.text_input("Telefone")
    email = st.text_input("E-mail (opcional)")
    senha = st.text_input("Senha", type="password")
    senha2 = st.text_input("Confirmar senha", type="password")
    tipo = st.radio("Voc\u00ea \u00e9:", ["Cliente", "Profissional de unhas"], horizontal=True)
    if st.button("Criar minha conta", use_container_width=True, type="primary"):
        if not nome or not tel or not senha:
            st.error("Preencha nome, telefone e senha.")
            return
        if senha != senha2:
            st.error("As senhas n\u00e3o conferem.")
            return
        tipo_db = "cliente" if tipo == "Cliente" else "manicure"
        s = gerar_hash(senha)
        try:
            execute("INSERT INTO usuarios (nome,telefone,email,senha,tipo) VALUES (%s,%s,%s,%s,%s)", (nome, tel, email, s, tipo_db))
            st.success("Conta criada com sucesso! Fa\u00e7a login.")
            st.balloons()
            ir_para("login")
            st.rerun()
        except Exception as e:
            st.error("Esse telefone j\u00e1 est\u00e1 cadastrado.")

def tela_cliente_home():
    nome_partes = st.session_state.user_nome.split()
    primeiro = nome_partes.pop(0) if nome_partes else st.session_state.user_nome
    st.markdown('<div class="header-unha"><h1>Ol\u00e1, ' + primeiro + '</h1><p>O que vamos fazer hoje?</p></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Agendamentos", use_container_width=True):
            ir_para("meus_agendamentos")
            st.rerun()
    with col2:
        if st.button("Meu perfil", use_container_width=True):
            ir_para("perfil")
            st.rerun()
    with col3:
        if st.button("Sair", use_container_width=True):
            logout()
            st.rerun()
    st.markdown('<p class="section-title">Servi\u00e7os dispon\u00edveis</p>', unsafe_allow_html=True)
    tabs = st.tabs(["M\u00e3os", "P\u00e9s", "Combos"])
    categorias = ["maos", "pes", "combo"]
    for i, cat in enumerate(categorias):
        with tabs[i]:
            servicos = query("SELECT * FROM servicos WHERE categoria=%s AND ativo=1", (cat,))
            for s in servicos:
                st.markdown('<div class="card"><div style="display:flex; align-items:center; justify-content:space-between;"><div><strong style="font-size:15px; color:#1A1A2E;">' + str(s["nome"]) + '</strong><br><span style="color:#6B7280; font-size:13px;">' + str(s["descricao"]) + '</span><br><span style="color:#9CA3AF; font-size:12px;">~' + str(s["duracao_min"]) + ' min</span></div><div style="text-align:right;"><strong style="color:#1A1A2E; font-size:20px;">R$ ' + f'{s["preco"]:.0f}' + '</strong></div></div></div>', unsafe_allow_html=True)
                if st.button("Agendar \u2192", key="srv_" + str(s["id"]), use_container_width=True, type="primary"):
                    ir_para("escolher_manicure", servico_id=s["id"])
                    st.rerun()

def tela_escolher_manicure():
    st.markdown('<div class="header-unha"><h1>Escolher profissional</h1><p>Selecione quem vai cuidar de voc\u00ea</p></div>', unsafe_allow_html=True)
    if st.button("Voltar"):
        ir_para("cliente_home")
        st.rerun()
    favs = query("SELECT manicure_id FROM favoritas WHERE cliente_id=%s", (st.session_state.user_id,))
    fav_ids = [f["manicure_id"] for f in favs]
    manicures = query("SELECT u.*, (SELECT COUNT(*) FROM agendamentos a WHERE a.manicure_id=u.id AND a.status='concluido') as total_atend FROM usuarios u WHERE u.tipo='manicure' AND u.ativo=1 ORDER BY u.avaliacao_media DESC")
    if not manicures:
        st.info("Nenhuma profissional dispon\u00edvel no momento.")
        return
    if fav_ids:
        st.markdown('<p class="section-title">Suas favoritas</p>', unsafe_allow_html=True)
        for m in manicures:
            if m["id"] in fav_ids:
                letra = str(m["nome"])[:1].upper()
                pri = str(m["nome"]).split().pop(0)
                st.markdown('<div class="card-destaque"><div style="display:flex; align-items:center; gap:14px;"><div class="avatar" style="background:linear-gradient(135deg,#B8860B,#D4A853);">' + letra + '</div><div style="flex:1;"><strong style="font-size:15px; color:#1A1A2E;">' + str(m["nome"]) + '</strong><br><span class="estrelas-box">' + estrelas(m["avaliacao_media"] or 5) + '</span> <span style="color:#9CA3AF; font-size:12px;">' + str(m["total_avaliacoes"] or 0) + ' avalia\u00e7\u00f5es</span><br><span style="color:#6B7280; font-size:12px;">' + str(m["bio"] or "") + '</span></div></div></div>', unsafe_allow_html=True)
                if st.button("Agendar com " + pri, key="fav_" + str(m["id"]), use_container_width=True, type="primary"):
                    ir_para("agendar", manicure_id=m["id"])
                    st.rerun()
    st.markdown('<p class="section-title">Todas as profissionais</p>', unsafe_allow_html=True)
    enviar_aberto = st.checkbox("Enviar para todas as dispon\u00edveis (a primeira que aceitar em 1h atende voc\u00ea)")
    st.session_state.aberto_para_todas = enviar_aberto
    for m in manicures:
        letra = str(m["nome"])[:1].upper()
        pri = str(m["nome"]).split().pop(0)
        fav_tag = ' <span style="color:#B8860B; font-size:11px; font-weight:600;">FAVORITA</span>' if m["id"] in fav_ids else ""
        st.markdown('<div class="card"><div style="display:flex; align-items:center; gap:14px;"><div class="avatar" style="background:#1A1A2E;">' + letra + '</div><div style="flex:1;"><strong style="font-size:15px; color:#1A1A2E;">' + str(m["nome"]) + '</strong>' + fav_tag + '<br><span class="estrelas-box">' + estrelas(m["avaliacao_media"] or 5) + '</span> <span style="color:#9CA3AF; font-size:12px;">' + str(m["total_avaliacoes"] or 0) + ' avalia\u00e7\u00f5es</span><br><span style="color:#6B7280; font-size:12px;">' + str(m["endereco"] or "Atende no local") + ' | ' + str(m["total_atend"]) + ' atendimentos</span></div></div><p style="color:#6B7280; font-size:12px; margin:10px 0 0 0; font-style:italic;">' + str(m["bio"] or "") + '</p></div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Agendar com " + pri, key="man_" + str(m["id"]), use_container_width=True, type="primary"):
                ir_para("agendar", manicure_id=m["id"])
                st.rerun()
        with col2:
            if m["id"] not in fav_ids:
                if st.button("Favoritar", key="favbtn_" + str(m["id"]), use_container_width=True):
                    execute("INSERT INTO favoritas (cliente_id, manicure_id) VALUES (%s,%s) ON CONFLICT DO NOTHING", (st.session_state.user_id, m["id"]))
                    st.rerun()

def tela_agendar():
    servico_list = query("SELECT * FROM servicos WHERE id=%s", (st.session_state.servico_id,))
    manicure_list = query("SELECT * FROM usuarios WHERE id=%s", (st.session_state.manicure_id,))
    if not servico_list or not manicure_list:
        st.error("Erro ao carregar dados.")
        ir_para("cliente_home")
        st.rerun()
        return
    servico = servico_list[0]
    manicure = manicure_list[0]
    st.markdown('<div class="header-unha"><h1>Agendar</h1><p>' + str(servico["nome"]) + ' com ' + str(manicure["nome"]) + '</p></div>', unsafe_allow_html=True)
    if st.button("Voltar"):
        ir_para("escolher_manicure")
        st.rerun()
    valor_total = servico["preco"]
    valor_manicure = valor_total * (1 - COMISSAO)
    duracao = servico["duracao_min"]
    st.markdown('<div class="card-destaque" style="text-align:center;"><h3 style="margin:0 0 4px 0; color:#1A1A2E;">' + str(servico["nome"]) + '</h3><p style="color:#6B7280; margin:0 0 12px 0;">~' + str(duracao) + ' minutos</p><p style="font-size:28px; font-weight:800; color:#1A1A2E; margin:0;">R$ ' + f'{valor_total:.2f}' + '</p></div>', unsafe_allow_html=True)
    disponibilidades = query("SELECT * FROM disponibilidade WHERE manicure_id=%s AND ativo=1", (st.session_state.manicure_id,))
    dias_semana_disp = set()
    for d in disponibilidades:
        dias_semana_disp.add(d["dia_semana"])
    hoje = date.today()
    agendados = query("SELECT a.data, a.horario, s.duracao_min FROM agendamentos a JOIN servicos s ON a.servico_id=s.id WHERE a.manicure_id=%s AND a.status IN ('pendente','confirmado','em_andamento') AND a.data >= %s", (st.session_state.manicure_id, hoje.strftime("%d/%m/%Y")))
    dias_disp = []
    for i in range(1, 31):
        dia = hoje + timedelta(days=i)
        if dia.weekday() in dias_semana_disp:
            dias_disp.append(dia)
    st.markdown('<p class="section-title">Data</p>', unsafe_allow_html=True)
    data_opcoes = {}
    for dia in dias_disp[:20]:
        label = dia.strftime("%d/%m/%Y (%a)")
        data_opcoes[label] = dia
    data_str = st.selectbox("Data dispon\u00edvel:", list(data_opcoes.keys()))
    data_sel = data_opcoes.get(data_str)
    horario_sel = None
    if data_sel:
        disp = [d for d in disponibilidades if d["dia_semana"] == data_sel.weekday()]
        if disp:
            d_info = disp[0]
            partes_inicio = d_info["hora_inicio"].split(":")
            h_inicio = int(partes_inicio[0])
            m_inicio = int(partes_inicio[1])
            partes_fim = d_info["hora_fim"].split(":")
            h_fim = int(partes_fim[0])
            m_fim = int(partes_fim[1])
            data_str_br = data_sel.strftime("%d/%m/%Y")
            ocupados = set()
            for ag in agendados:
                if ag["data"] == data_str_br:
                    partes_h = ag["horario"].split(":")
                    h = int(partes_h[0])
                    m = int(partes_h[1])
                    for off in range(0, ag["duracao_min"], 30):
                        ocupados.add(h * 60 + m + off)
            horarios_livres = []
            current = h_inicio * 60 + m_inicio
            end = h_fim * 60 + m_fim
            while current + duracao <= end:
                livre = True
                for off in range(0, duracao, 30):
                    if (current + off) in ocupados:
                        livre = False
                        break
                if livre:
                    hh = current // 60
                    mm = current % 60
                    horarios_livres.append(f"{hh:02d}:{mm:02d}")
                current += 30
            st.markdown('<p class="section-title">Hor\u00e1rio</p>', unsafe_allow_html=True)
            if horarios_livres:
                horario_sel = st.selectbox("Hor\u00e1rios dispon\u00edveis:", horarios_livres)
            else:
                st.warning("Sem hor\u00e1rios livres nesta data.")
    st.markdown('<p class="section-title">Local de atendimento</p>', unsafe_allow_html=True)
    endereco = st.text_input("Endere\u00e7o completo")
    complemento = st.text_input("Complemento (apto, bloco...)")
    st.markdown('<p class="section-title">Forma de pagamento</p>', unsafe_allow_html=True)
    forma_pg = st.radio("Escolha:", ["PIX", "Cart\u00e3o de Cr\u00e9dito", "Cart\u00e3o de D\u00e9bito", "Dinheiro"], horizontal=True)
    formas_map = {"PIX": "pix", "Cart\u00e3o de Cr\u00e9dito": "cartao_credito", "Cart\u00e3o de D\u00e9bito": "cartao_debito", "Dinheiro": "dinheiro"}
    obs = st.text_area("Observa\u00e7\u00f5es (opcional)")
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="card" style="border: 1.5px solid #1A1A2E;"><p style="font-size:12px; font-weight:700; color:#9CA3AF; text-transform:uppercase; letter-spacing:0.5px; margin:0 0 12px 0;">Resumo</p><p style="color:#1A1A2E; font-size:14px; margin:0; line-height:2;"><strong>Servi\u00e7o:</strong> ' + str(servico["nome"]) + '<br><strong>Profissional:</strong> ' + str(manicure["nome"]) + '<br><strong>Data:</strong> ' + str(data_str) + '<br><strong>Hor\u00e1rio:</strong> ' + str(horario_sel or "-") + '<br><strong>Pagamento:</strong> ' + str(forma_pg) + '</p><div class="divider"></div><p style="font-size:28px; font-weight:800; color:#1A1A2E; text-align:center; margin:0;">R$ ' + f'{valor_total:.2f}' + '</p></div>', unsafe_allow_html=True)
    if st.button("Confirmar agendamento", use_container_width=True, type="primary"):
        if not horario_sel:
            st.error("Selecione um hor\u00e1rio.")
            return
        if not endereco:
            st.error("Informe o endere\u00e7o.")
            return
        data_br = data_sel.strftime("%d/%m/%Y")
        data_lib = (data_sel + timedelta(days=DIAS_RECEBER)).strftime("%d/%m/%Y")
        fp = formas_map.get(forma_pg, "pix")
        aberto = 1 if st.session_state.get("aberto_para_todas", False) else 0
        hora_limite = datetime.now() + timedelta(hours=TEMPO_ACEITE_HORAS)
        result = execute_returning("INSERT INTO agendamentos (cliente_id,manicure_id,servico_id,data,horario,endereco_atendimento,complemento,valor_total,valor_manicure,valor_comissao,forma_pagamento,observacoes,data_liberacao_manicure,aberto_para_todas,hora_limite_aceite,status) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id", (st.session_state.user_id, st.session_state.manicure_id, st.session_state.servico_id, data_br, horario_sel, endereco, complemento, valor_total, valor_manicure, valor_total * COMISSAO, fp, obs, data_lib, aberto, hora_limite, "aguardando_aceite" if aberto else "pendente"))
        if result:
            ag_id = result["id"]
            execute("INSERT INTO transacoes (agendamento_id,tipo,valor,destinatario_id,forma_pagamento,data_prevista_liberacao) VALUES (%s,%s,%s,%s,%s,%s)", (ag_id, "pagamento", valor_total, st.session_state.manicure_id, fp, data_lib))
            execute("INSERT INTO notificacoes (usuario_id,titulo,mensagem,tipo) VALUES (%s,%s,%s,%s)", (st.session_state.manicure_id, "Novo agendamento", "Agendamento para " + data_br + " \u00e0s " + horario_sel + ". Aceite em 1 hora.", "agendamento"))
            st.session_state.ultimo_agendamento = ag_id
            ir_para("confirmacao")
            st.rerun()

def tela_confirmacao():
    ag_id = st.session_state.get("ultimo_agendamento")
    resultado = query("SELECT a.*, s.nome as sn, u.nome as mn FROM agendamentos a JOIN servicos s ON a.servico_id=s.id JOIN usuarios u ON a.manicure_id=u.id WHERE a.id=%s", (ag_id,))
    if not resultado:
        ir_para("cliente_home")
        st.rerun()
        return
    ag = resultado[0]
    st.markdown('<div style="text-align:center; padding:60px 0 20px 0;"><div style="width:64px; height:64px; background:#D1FAE5; border-radius:50%; display:flex; align-items:center; justify-content:center; margin:0 auto 20px auto;"><span style="color:#065F46; font-size:28px; font-weight:800;">\u2713</span></div><h2 style="color:#1A1A2E; font-weight:800; margin:0;">Agendamento confirmado</h2><p style="color:#6B7280; font-size:14px; margin:8px 0 0 0;">A profissional tem 1 hora para aceitar.</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="card" style="border: 1.5px solid var(--border);"><p style="color:#1A1A2E; font-size:14px; margin:0; line-height:2;"><strong>Servi\u00e7o:</strong> ' + str(ag["sn"]) + '<br><strong>Profissional:</strong> ' + str(ag["mn"]) + '<br><strong>Data:</strong> ' + str(ag["data"]) + '<br><strong>Hor\u00e1rio:</strong> ' + str(ag["horario"]) + '<br><strong>Local:</strong> ' + str(ag["endereco_atendimento"]) + '<br><strong>Pagamento:</strong> ' + nome_pagamento(ag["forma_pagamento"]) + '</p><div class="divider"></div><p style="font-size:28px; font-weight:800; color:#1A1A2E; text-align:center; margin:0;">R$ ' + f'{ag["valor_total"]:.2f}' + '</p></div>', unsafe_allow_html=True)
    if st.button("Voltar ao in\u00edcio", use_container_width=True, type="primary"):
        ir_para("cliente_home")
        st.rerun()

def tela_meus_agendamentos():
    st.markdown('<div class="header-unha"><h1>Meus agendamentos</h1></div>', unsafe_allow_html=True)
    if st.button("Voltar"):
        ir_para("cliente_home")
        st.rerun()
    agendamentos = query("SELECT a.*, s.nome as sn, u.nome as mn FROM agendamentos a JOIN servicos s ON a.servico_id=s.id JOIN usuarios u ON a.manicure_id=u.id WHERE a.cliente_id=%s ORDER BY a.data_criacao DESC LIMIT 20", (st.session_state.user_id,))
    if not agendamentos:
        st.markdown('<div style="text-align:center; padding:60px 0;"><p style="color:#9CA3AF; font-size:14px;">Nenhum agendamento ainda.</p></div>', unsafe_allow_html=True)
    else:
        for ag in agendamentos:
            st.markdown('<div class="card"><div style="display:flex; justify-content:space-between; align-items:center;"><div><strong style="color:#1A1A2E;">' + str(ag["sn"]) + '</strong><br><span style="color:#6B7280; font-size:13px;">com ' + str(ag["mn"]) + '</span><br><span style="color:#9CA3AF; font-size:12px;">' + str(ag["data"]) + ' \u00e0s ' + str(ag["horario"]) + '</span></div><div style="text-align:right;">' + tag_status(ag["status"]) + '<br><strong style="color:#1A1A2E; font-size:18px; margin-top:4px; display:inline-block;">R$ ' + f'{ag["valor_total"]:.2f}' + '</strong></div></div></div>', unsafe_allow_html=True)
            if ag["status"] == "concluido" and ag["avaliacao_nota"] is None:
                if st.button("Avaliar", key="aval_" + str(ag["id"]), use_container_width=True):
                    ir_para("avaliar", avaliando_id=ag["id"])
                    st.rerun()

def tela_avaliar():
    ag_id = st.session_state.get("avaliando_id")
    resultado = query("SELECT a.*, s.nome as sn, u.nome as mn FROM agendamentos a JOIN servicos s ON a.servico_id=s.id JOIN usuarios u ON a.manicure_id=u.id WHERE a.id=%s", (ag_id,))
    if not resultado:
        ir_para("cliente_home")
        st.rerun()
        return
    ag = resultado[0]
    st.markdown('<div class="header-unha"><h1>Avaliar</h1><p>' + str(ag["sn"]) + ' com ' + str(ag["mn"]) + '</p></div>', unsafe_allow_html=True)
    if st.button("Voltar"):
        ir_para("meus_agendamentos")
        st.rerun()
    st.markdown('<p class="section-title">Como foi sua experi\u00eancia?</p>', unsafe_allow_html=True)
    nota = st.slider("Nota:", 1, 5, 5)
    textos = {1: "P\u00e9ssimo", 2: "Ruim", 3: "Regular", 4: "Bom", 5: "Excelente"}
    st.markdown('<h2 style="text-align:center; color:#1A1A2E; font-weight:800;">' + textos[nota] + '</h2>', unsafe_allow_html=True)
    comentario = st.text_area("Conte como foi (opcional)")
    if st.button("Enviar avalia\u00e7\u00e3o", use_container_width=True, type="primary"):
        execute("UPDATE agendamentos SET avaliacao_nota=%s, avaliacao_comentario=%s WHERE id=%s", (nota, comentario, ag_id))
        media_result = query("SELECT AVG(avaliacao_nota) as media, COUNT(*) as total FROM agendamentos WHERE manicure_id=%s AND avaliacao_nota IS NOT NULL", (ag["manicure_id"],))
        if media_result:
            mr = media_result[0]
            execute("UPDATE usuarios SET avaliacao_media=%s, total_avaliacoes=%s WHERE id=%s", (mr["media"] or 5, mr["total"] or 0, ag["manicure_id"]))
        execute("INSERT INTO favoritas (cliente_id, manicure_id) VALUES (%s,%s) ON CONFLICT DO NOTHING", (st.session_state.user_id, ag["manicure_id"]))
        execute("INSERT INTO notificacoes (usuario_id,titulo,mensagem,tipo) VALUES (%s,%s,%s,%s)", (ag["manicure_id"], "Nova avalia\u00e7\u00e3o: " + str(nota) + " estrelas", comentario or "Sem coment\u00e1rio", "avaliacao"))
        st.success("Avalia\u00e7\u00e3o enviada!")
        ir_para("cliente_home")
        st.rerun()

def tela_perfil():
    resultado = query("SELECT * FROM usuarios WHERE id=%s", (st.session_state.user_id,))
    if not resultado:
        ir_para("cliente_home")
        st.rerun()
        return
    user = resultado[0]
    st.markdown('<div class="header-unha"><h1>Meu perfil</h1></div>', unsafe_allow_html=True)
    if st.button("Voltar"):
        ir_para("cliente_home")
        st.rerun()
    letra = str(user["nome"])[:1].upper()
    st.markdown('<div class="card" style="text-align:center; padding:30px;"><div class="avatar" style="background:#1A1A2E; width:72px; height:72px; font-size:28px; border-radius:20px; margin:0 auto 16px auto;">' + letra + '</div><h2 style="margin:0; color:#1A1A2E; font-weight:800;">' + str(user["nome"]) + '</h2><div class="divider"></div><p style="color:#6B7280; font-size:14px; line-height:2; margin:0; text-align:left;"><strong>Telefone:</strong> ' + str(user["telefone"]) + '<br><strong>E-mail:</strong> ' + str(user["email"] or "N\u00e3o informado") + '<br><strong>Endere\u00e7o:</strong> ' + str(user["endereco"] or "N\u00e3o informado") + '</p></div>', unsafe_allow_html=True)

def tela_manicure_home():
    hoje = date.today().strftime("%d/%m/%Y")
    nome_partes = st.session_state.user_nome.split()
    primeiro_nome = nome_partes.pop(0) if nome_partes else st.session_state.user_nome
    st.markdown('<div class="header-unha"><h1>Ol\u00e1, ' + primeiro_nome + '</h1><p>Painel da profissional</p></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Notifica\u00e7\u00f5es", use_container_width=True):
            pass
    with col2:
        if st.button("Sair", use_container_width=True):
            logout()
            st.rerun()
    mes_atual = date.today().strftime("%m/%Y")
    ganhos_result = query("SELECT COALESCE(SUM(valor_manicure),0) as ganhos, COUNT(*) as total FROM agendamentos WHERE manicure_id=%s AND status='concluido' AND data LIKE %s", (st.session_state.user_id, "%" + mes_atual))
    gr = ganhos_result[0] if ganhos_result else {"ganhos": 0, "total": 0}
    receber_result = query("SELECT COALESCE(SUM(valor_manicure),0) as valor FROM agendamentos WHERE manicure_id=%s AND status='concluido' AND pago=0", (st.session_state.user_id,))
    rr = receber_result[0] if receber_result else {"valor": 0}
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="kpi-box"><div class="kpi-label">Ganhos do m\u00eas</div><div class="kpi-valor" style="color:#10B981;">R$ ' + f'{gr["ganhos"]:.2f}' + '</div><div class="kpi-label">' + str(gr["total"]) + ' atendimentos</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="kpi-box"><div class="kpi-label">A receber</div><div class="kpi-valor" style="color:#1A1A2E;">R$ ' + f'{rr["valor"]:.2f}' + '</div><div class="kpi-label">Libera\u00e7\u00e3o em ' + str(DIAS_RECEBER) + ' dias</div></div>', unsafe_allow_html=True)
    pendentes = query("SELECT a.*, s.nome as sn, u.nome as cn FROM agendamentos a JOIN servicos s ON a.servico_id=s.id JOIN usuarios u ON a.cliente_id=u.id WHERE a.manicure_id=%s AND a.status IN ('pendente','aguardando_aceite') ORDER BY a.data_criacao DESC", (st.session_state.user_id,))
    if pendentes:
        st.markdown('<p class="section-title">Aguardando sua confirma\u00e7\u00e3o</p>', unsafe_allow_html=True)
        for ag in pendentes:
            st.markdown('<div class="card-destaque"><strong style="color:#1A1A2E;">' + str(ag["sn"]) + '</strong><br><span style="color:#6B7280; font-size:13px;">Cliente: ' + str(ag["cn"]) + '</span><br><span style="color:#9CA3AF; font-size:12px;">' + str(ag["data"]) + ' \u00e0s ' + str(ag["horario"]) + '</span><br><span style="color:#9CA3AF; font-size:12px;">' + str(ag["endereco_atendimento"] or "-") + '</span><br><strong style="color:#10B981;">Voc\u00ea recebe: R$ ' + f'{ag["valor_manicure"]:.2f}' + '</strong></div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Aceitar", key="aceitar_" + str(ag["id"]), use_container_width=True, type="primary"):
                    execute("UPDATE agendamentos SET status='confirmado' WHERE id=%s", (ag["id"],))
                    execute("INSERT INTO notificacoes (usuario_id,titulo,mensagem,tipo) VALUES (%s,%s,%s,%s)", (ag["cliente_id"], "Agendamento aceito", str(ag["sn"]) + " confirmado para " + str(ag["data"]), "agendamento"))
                    st.rerun()
            with c2:
                if st.button("Recusar", key="recusar_" + str(ag["id"]), use_container_width=True):
                    execute("UPDATE agendamentos SET status='cancelado' WHERE id=%s", (ag["id"],))
                    execute("INSERT INTO notificacoes (usuario_id,titulo,mensagem,tipo) VALUES (%s,%s,%s,%s)", (ag["cliente_id"], "Agendamento recusado", "Procure outra profissional.", "agendamento"))
                    st.rerun()
    st.markdown('<p class="section-title">Hoje (' + hoje + ')</p>', unsafe_allow_html=True)
    hoje_ag = query("SELECT a.*, s.nome as sn, u.nome as cn FROM agendamentos a JOIN servicos s ON a.servico_id=s.id JOIN usuarios u ON a.cliente_id=u.id WHERE a.manicure_id=%s AND a.data=%s AND a.status IN ('confirmado','em_andamento') ORDER BY a.horario", (st.session_state.user_id, hoje))
    if not hoje_ag:
        st.markdown('<div style="text-align:center; padding:20px;"><p style="color:#9CA3AF; font-size:13px;">Nenhum atendimento hoje.</p></div>', unsafe_allow_html=True)
    else:
        for ag in hoje_ag:
            st.markdown('<div class="card"><strong style="color:#1A1A2E;">' + str(ag["horario"]) + '</strong> ' + tag_status(ag["status"]) + '<br><span style="color:#6B7280; font-size:13px;">' + str(ag["sn"]) + ' | ' + str(ag["cn"]) + '</span><br><span style="color:#9CA3AF; font-size:12px;">' + str(ag["endereco_atendimento"] or "-") + '</span><br><strong style="color:#10B981;">R$ ' + f'{ag["valor_manicure"]:.2f}' + '</strong></div>', unsafe_allow_html=True)
            if ag["status"] == "confirmado":
                if st.button("Concluir", key="conc_" + str(ag["id"]), use_container_width=True, type="primary"):
                    execute("UPDATE agendamentos SET status='concluido' WHERE id=%s", (ag["id"],))
                    execute("INSERT INTO notificacoes (usuario_id,titulo,mensagem,tipo) VALUES (%s,%s,%s,%s)", (ag["cliente_id"], "Atendimento conclu\u00eddo", "Avalie sua experi\u00eancia!", "avaliacao"))
                    st.rerun()
    st.markdown('<p class="section-title">Pr\u00f3ximos</p>', unsafe_allow_html=True)
    proximos = query("SELECT a.*, s.nome as sn, u.nome as cn FROM agendamentos a JOIN servicos s ON a.servico_id=s.id JOIN usuarios u ON a.cliente_id=u.id WHERE a.manicure_id=%s AND a.status='confirmado' AND a.data > %s ORDER BY a.data, a.horario LIMIT 10", (st.session_state.user_id, hoje))
    if not proximos:
        st.markdown('<p style="color:#9CA3AF; font-size:13px; text-align:center;">Nenhum agendamento futuro.</p>', unsafe_allow_html=True)
    else:
        for ag in proximos:
            st.markdown('<div class="card"><strong style="color:#1A1A2E;">' + str(ag["data"]) + ' \u00e0s ' + str(ag["horario"]) + '</strong><br><span style="color:#6B7280; font-size:13px;">' + str(ag["sn"]) + ' | ' + str(ag["cn"]) + '</span><br><strong style="color:#10B981;">R$ ' + f'{ag["valor_manicure"]:.2f}' + '</strong></div>', unsafe_allow_html=True)

def tela_admin():
    st.markdown('<div style="background:#1A1A2E; padding: 40px 24px 30px 24px; border-bottom: none; margin: -6rem -1rem 2rem -1rem; text-align:left;"><h1 style="color:white !important; font-size:28px !important; margin:0 !important; font-weight:800 !important;">Painel administrativo</h1><p style="color:#9CA3AF; font-size:14px;">Unha Click</p></div>', unsafe_allow_html=True)
    if st.button("Sair"):
        logout()
        st.rerun()
    stats = query("SELECT (SELECT COUNT(*) FROM usuarios WHERE tipo='cliente') as clientes, (SELECT COUNT(*) FROM usuarios WHERE tipo='manicure') as manicures, (SELECT COUNT(*) FROM agendamentos) as agendamentos, (SELECT COALESCE(SUM(valor_total),0) FROM agendamentos WHERE status='concluido') as faturamento, (SELECT COALESCE(SUM(valor_comissao),0) FROM agendamentos WHERE status='concluido') as comissao")
    s = stats[0] if stats else {"clientes": 0, "manicures": 0, "agendamentos": 0, "faturamento": 0, "comissao": 0}
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="kpi-box"><div class="kpi-label">Clientes</div><div class="kpi-valor" style="color:#1A1A2E;">' + str(s["clientes"]) + '</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="kpi-box"><div class="kpi-label">Profissionais</div><div class="kpi-valor" style="color:#1A1A2E;">' + str(s["manicures"]) + '</div></div>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        st.markdown('<div class="kpi-box"><div class="kpi-label">Agendamentos</div><div class="kpi-valor" style="color:#6366F1;">' + str(s["agendamentos"]) + '</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="kpi-box"><div class="kpi-label">Faturamento</div><div class="kpi-valor" style="color:#10B981;">R$ ' + f'{s["faturamento"]:.0f}' + '</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="card-destaque" style="text-align:center; margin-top:12px;"><p class="kpi-label" style="margin:0 0 4px 0;">Sua comiss\u00e3o (20%)</p><p style="font-size:32px; font-weight:800; color:#B8860B; margin:0;">R$ ' + f'{s["comissao"]:.2f}' + '</p></div>', unsafe_allow_html=True)
    st.markdown('<p class="section-title">\u00daltimos agendamentos</p>', unsafe_allow_html=True)
    ultimos = query("SELECT a.*, s.nome as sn, u1.nome as cn, u2.nome as mn FROM agendamentos a JOIN servicos s ON a.servico_id=s.id JOIN usuarios u1 ON a.cliente_id=u1.id JOIN usuarios u2 ON a.manicure_id=u2.id ORDER BY a.data_criacao DESC LIMIT 10")
    for a in ultimos:
        st.markdown('<div class="card"><div style="display:flex; justify-content:space-between; align-items:center;"><div><strong style="color:#1A1A2E;">' + str(a["sn"]) + '</strong><br><span style="color:#6B7280; font-size:13px;">' + str(a["cn"]) + ' \u2192 ' + str(a["mn"]) + '</span><br><span style="color:#9CA3AF; font-size:12px;">' + str(a["data"]) + ' \u00e0s ' + str(a["horario"]) + '</span></div><div style="text-align:right;">' + tag_status(a["status"]) + '<br><strong style="color:#1A1A2E;">R$ ' + f'{a["valor_total"]:.2f}' + '</strong></div></div></div>', unsafe_allow_html=True)

telas = {"login": tela_login, "cadastro": tela_cadastro, "cliente_home": tela_cliente_home, "escolher_manicure": tela_escolher_manicure, "agendar": tela_agendar, "confirmacao": tela_confirmacao, "meus_agendamentos": tela_meus_agendamentos, "avaliar": tela_avaliar, "perfil": tela_perfil, "manicure_home": tela_manicure_home, "admin": tela_admin}
tela_atual = st.session_state.get("tela", "login")
if tela_atual in telas:
    telas[tela_atual]()
else:
    tela_login()

