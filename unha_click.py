import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
import hashlib
from datetime import datetime, date, timedelta

st.set_page_config(page_title="Unha Click", page_icon="💅", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    * { font-family: 'Poppins', sans-serif; }
    .stApp { background: linear-gradient(180deg, #FFF9FB 0%, #FFFFFF 100%); }
    .header-unha { background: linear-gradient(135deg, #8B5E6B 0%, #C48B9F 100%); padding: 25px 20px; border-radius: 0 0 25px 25px; margin: -6rem -1rem 1.5rem -1rem; text-align: center; box-shadow: 0 4px 15px rgba(196, 139, 159, 0.3); }
    .header-unha h1 { color: white !important; font-size: 28px !important; margin: 0 !important; font-weight: 700 !important; }
    .header-unha p { color: #FFF8E7; font-size: 14px; margin: 5px 0 0 0; }
    .card { background: white; border-radius: 16px; padding: 18px; margin-bottom: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); border: 1px solid #F5E6EC; }
    .card-gold { background: linear-gradient(135deg, #FFF8E7 0%, #FFFFFF 100%); border: 2px solid #D4A853; border-radius: 16px; padding: 18px; margin-bottom: 12px; }
    .card-rose { background: linear-gradient(135deg, #F5E6EC 0%, #FFFFFF 100%); border: 1px solid #C48B9F; border-radius: 16px; padding: 18px; margin-bottom: 12px; }
    .kpi-box { background: white; border-radius: 14px; padding: 15px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.05); border: 1px solid #F5E6EC; }
    .kpi-valor { font-size: 26px; font-weight: 700; margin: 5px 0; }
    .kpi-label { font-size: 12px; color: #888; }
    .badge { display: inline-block; padding: 3px 10px; border-radius: 8px; font-size: 11px; font-weight: 600; color: white; }
    .badge-pendente { background: #FFA726; }
    .badge-confirmado { background: #2196F3; }
    .badge-concluido { background: #4CAF50; }
    .badge-cancelado { background: #E53935; }
    .estrelas { color: #D4A853; font-size: 18px; }
    .stButton > button { background: linear-gradient(135deg, #C48B9F 0%, #8B5E6B 100%) !important; color: white !important; border: none !important; border-radius: 14px !important; padding: 10px 30px !important; font-weight: 600 !important; font-size: 15px !important; width: 100% !important; }
    .servico-preco { background: #FFF8E7; color: #B8860B; padding: 5px 12px; border-radius: 8px; font-weight: 700; font-size: 14px; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

COMISSAO = 0.20
DIAS_RECEBER = 2

def get_new_connection():
    return psycopg2.connect(host=st.secrets["database"]["host"], port=st.secrets["database"]["port"], dbname=st.secrets["database"]["dbname"], user=st.secrets["database"]["user"], password=st.secrets["database"]["password"], sslmode="require", connect_timeout=10)

def query(sql, params=None, fetch=True):
    try:
        conn = get_new_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(sql, params)
        resultado = cur.fetchall() if fetch else None
        conn.commit()
        cur.close()
        conn.close()
        return resultado
    except Exception as e:
        st.error(f"Erro no banco: {e}")
        return [] if fetch else None

def execute(sql, params=None):
    query(sql, params, fetch=False)

def execute_returning(sql, params=None):
    try:
        conn = get_new_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(sql, params)
        resultado = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return resultado
    except Exception as e:
        st.error(f"Erro no banco: {e}")
        return None

if "banco_criado" not in st.session_state:
    try:
        conn = get_new_connection()
        cur = conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS usuarios (id SERIAL PRIMARY KEY, nome TEXT NOT NULL, telefone TEXT UNIQUE NOT NULL, email TEXT, senha TEXT NOT NULL, tipo TEXT DEFAULT 'cliente', endereco TEXT, bairro TEXT, cidade TEXT, estado TEXT DEFAULT 'SP', foto TEXT, avaliacao_media REAL DEFAULT 5.0, total_avaliacoes INTEGER DEFAULT 0, especialidades TEXT, bio TEXT, chave_pix TEXT, banco TEXT, ativo INTEGER DEFAULT 1, data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        cur.execute("""CREATE TABLE IF NOT EXISTS servicos (id SERIAL PRIMARY KEY, nome TEXT NOT NULL, descricao TEXT, preco REAL NOT NULL, duracao_min INTEGER DEFAULT 60, categoria TEXT DEFAULT 'maos', icone TEXT DEFAULT '💅', ativo INTEGER DEFAULT 1)""")
        cur.execute("""CREATE TABLE IF NOT EXISTS agendamentos (id SERIAL PRIMARY KEY, cliente_id INTEGER REFERENCES usuarios(id), manicure_id INTEGER REFERENCES usuarios(id), servico_id INTEGER REFERENCES servicos(id), data TEXT, horario TEXT, endereco_atendimento TEXT, bairro TEXT, complemento TEXT, valor_total REAL, valor_manicure REAL, valor_comissao REAL, cupom_codigo TEXT, status TEXT DEFAULT 'pendente', forma_pagamento TEXT DEFAULT 'pix', observacoes TEXT, data_liberacao_manicure TEXT, pago INTEGER DEFAULT 0, avaliacao_nota INTEGER, avaliacao_comentario TEXT, data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        cur.execute("""CREATE TABLE IF NOT EXISTS disponibilidade (id SERIAL PRIMARY KEY, manicure_id INTEGER, dia_semana INTEGER, hora_inicio TEXT DEFAULT '08:00', hora_fim TEXT DEFAULT '18:00', ativo INTEGER DEFAULT 1)""")
        cur.execute("""CREATE TABLE IF NOT EXISTS notificacoes (id SERIAL PRIMARY KEY, usuario_id INTEGER, titulo TEXT, mensagem TEXT, tipo TEXT DEFAULT 'info', lida INTEGER DEFAULT 0, data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        cur.execute("""CREATE TABLE IF NOT EXISTS transacoes (id SERIAL PRIMARY KEY, agendamento_id INTEGER, tipo TEXT, valor REAL, destinatario_id INTEGER, forma_pagamento TEXT, status TEXT DEFAULT 'pendente', data_prevista_liberacao TEXT, data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        conn.commit()
        cur.execute("SELECT COUNT(*) FROM servicos")
        if cur.fetchone() == 0:
            for srv in [("Esmaltacao Simples","Esmaltacao classica",35.0,40,"maos","💅"),("Esmaltacao em Gel","Gel de longa duracao",60.0,50,"maos","✨"),("Unha Decorada","Nail art personalizada",80.0,70,"maos","🎨"),("Francesinha","Classica francesinha",45.0,50,"maos","🤍"),("Alongamento Fibra","Fibra de vidro",120.0,90,"maos","💎"),("Pedicure Completa","Hidratacao + esmaltacao",50.0,60,"pes","🦶"),("Spa dos Pes","Esfoliacao + hidratacao",70.0,75,"pes","🧖"),("Combo Maos + Pes","Esmaltacao completa",75.0,90,"combo","👑"),("Combo VIP","Gel + Spa + Hidratacao",130.0,120,"combo","🌟"),("Combo Noiva","Pacote especial noivas",200.0,150,"combo","💒")]:
                cur.execute("INSERT INTO servicos (nome,descricao,preco,duracao_min,categoria,icone) VALUES (%s,%s,%s,%s,%s,%s)", srv)
        cur.execute("SELECT COUNT(*) FROM usuarios WHERE tipo='admin'")
        if cur.fetchone() == 0:
                    cur.execute("SELECT COUNT(*) FROM usuarios WHERE tipo='admin'")
        if cur.fetchone() == 0:
            senha_admin =[PASSWORD]6("admin123".encode()).hexdigest()
            cur.execute("INSERT INTO usuarios (nome,telefone,email,senha,tipo) VALUES (%s,%s,%s,%s,%s)", ("Fernando Jr","11999999999","fernando@unhaclick.com",senha_admin,"admin"))
            senha_mani =[PASSWORD]6([PASSWORD]4".encode()).hexdigest()
            cur.execute("INSERT INTO usuarios (nome,telefone,email,senha,tipo,especialidades,bio,chave_pix) VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id", ("Profissional Demo","11988887777","demo@unhaclick.com",senha_mani,"manicure","Gel,Fibra,Decoracao,Francesinha","Especialista em nail art com 5 anos de experiencia!","11988887777"))
            mid = cur.fetchone()
            for dia in range(0, 6):
                cur.execute("INSERT INTO disponibilidade (manicure_id,dia_semana,hora_inicio,hora_fim) VALUES (%s,%s,%s,%s)", (mid, dia, "08:00", "18:00"))
            senha_cli =[PASSWORD]6([PASSWORD]4".encode()).hexdigest()
            cur.execute("INSERT INTO usuarios (nome,telefone,email,senha,tipo) VALUES (%s,%s,%s,%s,%s)", ("Cliente Demo","11977776666","cliente@demo.com",senha_cli,"cliente"))


def badge_html(status):
    nomes = {"pendente": "Pendente", "confirmado": "Confirmado", "concluido": "Concluido", "cancelado": "Cancelado"}
    return '<span class="badge badge-' + status + '">' + nomes.get(status, status) + '</span>'

def forma_pg_nome(fp):
    nomes = {"pix": "PIX", "cartao_credito": "Cartao Credito", "cartao_debito": "Cartao Debito", "dinheiro": "Dinheiro"}
    return nomes.get(fp, fp)

if "user_id" not in st.session_state:
    st.session_state.user_id = None
    st.session_state.user_nome = ""
    st.session_state.user_tipo = ""
    st.session_state.tela = "login"
    st.session_state.servico_id = None
    st.session_state.manicure_id = None

def logout():
    st.session_state.user_id = None
    st.session_state.user_nome = ""
    st.session_state.user_tipo = ""
    st.session_state.tela = "login"

def ir_para(tela, **kwargs):
    st.session_state.tela = tela
    for k, v in kwargs.items():
        st.session_state[k] = v

def tela_login():
    st.markdown('<div style="text-align:center; padding: 40px 0 20px 0;"><div style="font-size: 70px;">💅</div><h1 style="color: #8B5E6B; font-size: 36px; margin: 10px 0 5px 0;">Unha Click</h1><p style="color: #888; font-style: italic;">Beleza na palma da mao</p></div>', unsafe_allow_html=True)
    tel = st.text_input("Telefone", placeholder="11999999999")
    senha = st.text_input("Senha", type="password")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("ENTRAR", use_container_width=True):
            if tel and senha:
                s =[PASSWORD]6(senha.encode()).hexdigest()
                resultado = query("SELECT * FROM usuarios WHERE telefone=%s AND senha=%s AND ativo=1", (tel, s))
                if resultado:
                    user = resultado
                    st.session_state.user_id = user["id"]
                    st.session_state.user_nome = user["nome"]
                    st.session_state.user_tipo = user["tipo"]
                    if user["tipo"] == "admin":
                        st.session_state.tela = "admin"
                    elif user["tipo"] == "manicure":
                        st.session_state.tela = "manicure_home"
                    else:
                        st.session_state.tela = "cliente_home"
                    st.rerun()
                else:
                    st.error("Telefone ou senha incorretos!")
            else:
                st.warning("Preencha todos os campos!")
    with col2:
        if st.button("CADASTRAR", use_container_width=True):
            st.session_state.tela = "cadastro"
            st.rerun()
    st.markdown("---")
    st.markdown('<div style="text-align:center; font-size:12px; color:#888;"><p><strong>Logins Demo:</strong></p><p>Admin: 11999999999 / admin123</p><p>Manicure: 11988887777 / 1234</p><p>Cliente: 11977776666 / 1234</p></div>', unsafe_allow_html=True)

def tela_cadastro():
    st.markdown('<div class="header-unha"><h1>Cadastro</h1><p>Crie sua conta!</p></div>', unsafe_allow_html=True)
    if st.button("Voltar"):
        ir_para("login")
        st.rerun()
    with st.form("form_cadastro"):
        nome = st.text_input("Nome completo *")
        tel = st.text_input("Telefone *", placeholder="11999999999")
        email = st.text_input("E-mail")
        senha = st.text_input("Criar senha *", type="password")
        endereco = st.text_input("Endereco")
        bairro = st.text_input("Bairro")
        cidade = st.text_input("Cidade")
        if st.form_submit_button("CADASTRAR"):
            if nome and tel and senha:
                s =[PASSWORD]6(senha.encode()).hexdigest()
                existe = query("SELECT id FROM usuarios WHERE telefone=%s", (tel,))
                if existe:
                    st.error("Telefone ja cadastrado!")
                else:
                    execute("INSERT INTO usuarios (nome,telefone,email,senha,tipo,endereco,bairro,cidade) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", (nome, tel, email, s, "cliente", endereco, bairro, cidade))
                    st.success("Cadastro realizado! Faca login!")
                    ir_para("login")
                    st.rerun()
            else:
                st.warning("Preencha os campos obrigatorios (*)")

def tela_cliente_home():
    primeiro_nome = st.session_state.user_nome.split()
    st.markdown('<div class="header-unha"><h1>Ola, ' + primeiro_nome + '!</h1><p>O que vamos fazer hoje?</p></div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("Home", use_container_width=True):
            ir_para("cliente_home")
            st.rerun()
    with col2:
        if st.button("Agenda", use_container_width=True):
            ir_para("meus_agendamentos")
            st.rerun()
    with col3:
        if st.button("Perfil", use_container_width=True):
            ir_para("perfil")
            st.rerun()
    with col4:
        if st.button("Sair", use_container_width=True):
            logout()
            st.rerun()
    proximos = query("SELECT a.*, s.nome as servico_nome, s.icone, u.nome as manicure_nome FROM agendamentos a JOIN servicos s ON a.servico_id=s.id JOIN usuarios u ON a.manicure_id=u.id WHERE a.cliente_id=%s AND a.status IN ('pendente','confirmado') ORDER BY a.data, a.horario LIMIT 3", (st.session_state.user_id,))
    if proximos:
        st.markdown("### Proximos Agendamentos")
        for ag in proximos:
            st.markdown('<div class="card-rose"><strong>' + str(ag["icone"]) + ' ' + str(ag["servico_nome"]) + '</strong><br><span style="color:#888;">com ' + str(ag["manicure_nome"]) + ' | ' + str(ag["data"]) + ' as ' + str(ag["horario"]) + '</span><br>' + badge_html(ag["status"]) + ' <strong style="color:#B8860B;">R$ ' + f'{ag["valor_total"]:.2f}' + '</strong></div>', unsafe_allow_html=True)
    st.markdown("### Nossos Servicos")
    servicos = query("SELECT * FROM servicos WHERE ativo=1 ORDER BY categoria, preco")
    categorias = {"maos": "Maos", "pes": "Pes", "combo": "Combos Especiais"}
    for cat_key, cat_nome in categorias.items():
        cat_servicos = [s for s in servicos if s["categoria"] == cat_key]
        if cat_servicos:
            st.markdown("#### " + cat_nome)
            for s in cat_servicos:
                col1, col2, col3 = st.columns([1, 4, 2])
                with col1:
                    st.markdown('<div style="font-size:32px;text-align:center;">' + str(s["icone"]) + '</div>', unsafe_allow_html=True)
                with col2:
                    st.markdown("**" + str(s["nome"]) + "**")
                    st.caption(str(s["descricao"]) + " | ~" + str(s["duracao_min"]) + " min")
                with col3:
                    st.markdown('<div class="servico-preco">R$ ' + f'{s["preco"]:.0f}' + '</div>', unsafe_allow_html=True)
                    if st.button("Agendar", key="srv_" + str(s["id"]), use_container_width=True):
                        ir_para("escolher_manicure", servico_id=s["id"])
                        st.rerun()
                st.divider()

def tela_escolher_manicure():
    st.markdown('<div class="header-unha"><h1>Escolher Profissional</h1><p>Selecione quem vai cuidar de voce</p></div>', unsafe_allow_html=True)
    if st.button("Voltar"):
        ir_para("cliente_home")
        st.rerun()
    manicures = query("SELECT u.*, (SELECT COUNT(*) FROM agendamentos a WHERE a.manicure_id=u.id AND a.status='concluido') as total_atend FROM usuarios u WHERE u.tipo='manicure' AND u.ativo=1 ORDER BY u.avaliacao_media DESC")
    for m in manicures:
        inicial = str(m["nome"]).upper()
        st.markdown('<div class="card"><div style="display:flex; align-items:center; gap:12px;"><div style="background:#C48B9F; color:white; width:56px; height:56px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:24px; font-weight:700;">' + inicial + '</div><div style="flex:1;"><strong style="font-size:16px;">' + str(m["nome"]) + '</strong><br><span class="estrelas">' + estrelas(m["avaliacao_media"] or 5) + '</span> <span style="color:#888; font-size:12px;">(' + str(m["total_avaliacoes"] or 0) + ' avaliacoes)</span><br><span style="color:#888; font-size:12px;">' + str(m["endereco"] or "Atende no local") + ' | ' + str(m["total_atend"]) + ' atendimentos</span></div></div><p style="color:#555; font-style:italic; font-size:12px; margin-top:8px;">' + str(m["bio"] or "") + '</p></div>', unsafe_allow_html=True)
        primeiro = str(m["nome"]).split()
        if st.button("Agendar com " + primeiro, key="man_" + str(m["id"]), use_container_width=True):
            ir_para("agendar", manicure_id=m["id"])
            st.rerun()
def tela_agendar():
    servico_list = query("SELECT * FROM servicos WHERE id=%s", (st.session_state.servico_id,))
    manicure_list = query("SELECT * FROM usuarios WHERE id=%s", (st.session_state.manicure_id,))
    if not servico_list or not manicure_list:
        st.error("Erro ao carregar dados")
        ir_para("cliente_home")
        st.rerun()
        return
    servico = servico_list
    manicure = manicure_list
    st.markdown('<div class="header-unha"><h1>Agendar</h1><p>' + str(servico["icone"]) + ' ' + str(servico["nome"]) + ' com ' + str(manicure["nome"]) + '</p></div>', unsafe_allow_html=True)
    if st.button("Voltar"):
        ir_para("escolher_manicure")
        st.rerun()
    valor_total = servico["preco"]
    valor_manicure = valor_total * (1 - COMISSAO)
    duracao = servico["duracao_min"]
    st.markdown('<div class="card-gold"><span style="font-size:28px;">' + str(servico["icone"]) + '</span> <strong>' + str(servico["nome"]) + '</strong> | ~' + str(duracao) + ' min | <strong style="color:#B8860B; font-size:18px;">R$ ' + f'{valor_total:.2f}' + '</strong></div>', unsafe_allow_html=True)
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
    st.markdown("### Escolha a Data")
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
            partes_inicio = disp["hora_inicio"].split(":")
            h_inicio = int(partes_inicio)
            m_inicio = int(partes_inicio)
            partes_fim = disp["hora_fim"].split(":")
            h_fim = int(partes_fim)
            m_fim = int(partes_fim)
            data_str_br = data_sel.strftime("%d/%m/%Y")
            ocupados = set()
            for ag in agendados:
                if ag["data"] == data_str_br:
                    partes_h = ag["horario"].split(":")
                    h = int(partes_h)
                    m = int(partes_h)
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
            st.markdown("### Horario")
            if horarios_livres:
                horario_sel = st.selectbox("Horarios disponiveis:", horarios_livres)
            else:
                st.warning("Sem horarios livres nesta data. Escolha outra!")
    st.markdown("### Local de Atendimento")
    endereco = st.text_input("Endereco completo *")
    complemento = st.text_input("Complemento (apto, bloco...)")
    st.markdown("### Forma de Pagamento")
    forma_pg = st.radio("Escolha:", ["PIX", "Cartao de Credito", "Cartao de Debito", "Dinheiro"], horizontal=True)
    formas_map = {"PIX": "pix", "Cartao de Credito": "cartao_credito", "Cartao de Debito": "cartao_debito", "Dinheiro": "dinheiro"}
    obs = st.text_area("Observacoes (opcional)")
    st.markdown('<div class="card-gold"><h4>Resumo</h4><p><strong>Servico:</strong> ' + str(servico["nome"]) + '<br><strong>Profissional:</strong> ' + str(manicure["nome"]) + '<br><strong>Data:</strong> ' + str(data_str) + '<br><strong>Horario:</strong> ' + str(horario_sel or "-") + '<br><strong>Pagamento:</strong> ' + str(forma_pg) + '</p><hr><h3 style="color:#B8860B;">TOTAL: R$ ' + f'{valor_total:.2f}' + '</h3></div>', unsafe_allow_html=True)
    if st.button("CONFIRMAR AGENDAMENTO", use_container_width=True):
        if not horario_sel:
            st.error("Selecione um horario!")
            return
        if not endereco:
            st.error("Informe o endereco!")
            return
        data_br = data_sel.strftime("%d/%m/%Y")
        data_lib = (data_sel + timedelta(days=DIAS_RECEBER)).strftime("%d/%m/%Y")
        fp = formas_map.get(forma_pg, "pix")
        conflito = query("SELECT COUNT(*) as cnt FROM agendamentos WHERE manicure_id=%s AND data=%s AND horario=%s AND status IN ('pendente','confirmado')", (st.session_state.manicure_id, data_br, horario_sel))
        if conflito and conflito["cnt"] > 0:
            st.error("Horario acabou de ser reservado!")
            return
        result = execute_returning("INSERT INTO agendamentos (cliente_id,manicure_id,servico_id,data,horario,endereco_atendimento,complemento,valor_total,valor_manicure,valor_comissao,forma_pagamento,observacoes,data_liberacao_manicure) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id", (st.session_state.user_id, st.session_state.manicure_id, st.session_state.servico_id, data_br, horario_sel, endereco, complemento, valor_total, valor_manicure, valor_total * COMISSAO, fp, obs, data_lib))
        if result:
            ag_id = result["id"]
            execute("INSERT INTO transacoes (agendamento_id,tipo,valor,destinatario_id,forma_pagamento,data_prevista_liberacao) VALUES (%s,%s,%s,%s,%s,%s)", (ag_id, "pagamento", valor_total, st.session_state.manicure_id, fp, data_lib))
            execute("INSERT INTO notificacoes (usuario_id,titulo,mensagem,tipo) VALUES (%s,%s,%s,%s)", (st.session_state.manicure_id, "Novo Agendamento!", "Novo agendamento " + data_br + " as " + horario_sel, "agendamento"))
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
    ag = resultado
    st.markdown('<div style="text-align:center; padding:40px 0;"><div style="font-size:70px;">✅</div><h2 style="color:#4CAF50;">Agendamento Confirmado!</h2><p style="color:#888;">A profissional recebera a notificacao</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="card-gold"><h4>' + str(ag["icone"]) + ' ' + str(ag["sn"]) + '</h4><p><strong>Profissional:</strong> ' + str(ag["mn"]) + '<br><strong>Data:</strong> ' + str(ag["data"]) + '<br><strong>Horario:</strong> ' + str(ag["horario"]) + '<br><strong>Local:</strong> ' + str(ag["endereco_atendimento"]) + '<br><strong>Pagamento:</strong> ' + forma_pg_nome(ag["forma_pagamento"]) + '</p><hr><h3 style="color:#B8860B;">Total: R$ ' + f'{ag["valor_total"]:.2f}' + '</h3></div>', unsafe_allow_html=True)
    if st.button("Voltar ao Inicio", use_container_width=True):
        ir_para("cliente_home")
        st.rerun()

def tela_meus_agendamentos():
    st.markdown('<div class="header-unha"><h1>Meus Agendamentos</h1></div>', unsafe_allow_html=True)
    if st.button("Voltar"):
        ir_para("cliente_home")
        st.rerun()
    agendamentos = query("SELECT a.*, s.nome as sn, s.icone, u.nome as mn FROM agendamentos a JOIN servicos s ON a.servico_id=s.id JOIN usuarios u ON a.manicure_id=u.id WHERE a.cliente_id=%s ORDER BY a.data_criacao DESC LIMIT 20", (st.session_state.user_id,))
    if not agendamentos:
        st.info("Nenhum agendamento ainda. Que tal agendar?")
    else:
        for ag in agendamentos:
            st.markdown('<div class="card"><strong>' + str(ag["icone"]) + ' ' + str(ag["sn"]) + '</strong> com ' + str(ag["mn"]) + '<br>' + str(ag["data"]) + ' as ' + str(ag["horario"]) + ' | ' + badge_html(ag["status"]) + ' | <strong style="color:#B8860B;">R$ ' + f'{ag["valor_total"]:.2f}' + '</strong></div>', unsafe_allow_html=True)
            if ag["status"] == "concluido" and ag["avaliacao_nota"] is None:
                if st.button("Avaliar", key="aval_" + str(ag["id"])):
                    ir_para("avaliar", avaliando_id=ag["id"])
                    st.rerun()

def tela_avaliar():
    ag_id = st.session_state.get("avaliando_id")
    resultado = query("SELECT a.*, s.nome as sn, u.nome as mn FROM agendamentos a JOIN servicos s ON a.servico_id=s.id JOIN usuarios u ON a.manicure_id=u.id WHERE a.id=%s", (ag_id,))
    if not resultado:
        ir_para("cliente_home")
        st.rerun()
        return
    ag = resultado
    st.markdown('<div class="header-unha"><h1>Avaliar</h1><p>' + str(ag["sn"]) + ' com ' + str(ag["mn"]) + '</p></div>', unsafe_allow_html=True)
    if st.button("Voltar"):
        ir_para("meus_agendamentos")
        st.rerun()
    st.markdown("### Como foi sua experiencia?")
    nota = st.slider("Nota:", 1, 5, 5)
    textos = {1: "Pessimo", 2: "Ruim", 3: "Regular", 4: "Bom", 5: "Excelente!"}
    st.markdown('<h3 style="text-align:center;">' + textos[nota] + '</h3>', unsafe_allow_html=True)
    comentario = st.text_area("Conte como foi sua experiencia...")
    if st.button("ENVIAR AVALIACAO", use_container_width=True):
        execute("UPDATE agendamentos SET avaliacao_nota=%s, avaliacao_comentario=%s WHERE id=%s", (nota, comentario, ag_id))
        media_result = query("SELECT AVG(avaliacao_nota) as media, COUNT(*) as total FROM agendamentos WHERE manicure_id=%s AND avaliacao_nota IS NOT NULL", (ag["manicure_id"],))
        if media_result:
            execute("UPDATE usuarios SET avaliacao_media=%s, total_avaliacoes=%s WHERE id=%s", (media_result["media"] or 5, media_result["total"] or 0, ag["manicure_id"]))
        execute("INSERT INTO notificacoes (usuario_id,titulo,mensagem,tipo) VALUES (%s,%s,%s,%s)", (ag["manicure_id"], "Avaliacao: " + str(nota) + " estrelas!", comentario or "Sem comentario", "avaliacao"))
        st.success("Avaliacao enviada! Obrigado!")
        st.balloons()
        ir_para("cliente_home")
        st.rerun()

def tela_perfil():
    resultado = query("SELECT * FROM usuarios WHERE id=%s", (st.session_state.user_id,))
    if not resultado:
        ir_para("cliente_home")
        st.rerun()
        return
    user = resultado
    st.markdown('<div class="header-unha"><h1>Meu Perfil</h1></div>', unsafe_allow_html=True)
    if st.button("Voltar"):
        ir_para("cliente_home")
        st.rerun()
    inicial = str(user["nome"]).upper()
    st.markdown('<div class="card" style="text-align:center;"><div style="background:#C48B9F; color:white; width:80px; height:80px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:36px; font-weight:700; margin: 0 auto 10px auto;">' + inicial + '</div><h3>' + str(user["nome"]) + '</h3><p>' + str(user["telefone"]) + '<br>' + str(user["email"] or "Nao informado") + '<br>' + str(user["endereco"] or "Nao informado") + ', ' + str(user["bairro"] or "") + ' - ' + str(user["cidade"] or "") + '</p></div>', unsafe_allow_html=True)

def tela_manicure_home():
    hoje = date.today().strftime("%d/%m/%Y")
    primeiro_nome = st.session_state.user_nome.split()
    st.markdown('<div class="header-unha"><h1>Ola, ' + primeiro_nome + '!</h1><p>Painel da Profissional</p></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Notificacoes", use_container_width=True):
            pass
    with col2:
        if st.button("Sair", use_container_width=True):
            logout()
            st.rerun()
    mes_atual = date.today().strftime("%m/%Y")
    ganhos_result = query("SELECT COALESCE(SUM(valor_manicure),0) as ganhos, COUNT(*) as total FROM agendamentos WHERE manicure_id=%s AND status='concluido' AND data LIKE %s", (st.session_state.user_id, "%" + mes_atual))
    ganhos_mes = ganhos_result["ganhos"] if ganhos_result else 0
    total_atend = ganhos_result["total"] if ganhos_result else 0
    receber_result = query("SELECT COALESCE(SUM(valor_manicure),0) as valor FROM agendamentos WHERE manicure_id=%s AND status='concluido' AND pago=0", (st.session_state.user_id,))
    a_receber = receber_result["valor"] if receber_result else 0
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="kpi-box"><div class="kpi-label">Ganhos do Mes</div><div class="kpi-valor" style="color:#4CAF50;">R$ ' + f'{ganhos_mes:.2f}' + '</div><div class="kpi-label">' + str(total_atend) + ' atendimentos</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="kpi-box"><div class="kpi-label">A Receber</div><div class="kpi-valor" style="color:#B8860B;">R$ ' + f'{a_receber:.2f}' + '</div><div class="kpi-label">Liberacao em ' + str(DIAS_RECEBER) + ' dias</div></div>', unsafe_allow_html=True)
    st.markdown("### Hoje (" + hoje + ")")
    hoje_ag = query("SELECT a.*, s.nome as sn, s.icone, u.nome as cn FROM agendamentos a JOIN servicos s ON a.servico_id=s.id JOIN usuarios u ON a.cliente_id=u.id WHERE a.manicure_id=%s AND a.data=%s AND a.status IN ('pendente','confirmado','em_andamento') ORDER BY a.horario", (st.session_state.user_id, hoje))
    if not hoje_ag:
        st.info("Nenhum atendimento hoje. Aproveite!")
    else:
        for ag in hoje_ag:
            st.markdown('<div class="card"><strong>' + str(ag["horario"]) + '</strong> | ' + badge_html(ag["status"]) + '<br>' + str(ag["icone"]) + ' ' + str(ag["sn"]) + '<br>Cliente: ' + str(ag["cn"]) + '<br>' + str(ag["endereco_atendimento"] or "-") + '<br><strong style="color:#4CAF50;">Voce recebe: R$ ' + f'{ag["valor_manicure"]:.2f}' + '</strong></div>', unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            with c1:
                if ag["status"] == "pendente" and st.button("Confirmar", key="conf_" + str(ag["id"])):
                    execute("UPDATE agendamentos SET status='confirmado' WHERE id=%s", (ag["id"],))
                    st.rerun()
            with c2:
                if ag["status"] in ("confirmado", "em_andamento") and st.button("Concluir", key="conc_" + str(ag["id"])):
                    execute("UPDATE agendamentos SET status='concluido' WHERE id=%s", (ag["id"],))
                    execute("INSERT INTO notificacoes (usuario_id,titulo,mensagem,tipo) VALUES (%s,%s,%s,%s)", (ag["cliente_id"], "Atendimento concluido!", "Avalie sua experiencia!", "avaliacao"))
                    st.rerun()
            with c3:
                if ag["status"] != "concluido" and st.button("Cancelar", key="canc_" + str(ag["id"])):
                    execute("UPDATE agendamentos SET status='cancelado' WHERE id=%s", (ag["id"],))
                    st.rerun()
    st.markdown("### Proximos")
    proximos = query("SELECT a.*, s.nome as sn, s.icone, u.nome as cn FROM agendamentos a JOIN servicos s ON a.servico_id=s.id JOIN usuarios u ON a.cliente_id=u.id WHERE a.manicure_id=%s AND a.status IN ('pendente','confirmado') AND a.data > %s ORDER BY a.data, a.horario LIMIT 10", (st.session_state.user_id, hoje))
    if not proximos:
        st.info("Nenhum agendamento futuro")
    else:
        for ag in proximos:
            st.markdown('<div class="card">' + str(ag["data"]) + ' as ' + str(ag["horario"]) + ' | ' + badge_html(ag["status"]) + '<br>' + str(ag["icone"]) + ' ' + str(ag["sn"]) + ' | ' + str(ag["cn"]) + '<br><strong style="color:#4CAF50;">R$ ' + f'{ag["valor_manicure"]:.2f}' + '</strong></div>', unsafe_allow_html=True)

def tela_admin():
    st.markdown('<div style="background: linear-gradient(135deg, #B8860B 0%, #D4A853 100%); padding: 25px 20px; border-radius: 0 0 25px 25px; margin: -6rem -1rem 1.5rem -1rem; text-align:center; box-shadow: 0 4px 15px rgba(212,168,83,0.3);"><h1 style="color:white !important; font-size:28px !important; margin:0 !important;">Painel Admin</h1><p style="color:#FFF8E7; font-size:14px;">Unha Click - Dashboard</p></div>', unsafe_allow_html=True)
    if st.button("Sair"):
        logout()
        st.rerun()
    stats = query("SELECT (SELECT COUNT(*) FROM usuarios WHERE tipo='cliente') as clientes, (SELECT COUNT(*) FROM usuarios WHERE tipo='manicure') as manicures, (SELECT COUNT(*) FROM agendamentos) as agendamentos, (SELECT COALESCE(SUM(valor_total),0) FROM agendamentos WHERE status='concluido') as faturamento, (SELECT COALESCE(SUM(valor_comissao),0) FROM agendamentos WHERE status='concluido') as comissao")
    s = stats if stats else {"clientes": 0, "manicures": 0, "agendamentos": 0, "faturamento": 0, "comissao": 0}
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown('<div class="kpi-box"><div style="font-size:24px;">Clientes</div><div class="kpi-valor" style="color:#8B5E6B;">' + str(s["clientes"]) + '</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="kpi-box"><div style="font-size:24px;">Manicures</div><div class="kpi-valor" style="color:#8B5E6B;">' + str(s["manicures"]) + '</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="kpi-box"><div style="font-size:24px;">Agendamentos</div><div class="kpi-valor" style="color:#2196F3;">' + str(s["agendamentos"]) + '</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="kpi-box"><div style="font-size:24px;">Faturamento</div><div class="kpi-valor" style="color:#4CAF50;">R$ ' + f'{s["faturamento"]:.0f}' + '</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="card-gold" style="text-align:center; margin-top:15px;"><strong style="color:#B8860B; font-size:16px;">SUA COMISSAO (20%)</strong><h2 style="color:#B8860B; margin:10px 0;">R$ ' + f'{s["comissao"]:.2f}' + '</h2></div>', unsafe_allow_html=True)
    st.markdown("### Ultimos Agendamentos")
    ultimos = query("SELECT a.*, s.nome as sn, u1.nome as cn, u2.nome as mn FROM agendamentos a JOIN servicos s ON a.servico_id=s.id JOIN usuarios u1 ON a.cliente_id=u1.id JOIN usuarios u2 ON a.manicure_id=u2.id ORDER BY a.data_criacao DESC LIMIT 10")
    for a in ultimos:
        st.markdown('<div class="card"><strong>' + str(a["sn"]) + '</strong> | ' + str(a["cn"]) + ' -> ' + str(a["mn"]) + '<br>' + str(a["data"]) + ' ' + str(a["horario"]) + ' | ' + badge_html(a["status"]) + ' | <strong style="color:#B8860B;">R$ ' + f'{a["valor_total"]:.2f}' + '</strong></div>', unsafe_allow_html=True)

telas = {"login": tela_login, "cadastro": tela_cadastro, "cliente_home": tela_cliente_home, "escolher_manicure": tela_escolher_manicure, "agendar": tela_agendar, "confirmacao": tela_confirmacao, "meus_agendamentos": tela_meus_agendamentos, "avaliar": tela_avaliar, "perfil": tela_perfil, "manicure_home": tela_manicure_home, "admin": tela_admin}
tela_atual = st.session_state.get("tela", "login")
if tela_atual in telas:
    telas[tela_atual]()
else:
    tela_login()
