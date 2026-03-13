# cd "Directory"
# streamlit run app.py

import streamlit as st
import pandas as pd
import random
import json
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font

st.set_page_config(page_title="Gerador de Grade Escolar", layout="wide")

st.title("📚 Gerador de Grade Escolar")

# -------------------------
# DIAS E TEMPOS
# -------------------------

dias = ["Seg", "Ter", "Qua", "Qui", "Sex"]
tempos = ["01", "02", "03", "04", "05", "06"]

horarios = [f"{d}{t}" for d in dias for t in tempos]

# -------------------------
# NÚMERO DE TURMAS
# -------------------------

num_turmas = st.number_input("Número de turmas", 1, 10, 3)

turmas = [f"Turma {i}" for i in range(1, num_turmas+1)]

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
# FUNÇÕES
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
            st.session_state.professores = json.load(f)

        st.success("Professores carregados")

    except:

        st.warning("Nenhum arquivo encontrado")


# -------------------------
# ADICIONAR PROFESSOR
# -------------------------

st.header("Adicionar professor")

nome = st.text_input("Nome do professor")

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

            st.checkbox(
                f"Tempo {tempo}",
                key=chave
            )

        c1, c2 = st.columns(2)

        c1.button(
            "Marcar todos",
            key=f"marcar_{dia}",
            on_click=marcar_dia,
            args=(dia,)
        )

        c2.button(
            "Limpar",
            key=f"limpar_{dia}",
            on_click=limpar_dia,
            args=(dia,)
        )

# adicionar professor

if st.button("Adicionar professor"):

    disponibilidade = []

    for h in horarios:
        if st.session_state[h]:
            disponibilidade.append(h)

    if nome:

        st.session_state.professores[nome] = disponibilidade

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

for prof, disp in st.session_state.professores.items():

    col1, col2 = st.columns([4,1])

    with col1:

        horarios_legiveis = []

        for h in disp:

            dia = h[:3]
            tempo = h[3:]

            horarios_legiveis.append(f"{dia} Tempo {tempo}")

        st.write(prof, "→", ", ".join(horarios_legiveis))

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

    for tentativa in range(500):

        grade = {}

        prof_ocupado = {}

        contador_aulas = {prof: 0 for prof in professores}

        for turma in turmas:

            for h in horarios:

                candidatos = []

                for prof, disponibilidade in professores.items():

                    if h in disponibilidade:

                        if (prof, h) not in prof_ocupado:

                            candidatos.append(prof)

                if not candidatos:
                    continue

                random.shuffle(candidatos)

                candidatos.sort(key=lambda p: contador_aulas[p])

                escolhido = candidatos[0]

                grade[(turma, h)] = escolhido

                prof_ocupado[(escolhido, h)] = True

                contador_aulas[escolhido] += 1

        pontuacao = len(grade)

        if pontuacao > melhor_pontuacao:

            melhor_pontuacao = pontuacao
            melhor_grade = grade

    grade = melhor_grade

# -------------------------
# MOSTRAR TABELAS
# -------------------------

    tabelas = {}

    for turma in turmas:

        tabela = []

        for tempo in tempos:

            linha = []

            for dia in dias:

                chave = dia + tempo

                if (turma, chave) in grade:

                    linha.append(grade[(turma, chave)])

                else:

                    linha.append("")

               

            tabela.append(linha)

        df = pd.DataFrame(
            tabela,
            columns=dias,
            index=[f"Tempo {t}" for t in tempos]
        )

        tabelas[turma] = df

        st.subheader(turma)

        st.table(df)

# -------------------------
# EXPORTAR EXCEL
# -------------------------

    arquivo = "grade_horarios.xlsx"

    with pd.ExcelWriter(arquivo) as writer:

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