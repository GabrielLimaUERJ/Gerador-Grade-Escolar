import streamlit as st
import pandas as pd
import random
import json
import os
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font

st.set_page_config(page_title="Gerador de Grade Escolar", layout="wide")

# -------------------------
# GARANTIR QUE JSON EXISTE
# -------------------------
if not os.path.exists("professores.json"):
    with open("professores.json", "w") as f:
        json.dump({}, f)

st.title("📚 Gerador de Grade Escolar")

# -------------------------
# NÚMERO DE TEMPOS E TURMAS
# -------------------------
num_tempos = st.number_input("Número de tempos por dia", min_value=1, max_value=10, value=6)
num_turmas = st.number_input("Número de turmas", min_value=1, max_value=10, value=3)

dias = ["Seg", "Ter", "Qua", "Qui", "Sex"]
tempos = [f"{i+1:02}" for i in range(num_tempos)]
horarios = [f"{d}{t}" for d in dias for t in tempos]

turmas = [f"Turma {i}" for i in range(1, num_turmas + 1)]
st.write("Turmas consideradas:", turmas)

# -------------------------
# MEMÓRIA
# -------------------------
if "professores" not in st.session_state:
    st.session_state.professores = {}

for h in horarios:
    if h not in st.session_state:
        st.session_state[h] = False

# -------------------------
# FUNÇÕES DE MARCAÇÃO
# -------------------------
def marcar_todos():
    for h in horarios:
        st.session_state[h] = True

def limpar_todos():
    for h in horarios:
        st.session_state[h] = False

def marcar_dia(dia):
    for t in tempos:
        st.session_state[f"{dia}{t}"] = True

def limpar_dia(dia):
    for t in tempos:
        st.session_state[f"{dia}{t}"] = False

def salvar_professores():
    with open("professores.json", "w") as f:
        json.dump(st.session_state.professores, f)
    st.success("Professores salvos")

def carregar_professores():
    try:
        with open("professores.json", "r") as f:
            dados = json.load(f)
        if isinstance(dados, dict):
            st.session_state.professores = dados
        else:
            st.session_state.professores = {}
        st.success("Professores carregados")
    except:
        st.session_state.professores = {}
        st.warning("Arquivo vazio ou inexistente")

# -------------------------
# CARREGAMENTO AUTOMÁTICO AO INICIAR
# -------------------------
if not st.session_state.get("professores"):
    carregar_professores()

# -------------------------
# ADICIONAR PROFESSOR
# -------------------------
st.header("Adicionar professor")
nome = st.text_input("Nome do professor")
dois_tempos_seguidos = st.checkbox("Leciona dois tempos seguidos?")
tempos_semana = st.number_input("Quantos tempos este professor vai lecionar por semana?", min_value=1, max_value=num_tempos*len(dias))

col1, col2 = st.columns(2)
col1.button("Marcar todos os horários", on_click=marcar_todos)
col2.button("Limpar todos os horários", on_click=limpar_todos)

st.subheader("Disponibilidade")
cols = st.columns(len(dias))
for i, dia in enumerate(dias):
    with cols[i]:
        st.markdown(f"**{dia}**")
        for tempo in tempos:
            chave = f"{dia}{tempo}"
            st.checkbox(f"Tempo {tempo}", key=chave)
        c1, c2 = st.columns(2)
        c1.button("Marcar todos", key=f"marcar_{dia}", on_click=marcar_dia, args=(dia,))
        c2.button("Limpar", key=f"limpar_{dia}", on_click=limpar_dia, args=(dia,))

if st.button("Adicionar professor"):
    disponibilidade = [h for h in horarios if st.session_state[h]]
    if nome:
        st.session_state.professores[nome] = {
            "disponibilidade": disponibilidade,
            "dois_tempos": dois_tempos_seguidos,
            "tempos_semana": tempos_semana
        }
        st.success(f"{nome} adicionado")
        st.rerun()

# -------------------------
# SALVAR / CARREGAR
# -------------------------
col1, col2 = st.columns(2)
col1.button("💾 Salvar professores", on_click=salvar_professores)
col2.button("📂 Carregar professores", on_click=carregar_professores)

