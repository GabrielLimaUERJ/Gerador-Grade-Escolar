import streamlit as st

st.title("Gerador de Grade Escolar")

nome = st.text_input("Nome do professor")

if st.button("Adicionar"):
    st.write("Professor adicionado:", nome)