
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

st.set_page_config(page_title="Unha Click", page_icon="💅", layout="centered")

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
* {font-family: 'Poppins', sans-serif !important;}
.stApp {background: linear-gradient(135deg, #FFF5F7 0%, #FFF0F3 50%, #FFFAF5 100%);}
.header-unha {background: linear-gradient(135deg, #C48B9F 0%, #D4A0B0 50%, #E8C4C8 100%); padding: 30px 20px; border-radius: 0 0 30px 30px; margin: -6rem -1rem 1.5rem -1rem; text-align:center; box-shadow: 0 8px 32px rgba(196,139,159,0.3);}
.header-unha h1 {color:white !important; font-size:32px !important; margin:0 !important; font-weight:700 !important; letter-spacing: -0.5px;}
.header-unha p {color:#FFF5F7 !important; font-size:14px !important; margin:5px 0 0 0 !important; font-weight:300;}
.card {background: white; border-radius: 20px; padding: 20px; margin: 12px 0; box-shadow: 0 4px 20px rgba(0,0,0,0.06); border: 1px solid rgba(196,139,159,0.1); transition: transform 0.2s, box-shadow 0.2s;}
.card:hover {transform: translateY(-2px); box-shadow: 0 8px 30px rgba(196,139,159,0.15);}
.card-gold {background: linear-gradient(135deg, #FFFAF0 0%, #FFF8E7 100%); border-radius: 20px; padding: 20px; margin: 12px 0; box-shadow: 0 4px 20px rgba(212,168,83,0.12); border: 1px solid rgba(212,168,83,0.2);}
.kpi-box {background: white; border-radius: 20px; padding: 20px; text-align:center; box-shadow: 0 4px 20px rgba(0,0,0,0.06); border: 1px solid rgba(196,139,159,0.1);}
.kpi-valor {font-size: 28px; font-weight: 700; margin: 8px 0;}
.kpi-label {font-size: 13px; color: #888; font-weight: 400;}
.badge {padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 600; letter-spacing: 0.5px;}
.badge-pendente {background: #FFF3E0; color: #E65100;}
.badge-confirmado {background: #E8F5E9; color: #2E7D32;}
.badge-concluido {background: #E3F2FD; color: #1565C0;}
.badge-cancelado {background: #FFEBEE; color: #C62828;}
.badge-aguardando {background: #F3E5F5; color: #7B1FA2;}
.estrelas {color: #FFB800; font-size: 16px; letter-spacing: 2px;}
.btn-rosa > button {background: linear-gradient(135deg, #C48B9F, #D4A0B0) !important; color: white !important; border: none !important; border-radius: 15px !important; font-weight: 600 !important; letter-spacing: 0.3px;}
.btn-gold > button {background: linear-gradient(135deg, #B8860B, #D4A853) !important; color: white !important; border: none !important; border-radius: 15px !important; font-weight: 600 !important;}
.stButton > button {border-radius: 15px !important; font-weight: 500 !important; padding: 8px 20px !important; transition: all 0.3s !important;}
.stButton > button:hover {transform: translateY(-1px) !important; box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;}
div[data-testid="stTextInput"] > div > div > input {border-radius: 15px !important; border: 2px solid rgba(196,139,159,0.2) !important; padding: 10px 15px !important;}
div[data-testid="stTextInput"] > div > div > input:focus {border-color: #C48B9F !important; box-shadow: 0 0 0 3px rgba(196,139,159,0.1) !important;}
.foto-manicure {width: 60px; height: 60px; border-radius: 50%; object-fit: cover; border: 3px solid #C48B9F;}
.servico-icon {font-size: 40px; display: block; text-align: center; margin-bottom: 8px;}
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
    return "★" * n + "☆" * (5 - n)

def badge_html(status):
    nomes = {"pendente": "⏳ Pendente", "confirmado": "✅ Confirmado", "concluido": "🎉 Concluido", "cancelado": "❌ Cancelado", "aguardando_aceite": "🔔 Aguardando"}
    return '<span class="badge badge-' + status.replace("aguardando_aceite", "aguardando") + '">' + nomes.get(status, status) + '</span>'

def forma_pg_nome(fp):
    nomes = {"pix": "PIX", "cartao_credito": "Cartao de Credito", "cartao_debito": "Cartao de Debito", "dinheiro": "Dinheiro"}
    return nomes.get(fp, fp)

@st.cache_resource
def inicializar_banco():
    try:
        conn = get_new_connection()
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS usuarios (id SERIAL PRIMARY KEY, nome TEXT NOT NULL, telefone TEXT UNIQUE NOT NULL, email TEXT, senha TEXT NOT NULL, tipo TEXT DEFAULT 'cliente', endereco TEXT, bairro TEXT, cidade TEXT, estado TEXT DEFAULT 'SP', foto TEXT, avaliacao_media REAL DEFAULT 5.0, total_avaliacoes INTEGER DEFAULT 0, especialidades TEXT, bio TEXT, chave_pix TEXT, banco TEXT, ativo INTEGER DEFAULT 1, data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        cur.execute("""CREATE TABLE IF NOT EXISTS servicos (id SERIAL PRIMARY KEY, nome TEXT NOT NULL, descricao TEXT, preco REAL NOT NULL, duracao_min INTEGER DEFAULT 60, categoria TEXT DEFAULT 'maos', icone TEXT DEFAULT '💅', ativo INTEGER DEFAULT 1)""")
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
        for srv in [("Esmaltacao Simples","Esmaltacao classica com acabamento premium",35.0,40,"maos","💅"),("Esmaltacao em Gel","Gel importado de longa duracao",60.0,50,"maos","✨"),("Unha Decorada","Nail art exclusiva e personalizada",80.0,70,"maos","🎨"),("Francesinha","Classica e sofisticada francesinha",45.0,50,"maos","🤍"),("Alongamento Fibra","Fibra de vidro premium",120.0,90,"maos","💎"),("Pedicure Completa","Hidratacao profunda + esmaltacao",50.0,60,"pes","🦶"),("Spa dos Pes","Esfoliacao + hidratacao + massagem",70.0,75,"pes","🧖"),("Combo Maos + Pes","Esmaltacao completa maos e pes",75.0,90,"combo","👑"),("Combo VIP","Gel + Spa + Hidratacao completa",130.0,120,"combo","🌟"),("Combo Noiva","Pacote exclusivo para noivas",200.0,150,"combo","💒")]:
            cur.execute("INSERT INTO servicos (nome,descricao,preco,duracao_min,categoria,icone) VALUES (%s,%s,%s,%s,%s,%s)", srv)
        senha_admin = HASH_ADMIN
        cur.execute("INSERT INTO usuarios (nome,telefone,email,senha,tipo) VALUES (%s,%s,%s,%s,%s)", ("Fernando Jr","11999999999","fernando@unhaclick.com",senha_admin,"admin"))
        senha_mani = HASH_DEMO
        cur.execute("INSERT INTO usuarios (nome,telefone,email,senha,tipo,especialidades,bio,chave_pix) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id", ("Ana Silva","11988887777","ana@unhaclick.com",senha_mani,"manicure","Gel, Fibra, Decoracao, Francesinha","Especialista em nail art com 5 anos de experiencia! Apaixonada por unhas perfeitas.","11988887777"))
        mid = cur.fetchone()["id"]
        for dia in range(0, 6):
            cur.execute("INSERT INTO disponibilidade (manicure_id,dia_semana,hora_inicio,hora_fim) VALUES (%s,%s,%s,%s)", (mid, dia, "08:00", "18:00"))
        senha_cli = HASH_DEMO
        cur.execute("INSERT INTO usuarios (nome,telefone,email,senha,tipo,endereco,bairro,cidade) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", ("Maria Demo","11977776666","maria@demo.com",senha_cli,"cliente","Rua das Flores, 123","Centro","Sao Paulo"))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        return False

inicializar_banco()

def tela_login():
    st.markdown('<div style="text-align:center; padding: 60px 0 20px 0;"><div style="font-size:80px;">💅</div><h1 style="color:#C48B9F; font-size:36px; font-weight:700; margin:10px 0 5px 0;">Unha Click</h1><p style="color:#999; font-size:14px; font-weight:300;">Beleza na ponta dos dedos</p></div>', unsafe_allow_html=True)
    st.markdown("")
    tel = st.text_input("📱 Telefone", placeholder="11999999999")
    senha = st.text_input("🔒 Senha", type="password", placeholder="Digite sua senha")
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
            st.error("Preencha todos os campos!")
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
            st.error("📱 Telefone ou senha incorretos!")
    st.markdown('<div style="background:rgba(196,139,159,0.08); border-radius:15px; padding:15px; margin-top:30px; text-align:center;"><p style="color:#999; font-size:12px; margin:0;">Logins Demo</p><p style="color:#888; font-size:11px; margin:5px 0 0 0;">Admin: 11999999999 / admin123<br>Manicure: 11988887777 / 1234<br>Cliente: 11977776666 / 1234</p></div>', unsafe_allow_html=True)

def tela_cadastro():
    st.markdown('<div class="header-unha"><h1>Criar Conta</h1><p>Junte-se ao Unha Click</p></div>', unsafe_allow_html=True)
    if st.button("← Voltar"):
        ir_para("login")
        st.rerun()
    nome = st.text_input("👤 Nome completo")
    tel = st.text_input("📱 Telefone")
    email = st.text_input("📧 Email (opcional)")
    senha = st.text_input("🔒 Senha", type="password")
    senha2 = st.text_input("🔒 Confirmar senha", type="password")
    tipo = st.radio("Voce e:", ["Cliente", "Profissional de unhas"], horizontal=True)
    if st.button("Criar minha conta", use_container_width=True, type="primary"):
        if not nome or not tel or not senha:
            st.error("Preencha nome, telefone e senha!")
            return
        if senha != senha2:
            st.error("Senhas nao conferem!")
            return
        tipo_db = "cliente" if tipo == "Cliente" else "manicure"
        s = gerar_hash(senha)
        try:
            execute("INSERT INTO usuarios (nome,telefone,email,senha,tipo) VALUES (%s,%s,%s,%s,%s)", (nome, tel, email, s, tipo_db))
            st.success("Conta criada! Faca login.")
            st.balloons()
            ir_para("login")
            st.rerun()
        except Exception as e:
            st.error("Telefone ja cadastrado!")

def tela_cliente_home():
    nome_partes = st.session_state.user_nome.split()
    primeiro = nome_partes.pop(0) if nome_partes else st.session_state.user_nome
    st.markdown('<div class="header-unha"><h1>Ola, ' + primeiro + '! 👋</h1><p>O que vamos fazer hoje?</p></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📋 Agendamentos", use_container_width=True):
            ir_para("meus_agendamentos")
            st.rerun()
    with col2:
        if st.button("👤 Perfil", use_container_width=True):
            ir_para("perfil")
            st.rerun()
    with col3:
        if st.button("🚪 Sair", use_container_width=True):
            logout()
            st.rerun()
    st.markdown("### 💅 Servicos Disponiveis")
    tabs = st.tabs(["🖐 Maos", "🦶 Pes", "👑 Combos"])
    categorias = ["maos", "pes", "combo"]
    for i, cat in enumerate(categorias):
        with tabs[i]:
            servicos = query("SELECT * FROM servicos WHERE categoria=%s AND ativo=1", (cat,))
            for s in servicos:
                st.markdown('<div class="card"><div style="display:flex; align-items:center; gap:15px;"><div style="font-size:40px;">' + str(s["icone"]) + '</div><div style="flex:1;"><strong style="font-size:16px; color:#333;">' + str(s["nome"]) + '</strong><br><span style="color:#888; font-size:12px;">' + str(s["descricao"]) + '</span><br><span style="color:#888; font-size:12px;">⏱ ~' + str(s["duracao_min"]) + ' min</span></div><div style="text-align:right;"><strong style="color:#C48B9F; font-size:20px;">R$ ' + f'{s["preco"]:.0f}' + '</strong></div></div></div>', unsafe_allow_html=True)
                if st.button("Agendar " + str(s["nome"]), key="srv_" + str(s["id"]), use_container_width=True):
                    ir_para("escolher_manicure", servico_id=s["id"])
                    st.rerun()

def tela_escolher_manicure():
    st.markdown('<div class="header-unha"><h1>Escolher Profissional</h1><p>Selecione quem vai cuidar de voce</p></div>', unsafe_allow_html=True)
    if st.button("← Voltar"):
        ir_para("cliente_home")
        st.rerun()
    favs = query("SELECT manicure_id FROM favoritas WHERE cliente_id=%s", (st.session_state.user_id,))
    fav_ids = [f["manicure_id"] for f in favs]
    manicures = query("SELECT u.*, (SELECT COUNT(*) FROM agendamentos a WHERE a.manicure_id=u.id AND a.status='concluido') as total_atend FROM usuarios u WHERE u.tipo='manicure' AND u.ativo=1 ORDER BY u.avaliacao_media DESC")
    if not manicures:
        st.warning("Nenhuma profissional disponivel no momento.")
        return
    if fav_ids:
        st.markdown("### ⭐ Suas Favoritas")
        for m in manicures:
            if m["id"] in fav_ids:
                letra = str(m["nome"])[:1].upper()
                pri = str(m["nome"]).split().pop(0)
                st.markdown('<div class="card-gold"><div style="display:flex; align-items:center; gap:15px;"><div style="background:linear-gradient(135deg,#B8860B,#D4A853); color:white; width:56px; height:56px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:24px; font-weight:700;">' + letra + '</div><div style="flex:1;"><strong style="font-size:16px;">' + str(m["nome"]) + ' ⭐</strong><br><span class="estrelas">' + estrelas(m["avaliacao_media"] or 5) + '</span> <span style="color:#888; font-size:12px;">(' + str(m["total_avaliacoes"] or 0) + ' avaliacoes)</span><br><span style="color:#888; font-size:12px;">' + str(m["bio"] or "") + '</span></div></div></div>', unsafe_allow_html=True)
                if st.button("Agendar com " + pri + " ⭐", key="fav_" + str(m["id"]), use_container_width=True, type="primary"):
                    ir_para("agendar", manicure_id=m["id"])
                    st.rerun()
    st.markdown("### 💅 Todas as Profissionais")
    enviar_aberto = st.checkbox("🔔 Enviar para todas as profissionais disponiveis (a primeira que aceitar em 1h atende voce!)")
    if enviar_aberto:
        st.session_state.aberto_para_todas = True
    else:
        st.session_state.aberto_para_todas = False
    for m in manicures:
        letra = str(m["nome"])[:1].upper()
        pri = str(m["nome"]).split().pop(0)
        eh_fav = "⭐" if m["id"] in fav_ids else ""
        st.markdown('<div class="card"><div style="display:flex; align-items:center; gap:15px;"><div style="background:linear-gradient(135deg,#C48B9F,#D4A0B0); color:white; width:56px; height:56px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:24px; font-weight:700;">' + letra + '</div><div style="flex:1;"><strong style="font-size:16px;">' + str(m["nome"]) + ' ' + eh_fav + '</strong><br><span class="estrelas">' + estrelas(m["avaliacao_media"] or 5) + '</span> <span style="color:#888; font-size:12px;">(' + str(m["total_avaliacoes"] or 0) + ' avaliacoes)</span><br><span style="color:#888; font-size:12px;">📍 ' + str(m["endereco"] or "Atende no local") + ' | ' + str(m["total_atend"]) + ' atendimentos</span></div></div><p style="color:#666; font-style:italic; font-size:12px; margin-top:10px;">' + str(m["bio"] or "") + '</p></div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Agendar com " + pri, key="man_" + str(m["id"]), use_container_width=True, type="primary"):
                ir_para("agendar", manicure_id=m["id"])
                st.rerun()
        with col2:
            if m["id"] not in fav_ids:
                if st.button("⭐ Favoritar", key="favbtn_" + str(m["id"]), use_container_width=True):
                    execute("INSERT INTO favoritas (cliente_id, manicure_id) VALUES (%s,%s) ON CONFLICT DO NOTHING", (st.session_state.user_id, m["id"]))
                    st.rerun()

def tela_agendar():
    servico_list = query("SELECT * FROM servicos WHERE id=%s", (st.session_state.servico_id,))
    manicure_list = query("SELECT * FROM usuarios WHERE id=%s", (st.session_state.manicure_id,))
    if not servico_list or not manicure_list:
        st.error("Erro ao carregar dados")
        ir_para("cliente_home")
        st.rerun()
        return
    servico = servico_list[0]
    manicure = manicure_list[0]
    st.markdown('<div class="header-unha"><h1>📅 Agendar</h1><p>' + str(servico["icone"]) + ' ' + str(servico["nome"]) + ' com ' + str(manicure["nome"]) + '</p></div>', unsafe_allow_html=True)
    if st.button("← Voltar"):
        ir_para("escolher_manicure")
        st.rerun()
    valor_total = servico["preco"]
    valor_manicure = valor_total * (1 - COMISSAO)
    duracao = servico["duracao_min"]
    st.markdown('<div class="card-gold"><div style="text-align:center;"><span style="font-size:50px;">' + str(servico["icone"]) + '</span><h3 style="margin:10px 0 5px 0;">' + str(servico["nome"]) + '</h3><p style="color:#888; margin:0;">⏱ ~' + str(duracao) + ' min</p><h2 style="color:#B8860B; margin:15px 0 0 0;">R$ ' + f'{valor_total:.2f}' + '</h2></div></div>', unsafe_allow_html=True)
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
    st.markdown("### 📅 Escolha a Data")
    data_opcoes = {}
    for dia in dias_disp[:20]:
        label = dia.strftime("%d/%m/%Y (%a)")
        data_opcoes[label] = dia
    data_str = st.selectbox("Data disponivel:", list(data_opcoes.keys()))
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
            st.markdown("### ⏰ Horario")
            if horarios_livres:
                horario_sel = st.selectbox("Horarios disponiveis:", horarios_livres)
            else:
                st.warning("Sem horarios livres nesta data. Escolha outra!")
    st.markdown("### 📍 Local de Atendimento")
    endereco = st.text_input("Endereco completo *")
    complemento = st.text_input("Complemento (apto, bloco...)")
    st.markdown("### 💳 Forma de Pagamento")
    forma_pg = st.radio("Escolha:", ["PIX", "Cartao de Credito", "Cartao de Debito", "Dinheiro"], horizontal=True)
    formas_map = {"PIX": "pix", "Cartao de Credito": "cartao_credito", "Cartao de Debito": "cartao_debito", "Dinheiro": "dinheiro"}
    obs = st.text_area("📝 Observacoes (opcional)")
    st.markdown('<div class="card-gold"><h4>📋 Resumo do Agendamento</h4><p><strong>Servico:</strong> ' + str(servico["nome"]) + '<br><strong>Profissional:</strong> ' + str(manicure["nome"]) + '<br><strong>Data:</strong> ' + str(data_str) + '<br><strong>Horario:</strong> ' + str(horario_sel or "-") + '<br><strong>Pagamento:</strong> ' + str(forma_pg) + '</p><hr><h2 style="color:#B8860B; text-align:center;">TOTAL: R$ ' + f'{valor_total:.2f}' + '</h2></div>', unsafe_allow_html=True)
    if st.button("✅ CONFIRMAR AGENDAMENTO", use_container_width=True, type="primary"):
        if not horario_sel:
            st.error("Selecione um horario!")
            return
        if not endereco:
            st.error("Informe o endereco!")
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
            execute("INSERT INTO notificacoes (usuario_id,titulo,mensagem,tipo) VALUES (%s,%s,%s,%s)", (st.session_state.manicure_id, "🔔 Novo Agendamento!", "Novo agendamento " + data_br + " as " + horario_sel + " - Aceite em 1h!", "agendamento"))
            st.session_state.ultimo_agendamento = ag_id
            ir_para("confirmacao")
            st.rerun()

def tela_confirmacao():
    ag_id = st.session_state.get("ultimo_agendamento")
    resultado = query("SELECT a.*, s.nome as sn, s.icone, u.nome as mn FROM agendamentos a JOIN servicos s ON a.servico_id=s.id JOIN usuarios u ON a.manicure_id=u.id WHERE a.id=%s", (ag_id,))
    if not resultado:
        ir_para("cliente_home")
        st.rerun()
        return
    ag = resultado[0]
    st.markdown('<div style="text-align:center; padding:40px 0;"><div style="font-size:80px;">✅</div><h2 style="color:#4CAF50; font-weight:700;">Agendamento Confirmado!</h2><p style="color:#888; font-size:14px;">A profissional tem 1 hora para aceitar</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="card-gold"><div style="text-align:center;"><span style="font-size:40px;">' + str(ag["icone"]) + '</span><h3>' + str(ag["sn"]) + '</h3></div><p><strong>Profissional:</strong> ' + str(ag["mn"]) + '<br><strong>Data:</strong> ' + str(ag["data"]) + '<br><strong>Horario:</strong> ' + str(ag["horario"]) + '<br><strong>Local:</strong> ' + str(ag["endereco_atendimento"]) + '<br><strong>Pagamento:</strong> ' + forma_pg_nome(ag["forma_pagamento"]) + '</p><hr><h2 style="color:#B8860B; text-align:center;">R$ ' + f'{ag["valor_total"]:.2f}' + '</h2></div>', unsafe_allow_html=True)
    if st.button("🏠 Voltar ao Inicio", use_container_width=True, type="primary"):
        ir_para("cliente_home")
        st.rerun()

def tela_meus_agendamentos():
    st.markdown('<div class="header-unha"><h1>📋 Meus Agendamentos</h1></div>', unsafe_allow_html=True)
    if st.button("← Voltar"):
        ir_para("cliente_home")
        st.rerun()
    agendamentos = query("SELECT a.*, s.nome as sn, s.icone, u.nome as mn FROM agendamentos a JOIN servicos s ON a.servico_id=s.id JOIN usuarios u ON a.manicure_id=u.id WHERE a.cliente_id=%s ORDER BY a.data_criacao DESC LIMIT 20", (st.session_state.user_id,))
    if not agendamentos:
        st.markdown('<div style="text-align:center; padding:40px;"><div style="font-size:60px;">📭</div><p style="color:#888;">Nenhum agendamento ainda.<br>Que tal agendar?</p></div>', unsafe_allow_html=True)
    else:
        for ag in agendamentos:
            st.markdown('<div class="card"><div style="display:flex; justify-content:space-between; align-items:center;"><div><strong>' + str(ag["icone"]) + ' ' + str(ag["sn"]) + '</strong><br><span style="color:#888;">com ' + str(ag["mn"]) + '</span><br><span style="color:#888; font-size:12px;">📅 ' + str(ag["data"]) + ' ⏰ ' + str(ag["horario"]) + '</span></div><div style="text-align:right;">' + badge_html(ag["status"]) + '<br><strong style="color:#B8860B; font-size:18px;">R$ ' + f'{ag["valor_total"]:.2f}' + '</strong></div></div></div>', unsafe_allow_html=True)
            if ag["status"] == "concluido" and ag["avaliacao_nota"] is None:
                if st.button("⭐ Avaliar", key="aval_" + str(ag["id"]), use_container_width=True):
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
    st.markdown('<div class="header-unha"><h1>⭐ Avaliar</h1><p>' + str(ag["sn"]) + ' com ' + str(ag["mn"]) + '</p></div>', unsafe_allow_html=True)
    if st.button("← Voltar"):
        ir_para("meus_agendamentos")
        st.rerun()
    st.markdown("### Como foi sua experiencia?")
    nota = st.slider("Nota:", 1, 5, 5)
    textos = {1: "😞 Pessimo", 2: "😕 Ruim", 3: "😐 Regular", 4: "😊 Bom", 5: "🤩 Excelente!"}
    st.markdown('<h2 style="text-align:center;">' + textos[nota] + '</h2>', unsafe_allow_html=True)
    comentario = st.text_area("💬 Conte como foi sua experiencia...")
    if st.button("✅ ENVIAR AVALIACAO", use_container_width=True, type="primary"):
        execute("UPDATE agendamentos SET avaliacao_nota=%s, avaliacao_comentario=%s WHERE id=%s", (nota, comentario, ag_id))
        media_result = query("SELECT AVG(avaliacao_nota) as media, COUNT(*) as total FROM agendamentos WHERE manicure_id=%s AND avaliacao_nota IS NOT NULL", (ag["manicure_id"],))
        if media_result:
            mr = media_result[0]
            execute("UPDATE usuarios SET avaliacao_media=%s, total_avaliacoes=%s WHERE id=%s", (mr["media"] or 5, mr["total"] or 0, ag["manicure_id"]))
        execute("INSERT INTO favoritas (cliente_id, manicure_id) VALUES (%s,%s) ON CONFLICT DO NOTHING", (st.session_state.user_id, ag["manicure_id"]))
        execute("INSERT INTO notificacoes (usuario_id,titulo,mensagem,tipo) VALUES (%s,%s,%s,%s)", (ag["manicure_id"], "⭐ Avaliacao: " + str(nota) + " estrelas!", comentario or "Sem comentario", "avaliacao"))
        st.success("Avaliacao enviada! Obrigada!")
        st.balloons()
        ir_para("cliente_home")
        st.rerun()

def tela_perfil():
    resultado = query("SELECT * FROM usuarios WHERE id=%s", (st.session_state.user_id,))
    if not resultado:
        ir_para("cliente_home")
        st.rerun()
        return
    user = resultado[0]
    st.markdown('<div class="header-unha"><h1>👤 Meu Perfil</h1></div>', unsafe_allow_html=True)
    if st.button("← Voltar"):
        ir_para("cliente_home")
        st.rerun()
    letra = str(user["nome"])[:1].upper()
    st.markdown('<div class="card" style="text-align:center;"><div style="background:linear-gradient(135deg,#C48B9F,#D4A0B0); color:white; width:90px; height:90px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:40px; font-weight:700; margin: 0 auto 15px auto;">' + letra + '</div><h2 style="margin:0;">' + str(user["nome"]) + '</h2><p style="color:#888;">📱 ' + str(user["telefone"]) + '<br>📧 ' + str(user["email"] or "Nao informado") + '<br>📍 ' + str(user["endereco"] or "Nao informado") + '</p></div>', unsafe_allow_html=True)

def tela_manicure_home():
    hoje = date.today().strftime("%d/%m/%Y")
    nome_partes = st.session_state.user_nome.split()
    primeiro_nome = nome_partes.pop(0) if nome_partes else st.session_state.user_nome
    st.markdown('<div class="header-unha"><h1>Ola, ' + primeiro_nome + '! 💅</h1><p>Painel da Profissional</p></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔔 Notificacoes", use_container_width=True):
            pass
    with col2:
        if st.button("🚪 Sair", use_container_width=True):
            logout()
            st.rerun()
    mes_atual = date.today().strftime("%m/%Y")
    ganhos_result = query("SELECT COALESCE(SUM(valor_manicure),0) as ganhos, COUNT(*) as total FROM agendamentos WHERE manicure_id=%s AND status='concluido' AND data LIKE %s", (st.session_state.user_id, "%" + mes_atual))
    gr = ganhos_result[0] if ganhos_result else {"ganhos": 0, "total": 0}
    ganhos_mes = gr["ganhos"]
    total_atend = gr["total"]
    receber_result = query("SELECT COALESCE(SUM(valor_manicure),0) as valor FROM agendamentos WHERE manicure_id=%s AND status='concluido' AND pago=0", (st.session_state.user_id,))
    rr = receber_result[0] if receber_result else {"valor": 0}
    a_receber = rr["valor"]
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="kpi-box"><div class="kpi-label">💰 Ganhos do Mes</div><div class="kpi-valor" style="color:#4CAF50;">R$ ' + f'{ganhos_mes:.2f}' + '</div><div class="kpi-label">' + str(total_atend) + ' atendimentos</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="kpi-box"><div class="kpi-label">📥 A Receber</div><div class="kpi-valor" style="color:#B8860B;">R$ ' + f'{a_receber:.2f}' + '</div><div class="kpi-label">Liberacao em ' + str(DIAS_RECEBER) + ' dias</div></div>', unsafe_allow_html=True)
    pendentes = query("SELECT a.*, s.nome as sn, s.icone, u.nome as cn FROM agendamentos a JOIN servicos s ON a.servico_id=s.id JOIN usuarios u ON a.cliente_id=u.id WHERE a.manicure_id=%s AND a.status IN ('pendente','aguardando_aceite') ORDER BY a.data_criacao DESC", (st.session_state.user_id,))
    if pendentes:
        st.markdown("### 🔔 Aguardando Sua Confirmacao")
        for ag in pendentes:
            st.markdown('<div class="card-gold"><strong>🔔 ' + str(ag["icone"]) + ' ' + str(ag["sn"]) + '</strong><br>Cliente: ' + str(ag["cn"]) + '<br>📅 ' + str(ag["data"]) + ' ⏰ ' + str(ag["horario"]) + '<br>📍 ' + str(ag["endereco_atendimento"] or "-") + '<br><strong style="color:#4CAF50;">Voce recebe: R$ ' + f'{ag["valor_manicure"]:.2f}' + '</strong></div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ Aceitar", key="aceitar_" + str(ag["id"]), use_container_width=True, type="primary"):
                    execute("UPDATE agendamentos SET status='confirmado' WHERE id=%s", (ag["id"],))
                    execute("INSERT INTO notificacoes (usuario_id,titulo,mensagem,tipo) VALUES (%s,%s,%s,%s)", (ag["cliente_id"], "✅ Agendamento Aceito!", str(ag["sn"]) + " confirmado para " + str(ag["data"]), "agendamento"))
                    st.rerun()
            with c2:
                if st.button("❌ Recusar", key="recusar_" + str(ag["id"]), use_container_width=True):
                    execute("UPDATE agendamentos SET status='cancelado' WHERE id=%s", (ag["id"],))
                    execute("INSERT INTO notificacoes (usuario_id,titulo,mensagem,tipo) VALUES (%s,%s,%s,%s)", (ag["cliente_id"], "❌ Agendamento Recusado", "Procure outra profissional", "agendamento"))
                    st.rerun()
    st.markdown("### 📅 Hoje (" + hoje + ")")
    hoje_ag = query("SELECT a.*, s.nome as sn, s.icone, u.nome as cn FROM agendamentos a JOIN servicos s ON a.servico_id=s.id JOIN usuarios u ON a.cliente_id=u.id WHERE a.manicure_id=%s AND a.data=%s AND a.status IN ('confirmado','em_andamento') ORDER BY a.horario", (st.session_state.user_id, hoje))
    if not hoje_ag:
        st.markdown('<div style="text-align:center; padding:20px;"><p style="color:#888;">Nenhum atendimento hoje. Descanse! 😊</p></div>', unsafe_allow_html=True)
    else:
        for ag in hoje_ag:
            st.markdown('<div class="card"><strong>⏰ ' + str(ag["horario"]) + '</strong> | ' + badge_html(ag["status"]) + '<br>' + str(ag["icone"]) + ' ' + str(ag["sn"]) + '<br>👤 ' + str(ag["cn"]) + '<br>📍 ' + str(ag["endereco_atendimento"] or "-") + '<br><strong style="color:#4CAF50;">R$ ' + f'{ag["valor_manicure"]:.2f}' + '</strong></div>', unsafe_allow_html=True)
            if ag["status"] == "confirmado":
                if st.button("✅ Concluir", key="conc_" + str(ag["id"]), use_container_width=True, type="primary"):
                    execute("UPDATE agendamentos SET status='concluido' WHERE id=%s", (ag["id"],))
                    execute("INSERT INTO notificacoes (usuario_id,titulo,mensagem,tipo) VALUES (%s,%s,%s,%s)", (ag["cliente_id"], "🎉 Atendimento Concluido!", "Avalie sua experiencia!", "avaliacao"))
                    st.rerun()
    st.markdown("### 📅 Proximos")
    proximos = query("SELECT a.*, s.nome as sn, s.icone, u.nome as cn FROM agendamentos a JOIN servicos s ON a.servico_id=s.id JOIN usuarios u ON a.cliente_id=u.id WHERE a.manicure_id=%s AND a.status='confirmado' AND a.data > %s ORDER BY a.data, a.horario LIMIT 10", (st.session_state.user_id, hoje))
    if not proximos:
        st.info("Nenhum agendamento futuro")
    else:
        for ag in proximos:
            st.markdown('<div class="card">📅 ' + str(ag["data"]) + ' ⏰ ' + str(ag["horario"]) + '<br>' + str(ag["icone"]) + ' ' + str(ag["sn"]) + ' | 👤 ' + str(ag["cn"]) + '<br><strong style="color:#4CAF50;">R$ ' + f'{ag["valor_manicure"]:.2f}' + '</strong></div>', unsafe_allow_html=True)

def tela_admin():
    st.markdown('<div style="background: linear-gradient(135deg, #B8860B 0%, #D4A853 50%, #E8D5A0 100%); padding: 30px 20px; border-radius: 0 0 30px 30px; margin: -6rem -1rem 1.5rem -1rem; text-align:center; box-shadow: 0 8px 32px rgba(184,134,11,0.3);"><h1 style="color:white !important; font-size:28px !important; margin:0 !important;">👑 Painel Admin</h1><p style="color:#FFF8E7; font-size:14px;">Unha Click - Dashboard</p></div>', unsafe_allow_html=True)
    if st.button("🚪 Sair"):
        logout()
        st.rerun()
    stats = query("SELECT (SELECT COUNT(*) FROM usuarios WHERE tipo='cliente') as clientes, (SELECT COUNT(*) FROM usuarios WHERE tipo='manicure') as manicures, (SELECT COUNT(*) FROM agendamentos) as agendamentos, (SELECT COALESCE(SUM(valor_total),0) FROM agendamentos WHERE status='concluido') as faturamento, (SELECT COALESCE(SUM(valor_comissao),0) FROM agendamentos WHERE status='concluido') as comissao")
    s = stats[0] if stats else {"clientes": 0, "manicures": 0, "agendamentos": 0, "faturamento": 0, "comissao": 0}
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="kpi-box"><div class="kpi-label">👥 Clientes</div><div class="kpi-valor" style="color:#C48B9F;">' + str(s["clientes"]) + '</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="kpi-box"><div class="kpi-label">💅 Profissionais</div><div class="kpi-valor" style="color:#C48B9F;">' + str(s["manicures"]) + '</div></div>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        st.markdown('<div class="kpi-box"><div class="kpi-label">📋 Agendamentos</div><div class="kpi-valor" style="color:#2196F3;">' + str(s["agendamentos"]) + '</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="kpi-box"><div class="kpi-label">💰 Faturamento</div><div class="kpi-valor" style="color:#4CAF50;">R$ ' + f'{s["faturamento"]:.0f}' + '</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="card-gold" style="text-align:center; margin-top:15px;"><strong style="color:#B8860B; font-size:16px;">👑 SUA COMISSAO (20%)</strong><h2 style="color:#B8860B; margin:10px 0;">R$ ' + f'{s["comissao"]:.2f}' + '</h2></div>', unsafe_allow_html=True)
    st.markdown("### 📋 Ultimos Agendamentos")
    ultimos = query("SELECT a.*, s.nome as sn, u1.nome as cn, u2.nome as mn FROM agendamentos a JOIN servicos s ON a.servico_id=s.id JOIN usuarios u1 ON a.cliente_id=u1.id JOIN usuarios u2 ON a.manicure_id=u2.id ORDER BY a.data_criacao DESC LIMIT 10")
    for a in ultimos:
        st.markdown('<div class="card"><strong>' + str(a["sn"]) + '</strong> | 👤 ' + str(a["cn"]) + ' → 💅 ' + str(a["mn"]) + '<br>📅 ' + str(a["data"]) + ' ⏰ ' + str(a["horario"]) + ' | ' + badge_html(a["status"]) + '<br><strong style="color:#B8860B;">R$ ' + f'{a["valor_total"]:.2f}' + '</strong></div>', unsafe_allow_html=True)

telas = {"login": tela_login, "cadastro": tela_cadastro, "cliente_home": tela_cliente_home, "escolher_manicure": tela_escolher_manicure, "agendar": tela_agendar, "confirmacao": tela_confirmacao, "meus_agendamentos": tela_meus_agendamentos, "avaliar": tela_avaliar, "perfil": tela_perfil, "manicure_home": tela_manicure_home, "admin": tela_admin}
tela_atual = st.session_state.get("tela", "login")
if tela_atual in telas:
    telas[tela_atual]()
else:
    tela_login()

