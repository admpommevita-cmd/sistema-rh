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
                        conn.close()