# -------------------------
# LISTA DE PROFESSORES
# -------------------------
st.subheader("Professores cadastrados")
for prof, info in st.session_state.professores.items():
    col1, col2 = st.columns([4,1])
    with col1:
        horarios_legiveis = [f"{h[:3]} Tempo {h[3:]}" for h in info["disponibilidade"]]
        st.write(f"{prof} → {', '.join(horarios_legiveis)} | Dois tempos: {info['dois_tempos']} | Aulas/semana: {info['tempos_semana']}")
    with col2:
        if st.button("Remover", key=f"remover_{prof}"):
            del st.session_state.professores[prof]
            st.rerun()

# -------------------------
# GERAR GRADE MULTI TURMAS
# -------------------------
if st.button("Gerar grade"):
    professores = st.session_state.professores
    melhor_grade = None
    melhor_pontuacao = -1
    impossiveis = {}

    for tentativa in range(1000):
        grade = {}
        prof_ocupado = {}
        contador_aulas = {prof: 0 for prof in professores}

        for turma in turmas:
            for h in horarios:
                candidatos = []
                for prof, info in professores.items():
                    if contador_aulas[prof] >= info["tempos_semana"]:
                        continue
                    if h in info["disponibilidade"] and (prof, h) not in prof_ocupado:
                        # checar dois tempos consecutivos
                        if info["dois_tempos"]:
                            dia = h[:3]
                            tempo_num = int(h[3:])
                            if tempo_num == num_tempos:
                                continue
                            prox_h = f"{dia}{tempo_num+1:02}"
                            if prox_h not in info["disponibilidade"] or (prof, prox_h) in prof_ocupado:
                                continue
                        candidatos.append(prof)

                if not candidatos:
                    continue

                random.shuffle(candidatos)
                candidatos.sort(key=lambda p: contador_aulas[p])
                escolhido = candidatos[0]
                grade[(turma, h)] = escolhido
                prof_ocupado[(escolhido, h)] = True
                contador_aulas[escolhido] += 1

                if professores[escolhido]["dois_tempos"]:
                    dia = h[:3]
                    tempo_num = int(h[3:])
                    prox_h = f"{dia}{tempo_num+1:02}"
                    grade[(turma, prox_h)] = escolhido
                    prof_ocupado[(escolhido, prox_h)] = True
                    contador_aulas[escolhido] += 1

        # verificar professores que não completaram os tempos/semana
        for prof, info in professores.items():
            if contador_aulas[prof] < info["tempos_semana"]:
                impossiveis[prof] = info["tempos_semana"] - contador_aulas[prof]

        pontuacao = len(grade)
        if pontuacao > melhor_pontuacao:
            melhor_pontuacao = pontuacao
            melhor_grade = grade

    if melhor_grade is None:
        st.warning("Não foi possível gerar uma grade completa com os professores disponíveis.")
    else:
        grade = melhor_grade
        # preencher horários vazios
        for turma in turmas:
            for h in horarios:
                if (turma, h) not in grade:
                    grade[(turma, h)] = ""

        # -------------------------
        # MOSTRAR TABELAS
        # -------------------------
        tabelas = {}
        for turma in turmas:
            tabela = []
            for tempo in tempos:
                linha = []
                for dia in dias:
                    chave = f"{dia}{tempo}"
                    linha.append(grade.get((turma, chave), ""))
                tabela.append(linha)
            df = pd.DataFrame(tabela, columns=dias, index=[f"Tempo {t}" for t in tempos])
            tabelas[turma] = df
            st.subheader(turma)
            st.table(df)

        # -------------------------
        # EXPORTAR EXCEL
        # -------------------------
        arquivo = "grade_horarios.xlsx"
        with pd.ExcelWriter(arquivo, engine='openpyxl') as writer:
            for turma, df in tabelas.items():
                df.to_excel(writer, sheet_name=turma)

        wb = load_workbook(arquivo)
        for ws in wb.worksheets:
            for row in ws.iter_rows():
                for cell in row:
                    cell.alignment = Alignment(horizontal="center", vertical="center")
            for cell in ws[1]:
                cell.font = Font(bold=True)
        wb.save(arquivo)

        with open(arquivo, "rb") as f:
            st.download_button(
                "📥 Baixar Excel",
                f,
                file_name="grade_horarios.xlsx"
            )

    # -------------------------
    # AVISO DE PROFESSORES IMPOSSÍVEIS
    # -------------------------
    if impossiveis:
        st.error("Os seguintes professores não puderam ser totalmente encaixados na grade. Ajuste a disponibilidade ou os tempos/semana:")
        for prof, faltando in impossiveis.items():
            st.write(f"{prof} → faltam {faltando} tempos")
