# 🏫 Gerador de Grade Escolar

Aplicação em Python que gera automaticamente horários escolares com base na disponibilidade dos professores e restrições de sequência de aulas.

---

## 🎯 Objetivo

Organizar a grade escolar de forma automática, eficiente e flexível, permitindo:  

- Otimização de horários de professores e turmas  
- Redução de conflitos de aulas  
- Exportação de resultados para análise ou uso diário  

---

## 🛠️ Tecnologias

- Python  
- Streamlit  
- Pandas  
- JSON (armazenamento de dados de professores e turmas)  
- Algoritmo heurístico de otimização  

---

## 📚 Funcionalidades

- Cadastro de professores e disciplinas  
- Definição de disponibilidade por horário e dia  
- Geração automática da grade escolar  
- Respeito a restrições de sequência de aulas  
- Visualização da grade por professor e turma  
- Exportação para CSV ou Excel  
- Ajustes manuais via interface interativa  

---

## ▶️ Como executar

1. Clone o repositório:

```bash
git clone https://github.com/GabrielLimaUERJ/Gerador-Grade-Escolar.git
cd Gerador-Grade-Escolar
pip install -r requirements.txt
streamlit run app.py
