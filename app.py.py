import streamlit as st
import sqlite3
import pandas as pd
import hashlib
import io
import datetime

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="Sistema de Gestão de Pessoal - Supera",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_FILE = "supera_rh.db"

# ==============================================================================
# FUNÇÕES DE BANCO DE DADOS & AUTENTICAÇÃO
# ==============================================================================
def get_connection():
    return sqlite3.connect(DB_FILE)

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # Tabela de Usuários
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha_hash TEXT NOT NULL,
            perfil TEXT NOT NULL,
            unidade TEXT DEFAULT 'Todas'
        )
    ''')
    
    # Tabela de Colaboradores
    c.execute('''
        CREATE TABLE IF NOT EXISTS colaboradores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            funcional TEXT UNIQUE,
            nome TEXT NOT NULL,
            cpf TEXT,
            data_nascimento TEXT,
            sexo TEXT,
            naturalidade TEXT,
            nome_pai TEXT,
            nome_mae TEXT,
            cep TEXT,
            endereco TEXT,
            numero TEXT,
            complemento TEXT,
            bairro TEXT,
            cidade TEXT,
            uf TEXT,
            rg TEXT,
            orgao_emissor TEXT,
            ctps TEXT,
            pis TEXT,
            data_admissao TEXT,
            cod_funcao TEXT,
            funcao TEXT,
            filial TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Ativo',
            carga_horaria TEXT,
            telefone TEXT,
            email TEXT,
            salario_base REAL,
            depend_irpf INTEGER DEFAULT 0,
            depend_salario INTEGER DEFAULT 0,
            banco TEXT,
            agencia TEXT,
            conta TEXT,
            chave_pix TEXT,
            vale_transporte TEXT DEFAULT 'Não',
            assistencia_medica TEXT DEFAULT 'Não'
        )
    ''')
    
    # Inserir usuários padrão se não existirem
    c.execute("SELECT COUNT(*) FROM usuarios")
    if c.fetchone()[0] == 0:
        usuarios_default = [
            ("Administrador RH", "admin@supera.com", make_hashes("admin123"), "Administrador", "Todas"),
            ("Gestor Barueri", "editor.barueri@supera.com", make_hashes("editor123"), "Editor", "Hospital Barueri / Supera"),
            ("Consulta Operacional", "consulta@supera.com", make_hashes("user123"), "Visualizador", "Todas")
        ]
        c.executemany("INSERT INTO usuarios (nome, email, senha_hash, perfil, unidade) VALUES (?,?,?,?,?)", usuarios_default)
    
    # Inserir dados iniciais de demonstração se tabela estiver totalmente vazia
    c.execute("SELECT COUNT(*) FROM colaboradores")
    if c.fetchone()[0] == 0:
        colaboradores_seed = [
            ("10300669", "ADEILDA MARIA FELIX DE ANDRADE DE LIMA", "810189594-91", "10/06/1971", "F", "Catende", "ANTONIO FELIX DE ANDRADE", "HILDA MARIA DE ANDRADE", "06300-000", "71", "", "Centro", "Barueri", "SP", "570867964", "SSP", "32712/PE", "13669862772", "17/01/2022", "759", "AUXILIAR DE SERVIÇOS GERAIS", "Hospital Barueri / Supera", "Ativo", "08:00-16:20 - 6X1", "11981018959", "adeilda@email.com", 1440.38, 0, 0, "33", "328", "20059744", "81018959491", "Sim", "Sim"),
            ("10300796", "ADEILDE FERNANDES DO NASCIMENTO", "115014738-59", "15/05/1963", "F", "Viçosa", "JOSE FRANCISCO DO NASCIMENTO", "MARIZA FERNANDES LOPES", "06680-103", "257", "APTO 243", "CDHU", "Barueri", "SP", "244147085", "SSP", "46760/SP", "16965114003", "08/01/2021", "759", "AUXILIAR DE SERVIÇOS GERAIS", "Hospital Barueri / Supera", "Demitido", "07:00-19:00 - 12x36", "11911414445", "", 1440.38, 0, 0, "33", "134", "710156280", "11501473859", "Sim", "Não"),
            ("10300599", "ADILSON ANTONIO SILVA", "948051216-53", "11/06/1973", "M", "Três Corações", "JOAO MARIANO DA SILVA FILHO", "MARIA ZITA MACHADO SILVA", "08031-760", "150", "", "Jardim", "São Paulo", "SP", "39476981", "SSP", "68566/SP", "12498609174", "20/08/2021", "758", "AUXILIAR DE COZINHA", "Camino School / Supera", "Ativo", "07:00-16:48 Seg a Sex", "11982815992", "adilson@email.com", 1440.38, 0, 0, "33", "134", "10344121", "4094-47168-8", "Sim", "Sim"),
            ("10300134", "ADILSON NASCIMENTO DO MONTE", "242793843-22", "03/06/1974", "M", "Recife", "AMARO JOSE DO MONTE", "AURINETE NOEMIA NASCIMENTO", "54280-745", "260", "", "Várzea", "Recife", "PE", "4419510", "SSP", "70481/PE", "12612189779", "06/01/2016", "9", "COZINHEIRO (A) I", "Fund.Alt.Vent.- FAV/Supera", "Demitido", "06:00-16:00 Seg a Sex", "81988622174", "", 1400.00, 0, 1, "237", "32018", "5210542", "81988622174", "Sim", "Não"),
            ("10300610", "ADRIELEN REIS ARCANJO", "114033016-03", "24/07/1993", "F", "Campo do Meio", "LOURENÇO ARCANJO", "EDVALDA REIS", "06395-060", "62", "CASA 1", "Ariston", "Carapicuíba", "SP", "601653142", "SSP", "39003/MG", "13819269893", "01/09/2021", "14", "NUTRICIONISTA", "Hospital Barueri / Supera", "Ativo", "14:00-22:20 Seg a Sab", "11985711663", "adrielen@email.com", 3452.53, 0, 0, "33", "134", "10345115", "11985711663", "Sim", "Não")
        ]
        
        c.executemany('''
            INSERT INTO colaboradores (
                funcional, nome, cpf, data_nascimento, sexo, naturalidade, nome_pai, nome_mae,
                cep, endereco, numero, complemento, bairro, cidade, uf, rg, orgao_emissor, ctps, pis,
                data_admissao, cod_funcao, funcao, filial, status, carga_horaria, telefone, email,
                salario_base, depend_irpf, depend_salario, banco, agencia, conta, chave_pix, vale_transporte, assistencia_medica
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ''', colaboradores_seed)
        
    conn.commit()
    conn.close()

def authenticate_user(email, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, nome, email, perfil, unidade, senha_hash FROM usuarios WHERE email = ?", (email,))
    user_data = c.fetchone()
    conn.close()
    
    if user_data:
        if check_hashes(password, user_data[5]):
            return {
                "id": user_data[0],
                "nome": user_data[1],
                "email": user_data[2],
                "perfil": user_data[3],
                "unidade": user_data[4]
            }
    return None

def mask_cpf(cpf):
    if not cpf or len(str(cpf).strip()) < 11:
        return "***.***.***-**"
    clean_cpf = ''.join(filter(str.isdigit, str(cpf)))
    if len(clean_cpf) == 11:
        return f"***.***.{clean_cpf[6:9]}-{clean_cpf[9:11]}"
    return "***.***.***-**"

def map_dataframe_columns(df):
    col_map = {}
    for col in df.columns:
        c_clean = str(col).strip().upper()
        if "FUNCIONAL" in c_clean or "MATRICULA" in c_clean or "MATRÍCULA" in c_clean:
            col_map[col] = "funcional"
        elif "NOME" in c_clean and "PAI" not in c_clean and "MÃE" not in c_clean and "MAE" not in c_clean:
            col_map[col] = "nome"
        elif "CPF" in c_clean:
            col_map[col] = "cpf"
        elif "NASCIMENTO" in c_clean or "DATA NASC" in c_clean:
            col_map[col] = "data_nascimento"
        elif "SEXO" in c_clean:
            col_map[col] = "sexo"
        elif "NATURAL" in c_clean:
            col_map[col] = "naturalidade"
        elif "PAI" in c_clean:
            col_map[col] = "nome_pai"
        elif "MÃE" in c_clean or "MAE" in c_clean:
            col_map[col] = "nome_mae"
        elif "CEP" in c_clean:
            col_map[col] = "cep"
        elif "LOGRADOURO" in c_clean or "ENDEREÇO" in c_clean or "ENDERECO" in c_clean:
            col_map[col] = "endereco"
        elif "NÚMERO" in c_clean or "NUMERO" in c_clean:
            col_map[col] = "numero"
        elif "COMPLEMENTO" in c_clean:
            col_map[col] = "complemento"
        elif "BAIRRO" in c_clean:
            col_map[col] = "bairro"
        elif "LOCALIDADE" in c_clean or "CIDADE" in c_clean:
            col_map[col] = "cidade"
        elif "UF" in c_clean and "CTPS" not in c_clean:
            col_map[col] = "uf"
        elif "DOCUMENTO" in c_clean or "RG" in c_clean:
            col_map[col] = "rg"
        elif "EMISSOR" in c_clean or "ORGÃO" in c_clean or "ORGAO" in c_clean:
            col_map[col] = "orgao_emissor"
        elif "CTPS" in c_clean:
            col_map[col] = "ctps"
        elif "PIS" in c_clean:
            col_map[col] = "pis"
        elif "ADMISSÃO" in c_clean or "ADMISSAO" in c_clean or "DATA ADM" in c_clean or "ADMISS" in c_clean:
            col_map[col] = "data_admissao"
        elif "CÓD FUNÇÃO" in c_clean or "COD FUNCAO" in c_clean or "CÓDIGO FUNÇÃO" in c_clean or "CÓD" in c_clean:
            col_map[col] = "cod_funcao"
        elif "FUNÇÃO" in c_clean or "FUNCAO" in c_clean or "CARGO" in c_clean:
            col_map[col] = "funcao"
        elif "FILIAL" in c_clean or "UNIDADE" in c_clean:
            col_map[col] = "filial"
        elif "STATUS" in c_clean or "SITUAÇÃO" in c_clean or "SITUACAO" in c_clean:
            col_map[col] = "status"
        elif "CARGA HORÁRIA" in c_clean or "CARGA HORARIA" in c_clean or "HORÁRIO" in c_clean or "HORARIO" in c_clean or "ESCALA" in c_clean:
            col_map[col] = "carga_horaria"
        elif "TELEFONE" in c_clean or "CELULAR" in c_clean or "CONTATO" in c_clean:
            col_map[col] = "telefone"
        elif "E-MAIL" in c_clean or "EMAIL" in c_clean:
            col_map[col] = "email"
        elif "SALÁRIO" in c_clean or "SALARIO" in c_clean or "SALÁRIO BASE" in c_clean:
            col_map[col] = "salario_base"
        elif "BANCO" in c_clean:
            col_map[col] = "banco"
        elif "AGÊNCIA" in c_clean or "AGENCIA" in c_clean:
            col_map[col] = "agencia"
        elif "CONTA" in c_clean:
            col_map[col] = "conta"
        elif "PIX" in c_clean:
            col_map[col] = "chave_pix"
        elif "VALE TRANSPORTE" in c_clean or "VT" in c_clean:
            col_map[col] = "vale_transporte"
        elif "ASSISTÊNCIA" in c_clean or "ASSISTENCIA" in c_clean or "GNDI" in c_clean:
            col_map[col] = "assistencia_medica"
    return col_map

# ==============================================================================
# INICIALIZAÇÃO DE ESTADO E BANCO DE DADOS
# ==============================================================================
init_db()

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user' not in st.session_state:
    st.session_state['user'] = None

# ==============================================================================
# TELA DE LOGIN
# ==============================================================================
if not st.session_state['logged_in']:
    st.markdown("<h2 style='text-align: center;'>🔐 Sistema de Gestão e Registro de Pessoal</h2>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #555;'>Supera Alimentação & Serviços</h4>", unsafe_allow_html=True)
    st.divider()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("Acesso ao Sistema")
        with st.form("login_form"):
            email_input = st.text_input("E-mail do Usuário", value="admin@supera.com")
            password_input = st.text_input("Senha", type="password", value="admin123")
            submit_login = st.form_submit_button("Entrar no Sistema", use_container_width=True)
            
            if submit_login:
                user = authenticate_user(email_input, password_input)
                if user:
                    st.session_state['logged_in'] = True
                    st.session_state['user'] = user
                    st.success(f"Bem-vindo(a), {user['nome']}!")
                    st.rerun()
                else:
                    st.error("E-mail ou senha incorretos. Tente novamente.")
        
        st.info("""
        💡 **Credenciais de Teste:**
        * **Administrador (RH Total)**: `admin@supera.com` | `admin123`
        * **Editor (Gestor Barueri)**: `editor.barueri@supera.com` | `editor123`
        * **Visualizador (Apenas Consulta)**: `consulta@supera.com` | `user123`
        """)
    st.stop()

# ==============================================================================
# MENU PRINCIPAL E SESSÃO ATIVA
# ==============================================================================
current_user = st.session_state['user']

with st.sidebar:
    st.title("🏢 Supera RH Web")
    st.write(f"👤 **{current_user['nome']}**")
    st.caption(f"Perfil: **{current_user['perfil']}**")
    if current_user['unidade'] != 'Todas':
        st.caption(f"Escopo: `{current_user['unidade']}`")
    st.divider()
    
    menu = st.radio(
        "Navegação:",
        ["📊 Dashboard de RH", "👥 Cadastros de Colaboradores", "🔍 Pesquisa & Relatórios", "⚙️ Gerenciar Usuários"]
    )
    
    st.divider()
    if st.button("🚪 Sair do Sistema", use_container_width=True):
        st.session_state['logged_in'] = False
        st.session_state['user'] = None
        st.rerun()

# ==============================================================================
# FUNÇÕES DE CARREGAMENTO DE DADOS COM RBAC
# ==============================================================================
def load_colaboradores_df(unidade_filtro=None, status_filtro=None):
    conn = get_connection()
    query = "SELECT * FROM colaboradores WHERE 1=1"
    params = []
    
    if current_user['perfil'] == 'Editor' and current_user['unidade'] != 'Todas':
        query += " AND filial = ?"
        params.append(current_user['unidade'])
    elif unidade_filtro and unidade_filtro != 'Todas':
        query += " AND filial = ?"
        params.append(unidade_filtro)
        
    if status_filtro and status_filtro != 'Todos':
        query += " AND status = ?"
        params.append(status_filtro)
        
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

# ==============================================================================
# MÓDULO 1: DASHBOARD DE RH
# ==============================================================================
if menu == "📊 Dashboard de RH":
    st.title("📊 Painel de Indicadores de Gestão de Pessoal")
    st.markdown("Visão consolidada da força de trabalho por filial, função e status contratual.")
    
    df_all = load_colaboradores_df()
    
    c1, c2, c3, c4 = st.columns(4)
    total_func = len(df_all)
    total_ativos = len(df_all[df_all['status'] == 'Ativo'])
    total_demitidos = len(df_all[df_all['status'] == 'Demitido'])
    total_afastados = len(df_all[df_all['status'].str.contains('Afastado', na=False)])
    
    c1.metric("Total Cadastrados", total_func)
    c2.metric("Ativos na Equipe", total_ativos, delta=f"{int(total_ativos/total_func*100) if total_func>0 else 0}% do total")
    c3.metric("Desligados / Demitidos", total_demitidos)
    c4.metric("Afastados (INSS / Outros)", total_afastados)
    
    st.divider()
    
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.subheader("🏢 Distribuição por Filial / Unidade")
        if not df_all.empty:
            filial_counts = df_all['filial'].value_counts().reset_index()
            filial_counts.columns = ['Filial', 'Quantidade']
            st.bar_chart(filial_counts.set_index('Filial'))
        else:
            st.info("Nenhum registro encontrado.")
            
    with col_g2:
        st.subheader("👔 Principais Cargos / Funções")
        if not df_all.empty:
            cargo_counts = df_all['funcao'].value_counts().head(8).reset_index()
            cargo_counts.columns = ['Função', 'Quantidade']
            st.dataframe(cargo_counts, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum registro encontrado.")

    st.subheader("📋 Resumo por Status Contratual")
    if not df_all.empty:
        status_df = df_all.groupby(['filial', 'status']).size().unstack(fill_value=0)
        st.dataframe(status_df, use_container_width=True)

# ==============================================================================
# MÓDULO 2: CADASTROS DE COLABORADORES (CRUD & IMPORTAÇÃO)
# ==============================================================================
elif menu == "👥 Cadastros de Colaboradores":
    st.title("👥 Gestão de Colaboradores")
    
    tab_list, tab_novo, tab_editar, tab_import = st.tabs([
        "📋 Listagem Geral", 
        "➕ Adicionar Colaborador", 
        "✏️ Atualizar / Editar Cadastro",
        "📥 Importar Planilha (Excel/CSV)"
    ])
    
    with tab_list:
        st.subheader("Colaboradores Cadastrados")
        
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            conn = get_connection()
            unidades_list = ["Todas"] + [u[0] for u in conn.execute("SELECT DISTINCT filial FROM colaboradores").fetchall() if u[0]]
            conn.close()
            sel_unidade = st.selectbox("Filtrar por Unidade/Filial:", unidades_list)
        with f_col2:
            sel_status = st.selectbox("Filtrar por Status:", ["Todos", "Ativo", "Demitido", "Afastado INSS"])
            
        df_display = load_colaboradores_df(sel_unidade, sel_status)
        
        if current_user['perfil'] != 'Administrador':
            if 'salario_base' in df_display.columns:
                df_display['salario_base'] = None
            if 'banco' in df_display.columns:
                df_display['banco'] = "***"
            if 'conta' in df_display.columns:
                df_display['conta'] = "******"
            if 'chave_pix' in df_display.columns:
                df_display['chave_pix'] = "Confidencial"
                
        if current_user['perfil'] == 'Visualizador':
            if 'cpf' in df_display.columns:
                df_display['cpf'] = df_display['cpf'].apply(mask_cpf)
            if 'rg' in df_display.columns:
                df_display['rg'] = "***.***"
            if 'pis' in df_display.columns:
                df_display['pis'] = "***********"

        col_views = ['funcional', 'nome', 'cpf', 'funcao', 'filial', 'status', 'carga_horaria', 'data_admissao', 'telefone', 'salario_base']
        valid_cols = [c for c in col_views if c in df_display.columns]
        
        st.dataframe(df_display[valid_cols], use_container_width=True, hide_index=True)

    with tab_novo:
        if current_user['perfil'] == 'Visualizador':
            st.warning("⚠️ Seu perfil é de **Visualizador** e não possui permissão para cadastrar novos colaboradores.")
        else:
            st.subheader("Cadastrar Novo Colaborador")
            with st.form("form_novo_colaborador", clear_on_submit=True):
                st.markdown("##### 1. Informações Contratuais e Empresa")
                c1, c2, c3, c4 = st.columns(4)
                f_funcional = c1.text_input("Matrícula / Funcional*")
                f_nome = c2.text_input("Nome Completo*")
                f_filial = c3.selectbox("Filial / Unidade*", [
                    "Hospital Barueri / Supera", 
                    "Camino School / Supera", 
                    "Hospital Cubatão/ Supera", 
                    "Fund.Alt.Vent.- FAV/Supera", 
                    "Hospital Mandaqui/ Supera", 
                    "Hospital Picos / Supera", 
                    "Hospital Paulista / Supera",
                    "Hospital Mutinga / Supera",
                    "Singularidades / Supera",
                    "Sede - Supera"
                ])
                f_status = c4.selectbox("Status Inicial*", ["Ativo", "Afastado INSS", "Demitido"])
                
                c5, c6, c7, c8 = st.columns(4)
                f_funcao = c5.text_input("Função / Cargo*", value="AUXILIAR DE COZINHA")
                f_cod_funcao = c6.text_input("Código Função", value="758")
                f_admissao = c7.date_input("Data de Admissão", value=datetime.date.today()).strftime("%d/%m/%Y")
                f_carga_horaria = c8.text_input("Carga Horária / Escala", value="07:00-16:48 Seg a Sex")
                
                st.markdown("##### 2. Documentos Pessoais & Dados de Contato")
                d1, d2, d3, d4, d5 = st.columns(5)
                f_cpf = d1.text_input("CPF*")
                f_data_nasc = d2.text_input("Data Nascimento (DD/MM/AAAA)")
                f_sexo = d3.selectbox("Sexo", ["F", "M"])
                f_rg = d4.text_input("RG / Documento")
                f_pis = d5.text_input("PIS")
                
                ct1, ct2, ct3 = st.columns(3)
                f_naturalidade = ct1.text_input("Naturalidade")
                f_telefone = ct2.text_input("Telefone de Contato")
                f_email = ct3.text_input("E-mail Profissional/Pessoal")
                
                st.markdown("##### 3. Endereço Residencial")
                e1, e2, e3, e4 = st.columns([1, 2, 1, 1])
                f_cep = e1.text_input("CEP")
                f_endereco = e2.text_input("Logradouro / Endereço")
                f_numero = e3.text_input("Número")
                f_complemento = e4.text_input("Complemento")
                
                e5, e6, e7 = st.columns(3)
                f_bairro = e5.text_input("Bairro")
                f_cidade = e6.text_input("Cidade / Localidade", value="Barueri")
                f_uf = e7.text_input("UF", value="SP")
                
                st.markdown("##### 4. Dados Financeiros & Benefícios (Privativo RH)")
                if current_user['perfil'] == 'Administrador':
                    b1, b2, b3, b4 = st.columns(4)
                    f_salario = b1.number_input("Salário Base (R$)", value=1702.47, step=50.0)
                    f_banco = b2.text_input("Banco (Código ou Nome)", value="33 - Santander")
                    f_agencia = b3.text_input("Agência")
                    f_conta = b4.text_input("Conta Corrente/Poupança")
                    
                    p1, p2, p3 = st.columns(3)
                    f_chave_pix = p1.text_input("Chave PIX")
                    f_vt = p2.selectbox("Vale Transporte?", ["Sim", "Não"])
                    f_am = p3.selectbox("Assistência Médica?", ["Sim", "Não"])
                else:
                    st.info("ℹ️ Dados financeiros só podem ser inseridos pelo perfil Administrador.")
                    f_salario, f_banco, f_agencia, f_conta, f_chave_pix = 0.0, "", "", "", ""
                    f_vt, f_am = "Não", "Não"
                    
                salvar_btn = st.form_submit_button("💾 Salvar Cadastro de Colaborador", use_container_width=True)
                
                if salvar_btn:
                    if not f_nome or not f_funcional:
                        st.error("Preencha os campos obrigatórios (Nome e Matrícula/Funcional).")
                    else:
                        conn = get_connection()
                        c = conn.cursor()
                        try:
                            c.execute('''
                                INSERT INTO colaboradores (
                                    funcional, nome, cpf, data_nascimento, sexo, naturalidade,
                                    cep, endereco, numero, complemento, bairro, cidade, uf,
                                    rg, pis, data_admissao, cod_funcao, funcao, filial, status,
                                    carga_horaria, telefone, email, salario_base, banco, agencia,
                                    conta, chave_pix, vale_transporte, assistencia_medica
                                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                            ''', (
                                f_funcional, f_nome, f_cpf, f_data_nasc, f_sexo, f_naturalidade,
                                f_cep, f_endereco, f_numero, f_complemento, f_bairro, f_cidade, f_uf,
                                f_rg, f_pis, f_admissao, f_cod_funcao, f_funcao, f_filial, f_status,
                                f_carga_horaria, f_telefone, f_email, f_salario, f_banco, f_agencia,
                                f_conta, f_chave_pix, f_vt, f_am
                            ))
                            conn.commit()
                            st.success(f"Colaborador **{f_nome}** cadastrado com sucesso!")
                        except sqlite3.IntegrityError:
                            st.error(f"A matrícula/funcional '{f_funcional}' já existe no banco de dados.")
                        finally:
                            conn.close()

    with tab_editar:
        if current_user['perfil'] == 'Visualizador':
            st.warning("⚠️ Seu perfil é de **Visualizador** e não possui permissão para editar registros.")
        else:
            st.subheader("Editar Dados de Colaborador")
            conn = get_connection()
            colab_list = conn.execute("SELECT id, funcional, nome, filial FROM colaboradores").fetchall()
            conn.close()
            
            if colab_list:
                options = {f"{c[1]} - {c[2]} ({c[3]})": c[0] for c in colab_list}
                selected_colab = st.selectbox("Selecione o Colaborador para Atualizar:", list(options.keys()))
                colab_id = options[selected_colab]
                
                conn = get_connection()
                c = conn.cursor()
                c.execute("SELECT * FROM colaboradores WHERE id = ?", (colab_id,))
                col_data = c.fetchone()
                colnames = [desc[0] for desc in c.description]
                c_dict = dict(zip(colnames, col_data))
                conn.close()
                
                with st.form("form_edit_colaborador"):
                    st.markdown(f"Editando: **{c_dict['nome']}** (Matrícula: {c_dict['funcional']})")
                    
                    e_col1, e_col2, e_col3 = st.columns(3)
                    ef_filial = e_col1.text_input("Filial / Unidade", value=c_dict['filial'])
                    ef_status = e_col2.selectbox("Status", ["Ativo", "Demitido", "Afastado INSS", "Afastado (RESCISÃO INDIRETA)"], index=0 if c_dict['status']=='Ativo' else 1)
                    ef_funcao = e_col3.text_input("Função", value=c_dict['funcao'])
                    
                    e_col4, e_col5, e_col6 = st.columns(3)
                    ef_tel = e_col4.text_input("Telefone", value=c_dict['telefone'] or "")
                    ef_email = e_col5.text_input("E-mail", value=c_dict['email'] or "")
                    ef_escala = e_col6.text_input("Carga Horária", value=c_dict['carga_horaria'] or "")
                    
                    if current_user['perfil'] == 'Administrador':
                        st.markdown("##### Dados Financeiros (Administrador)")
                        ef_sal1, ef_sal2, ef_sal3 = st.columns(3)
                        ef_salario = ef_sal1.number_input("Salário Base", value=float(c_dict['salario_base'] or 0.0))
                        ef_banco = ef_sal2.text_input("Banco", value=c_dict['banco'] or "")
                        ef_conta = ef_sal3.text_input("Conta", value=c_dict['conta'] or "")
                        ef_pix = st.text_input("Chave PIX", value=c_dict['chave_pix'] or "")
                    else:
                        ef_salario = c_dict['salario_base']
                        ef_banco = c_dict['banco']
                        ef_conta = c_dict['conta']
                        ef_pix = c_dict['chave_pix']
                        
                    btn_update = st.form_submit_button("🔄 Salvar Alterações", use_container_width=True)
                    
                    if btn_update:
                        conn = get_connection()
                        c = conn.cursor()
                        c.execute('''
                            UPDATE colaboradores SET
                                filial = ?, status = ?, funcao = ?, telefone = ?,
                                email = ?, carga_horaria = ?, salario_base = ?,
                                banco = ?, conta = ?, chave_pix = ?
                            WHERE id = ?
                        ''', (ef_filial, ef_status, ef_funcao, ef_tel, ef_email, ef_escala, ef_salario, ef_banco, ef_conta, ef_pix, colab_id))
                        conn.commit()
                        conn.close()
                        st.success("Dados do colaborador atualizados com sucesso!")
                        st.rerun()

    # ABA IMPORTAÇÃO DE PLANILHA
    with tab_import:
        if current_user['perfil'] == 'Visualizador':
            st.warning("⚠️ Seu perfil é de **Visualizador** e não possui permissão para importar planilhas.")
        else:
            st.subheader("📥 Carga em Lote de Colaboradores via Planilha")
            st.markdown("""
            Envie sua planilha em formato **Excel (`.xlsx` ou `.xls`)** ou **CSV (`.csv`)** para cadastrar ou atualizar todos os **600+ funcionários** de uma só vez no banco de dados.
            """)
            
            uploaded_file = st.file_uploader("Selecione o arquivo da sua planilha:", type=["xlsx", "xls", "csv"])
            
            if uploaded_file is not None:
                try:
                    if uploaded_file.name.endswith('.csv'):
                        try:
                            df_upload = pd.read_csv(uploaded_file, encoding='utf-8')
                        except UnicodeDecodeError:
                            uploaded_file.seek(0)
                            df_upload = pd.read_csv(uploaded_file, encoding='latin1')
                    else:
                        df_upload = pd.read_excel(uploaded_file)
                    
                    st.success(f"Planilha carregada com sucesso! Total de linhas encontradas: **{len(df_upload)}**")
                    
                    col_map = map_dataframe_columns(df_upload)
                    
                    st.markdown("##### Mapeamento Automático de Colunas Identificadas")
                    map_summary = [{"Coluna na Planilha": k, "Campo no Sistema": v} for k, v in col_map.items()]
                    st.dataframe(pd.DataFrame(map_summary), use_container_width=True)
                    
                    st.markdown("##### Pré-visualização dos Dados (Primeiras 5 Linhas)")
                    st.dataframe(df_upload.head(5), use_container_width=True)
                    
                    mod_import = st.radio("Modo de Importação:", [
                        "Atualizar cadastros existentes e inserir novos (Recomendado)",
                        "Substituir totalmente o banco de dados atual pela planilha"
                    ])
                    
                    btn_confirm = st.button("🚀 Confirmar e Importar para o Banco de Dados", type="primary", use_container_width=True)
                    
                    if btn_confirm:
                        conn = get_connection()
                        c = conn.cursor()
                        
                        if "Substituir totalmente" in mod_import:
                            c.execute("DELETE FROM colaboradores")
                            conn.commit()
                            
                        importados = 0
                        atualizados = 0
                        
                        for _, row in df_upload.iterrows():
                            # Extrair campos baseados no col_map
                            record = {}
                            for orig_col, mapped_field in col_map.items():
                                val = row[orig_col]
                                if pd.isna(val) or val is None:
                                    val = ""
                                else:
                                    val = str(val).strip()
                                record[mapped_field] = val
                            
                            # Garantir campos mínimos
                            funcional = record.get("funcional", "")
                            nome = record.get("nome", "")
                            cpf = record.get("cpf", "")
                            
                            if not nome and not funcional and not cpf:
                                continue # pular linha vazia
                                
                            if not funcional:
                                if cpf:
                                    funcional = ''.join(filter(str.isdigit, str(cpf)))
                                else:
                                    funcional = f"AUTO_{importados+atualizados+1}"
                                    
                            filial = record.get("filial", "Hospital Barueri / Supera")
                            status = record.get("status", "Ativo")
                            funcao = record.get("funcao", "AUXILIAR DE COZINHA")
                            
                            # Tratar salário
                            sal_str = record.get("salario_base", "0")
                            try:
                                sal_clean = str(sal_str).replace("R$", "").replace(".", "").replace(",", ".").strip()
                                salario_val = float(sal_clean) if sal_clean else 0.0
                            except ValueError:
                                salario_val = 0.0
                                
                            # Verificar se já existe
                            c.execute("SELECT id FROM colaboradores WHERE funcional = ? OR (cpf != '' AND cpf = ?)", (funcional, cpf))
                            existing = c.fetchone()
                            
                            if existing:
                                c.execute('''
                                    UPDATE colaboradores SET
                                        nome = COALESCE(NULLIF(?,''), nome),
                                        cpf = COALESCE(NULLIF(?,''), cpf),
                                        data_nascimento = COALESCE(NULLIF(?,''), data_nascimento),
                                        sexo = COALESCE(NULLIF(?,''), sexo),
                                        naturalidade = COALESCE(NULLIF(?,''), naturalidade),
                                        nome_pai = COALESCE(NULLIF(?,''), nome_pai),
                                        nome_mae = COALESCE(NULLIF(?,''), nome_mae),
                                        cep = COALESCE(NULLIF(?,''), cep),
                                        endereco = COALESCE(NULLIF(?,''), endereco),
                                        numero = COALESCE(NULLIF(?,''), numero),
                                        complemento = COALESCE(NULLIF(?,''), complemento),
                                        bairro = COALESCE(NULLIF(?,''), bairro),
                                        cidade = COALESCE(NULLIF(?,''), cidade),
                                        uf = COALESCE(NULLIF(?,''), uf),
                                        rg = COALESCE(NULLIF(?,''), rg),
                                        pis = COALESCE(NULLIF(?,''), pis),
                                        data_admissao = COALESCE(NULLIF(?,''), data_admissao),
                                        cod_funcao = COALESCE(NULLIF(?,''), cod_funcao),
                                        funcao = COALESCE(NULLIF(?,''), funcao),
                                        filial = COALESCE(NULLIF(?,''), filial),
                                        status = COALESCE(NULLIF(?,''), status),
                                        carga_horaria = COALESCE(NULLIF(?,''), carga_horaria),
                                        telefone = COALESCE(NULLIF(?,''), telefone),
                                        email = COALESCE(NULLIF(?,''), email),
                                        salario_base = CASE WHEN ? > 0 THEN ? ELSE salario_base END,
                                        banco = COALESCE(NULLIF(?,''), banco),
                                        agencia = COALESCE(NULLIF(?,''), agencia),
                                        conta = COALESCE(NULLIF(?,''), conta),
                                        chave_pix = COALESCE(NULLIF(?,''), chave_pix)
                                    WHERE id = ?
                                ''', (
                                    nome, cpf, record.get("data_nascimento",""), record.get("sexo",""), record.get("naturalidade",""),
                                    record.get("nome_pai",""), record.get("nome_mae",""), record.get("cep",""), record.get("endereco",""),
                                    record.get("numero",""), record.get("complemento",""), record.get("bairro",""), record.get("cidade",""),
                                    record.get("uf",""), record.get("rg",""), record.get("pis",""), record.get("data_admissao",""),
                                    record.get("cod_funcao",""), funcao, filial, status, record.get("carga_horaria",""),
                                    record.get("telefone",""), record.get("email",""), salario_val, salario_val, record.get("banco",""),
                                    record.get("agencia",""), record.get("conta",""), record.get("chave_pix",""), existing[0]
                                ))
                                atualizados += 1
                            else:
                                c.execute('''
                                    INSERT INTO colaboradores (
                                        funcional, nome, cpf, data_nascimento, sexo, naturalidade,
                                        nome_pai, nome_mae, cep, endereco, numero, complemento,
                                        bairro, cidade, uf, rg, pis, data_admissao, cod_funcao,
                                        funcao, filial, status, carga_horaria, telefone, email,
                                        salario_base, banco, agencia, conta, chave_pix, vale_transporte, assistencia_medica
                                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                                ''', (
                                    funcional, nome, cpf, record.get("data_nascimento",""), record.get("sexo",""), record.get("naturalidade",""),
                                    record.get("nome_pai",""), record.get("nome_mae",""), record.get("cep",""), record.get("endereco",""),
                                    record.get("numero",""), record.get("complemento",""), record.get("bairro",""), record.get("cidade",""),
                                    record.get("uf",""), record.get("rg",""), record.get("pis",""), record.get("data_admissao",""),
                                    record.get("cod_funcao",""), funcao, filial, status, record.get("carga_horaria",""),
                                    record.get("telefone",""), record.get("email",""), salario_val, record.get("banco",""),
                                    record.get("agencia",""), record.get("conta",""), record.get("chave_pix",""),
                                    record.get("vale_transporte","Não"), record.get("assistencia_medica","Não")
                                ))
                                importados += 1
                        
                        conn.commit()
                        conn.close()
                        st.balloons()
                        st.success(f"🎉 Importação concluída com sucesso! **{importados} novos cadastros inseridos** e **{atualizados} registros atualizados**.")
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"Erro ao processar o arquivo: {str(e)}")

# ==============================================================================
# MÓDULO 3: PESQUISA & RELATÓRIOS (EXPORTAR)
# ==============================================================================
elif menu == "🔍 Pesquisa & Relatórios":
    st.title("🔍 Busca Avançada e Exportação de Relatórios")
    
    st.subheader("Filtros de Busca")
    q_col1, q_col2, q_col3 = st.columns(3)
    busca_nome = q_col1.text_input("Buscar por Nome ou CPF:")
    busca_filial = q_col2.selectbox("Unidade / Filial:", ["Todas"] + [
        "Hospital Barueri / Supera", "Camino School / Supera", "Hospital Cubatão/ Supera", 
        "Fund.Alt.Vent.- FAV/Supera", "Hospital Mandaqui/ Supera", "Hospital Picos / Supera", "Sede - Supera"
    ])
    busca_status = q_col3.selectbox("Status do Funcionário:", ["Todos", "Ativo", "Demitido", "Afastado INSS"])
    
    conn = get_connection()
    query = "SELECT * FROM colaboradores WHERE 1=1"
    params = []
    
    if busca_nome:
        query += " AND (nome LIKE ? OR cpf LIKE ? OR funcional LIKE ?)"
        params.extend([f"%{busca_nome}%", f"%{busca_nome}%", f"%{busca_nome}%"])
    if busca_filial != "Todas":
        query += " AND filial = ?"
        params.append(busca_filial)
    if busca_status != "Todos":
        query += " AND status = ?"
        params.append(busca_status)
        
    df_result = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    if current_user['perfil'] != 'Administrador':
        if 'salario_base' in df_result.columns:
            df_result['salario_base'] = None
        if 'chave_pix' in df_result.columns:
            df_result['chave_pix'] = "Restrito"
            
    if current_user['perfil'] == 'Visualizador':
        if 'cpf' in df_result.columns:
            df_result['cpf'] = df_result['cpf'].apply(mask_cpf)
            
    st.subheader(f"Resultados Encontrados ({len(df_result)})")
    st.dataframe(df_result, use_container_width=True)
    
    st.divider()
    csv_data = df_result.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar Relatório em CSV (Excel)",
        data=csv_data,
        file_name=f"relatorio_colaboradores_supera_{datetime.date.today().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )

# ==============================================================================
# MÓDULO 4: GERENCIAR USUÁRIOS E PERMISSÕES (ADMIN)
# ==============================================================================
elif menu == "⚙️ Gerenciar Usuários":
    st.title("⚙️ Controle de Usuários e Permissões de Acesso")
    
    if current_user['perfil'] != 'Administrador':
        st.error("⛔ Apenas usuários com perfil **Administrador** podem acessar a gestão de permissões.")
    else:
        st.subheader("Usuários Cadastrados no Sistema")
        conn = get_connection()
        df_users = pd.read_sql_query("SELECT id, nome, email, perfil, unidade FROM usuarios", conn)
        conn.close()
        
        st.dataframe(df_users, use_container_width=True)
        
        st.divider()
        st.subheader("➕ Adicionar Novo Usuário do Sistema")
        with st.form("form_novo_usuario"):
            u_nome = st.text_input("Nome do Usuário")
            u_email = st.text_input("E-mail corporativo")
            u_senha = st.text_input("Senha Inicial", type="password")
            u_perfil = st.selectbox("Perfil de Permissão", ["Administrador", "Editor", "Visualizador"])
            u_unidade = st.selectbox("Restrição de Filial/Unidade", ["Todas", "Hospital Barueri / Supera", "Camino School / Supera", "Hospital Cubatão/ Supera", "Fund.Alt.Vent.- FAV/Supera"])
            
            submit_user = st.form_submit_button("Criar Usuário")
            if submit_user:
                if not u_nome or not u_email or not u_senha:
                    st.error("Preencha todos os campos do novo usuário.")
                else:
                    conn = get_connection()
                    c = conn.cursor()
                    try:
                        c.execute("INSERT INTO usuarios (nome, email, senha_hash, perfil, unidade) VALUES (?,?,?,?,?)",
                                  (u_nome, u_email, make_hashes(u_senha), u_perfil, u_unidade))
                        conn.commit()
                        st.success(f"Usuário **{u_nome}** criado com sucesso!")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error(f"O e-mail '{u_email}' já está cadastrado.")
                    finally:
                        conn.close()
