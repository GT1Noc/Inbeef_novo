import base64
import streamlit as st
from pathlib import Path

# Renomear imports para V2
from calculations_pasto_v2 import (
    calcular_custo_diario,
    calcular_diferenca_investimento,
    calcular_investimento_total,
    calcular_ponto_equilibrio,
    calcular_ganho_liquido_por_animal,
    calcular_custo_total_padrao,
    calcular_retorno_inbeef
)
from pdf_generator_pasto_v2 import render_pdf
from config_pasto_v2 import CSS_PATH, LOGO_PATH

# Função auxiliar para formatar valores monetários no padrão brasileiro
def formatar_reais(valor, casas_decimais=2):
    try:
        valor_float = float(valor)
        if casas_decimais == 0:
            resultado = f"R$ {valor_float:,.0f}"
        else:
            resultado = f"R$ {valor_float:,.{casas_decimais}f}"
        return resultado.replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return "R$ 0,00"

# ----------------------------
# Injeção de CSS e logo
if CSS_PATH.exists():
    css = CSS_PATH.read_text()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

if LOGO_PATH.exists():
    logo = LOGO_PATH.read_bytes()
    b64 = base64.b64encode(logo).decode()
    st.markdown(
        "<div style='text-align:center; margin-bottom:10px;'>"
        f"<img src='data:image/png;base64,{b64}' width='200' />"
        "</div>",
        unsafe_allow_html=True
    )

# Cabeçalho em duas linhas, sem hífen, centrado
st.markdown(
    "<div style='text-align:center;'>"
    "<h1 style='margin:0;'>Simulador Comparativo Inbra</h1>"
    "<h2 style='margin:0;'>Inbeef</h2>"
    "</div>",
    unsafe_allow_html=True
)
# ----------------------------

with st.form("sim_form_pasto_v2"):
    # Entradas com tooltips
    dias = st.number_input(
        label="Período – Número de dias (dias)",
        min_value=1,
        value=30,
        help="Informe a duração do tratamento, em número inteiro de dias."
    )
    valor_kg_recria = st.number_input(
        label="Valor do kg do peso vivo",
        format="%.2f",
        min_value=0.01,
        help="Informe o valor do quilo do peso vivo utilizado para recria."
    )
    num_animais = st.number_input(
        label="Número total de animais – (número)",
        min_value=1,
        step=1,
        help="Total de animais no lote."
    )

    st.markdown("---")
    # Preço e consumo do produto padrão
    col1, col2 = st.columns(2)
    with col1:
        preco_padrao = st.number_input(
            label="Preço do produto padrão (R$/kg)",
            format="%.2f",
            min_value=0.01,
            help="Preço do suplemento padrão por quilo."
        )
    with col2:
        consumo_padrao_g = st.number_input(
            label="Consumo do produto padrão (g/dia)",
            format="%.2f",
            min_value=0.0,
            help="Consumo diário em gramas do suplemento padrão."
        )

    # Preço e consumo do produto com Inbeef
    col3, col4 = st.columns(2)
    with col3:
        preco_inbeef = st.number_input(
            label="Preço do produto com Inbeef (R$/kg)",
            format="%.2f",
            min_value=0.01,
            help="Preço do suplemento com Inbeef por quilo."
        )
    with col4:
        consumo_inbeef_g = st.number_input(
            label="Consumo do produto c/ Inbeef (g/dia)",
            format="%.2f",
            min_value=0.0,
            help="Consumo diário em gramas do suplemento com Inbeef."
        )

    # GMD padrão e Expectativa GMD adicional
    col5, col6 = st.columns(2)
    with col5:
        gmd_padrao = st.number_input(
            label="GMD Padrão (g/dia)",
            format="%.2f",
            min_value=0.0,
            help="Ganho médio diário de peso padrão."
        )
    with col6:
        expectativa_gmd = st.number_input(
            label="Expectativa GMD adicional (g/dia)",
            format="%.2f",
            min_value=0.0,
            help="Ganho médio diário adicional esperado."
        )

    submitted = st.form_submit_button("Calcular")

if submitted:
    # Cálculo dos parâmetros básicos
    custo_padrao_diario = calcular_custo_diario(consumo_padrao_g, preco_padrao)
    custo_inbeef_diario = calcular_custo_diario(consumo_inbeef_g, preco_inbeef)
    diferenca_investimento = calcular_diferenca_investimento(
        custo_inbeef_diario, custo_padrao_diario
    )
    ponto_equilibrio = calcular_ponto_equilibrio(
        diferenca_investimento, valor_kg_recria
    )
    ganho_liq_por_animal = calcular_ganho_liquido_por_animal(
        expectativa_gmd, ponto_equilibrio, valor_kg_recria, dias
    )
    custo_total_padrao = calcular_custo_total_padrao(
        num_animais, custo_padrao_diario, dias
    )
    custo_total_inbeef = calcular_investimento_total(
        num_animais, custo_inbeef_diario, dias
    )
    # Cálculo de arrobas produzidas
    qtde_arrobas_padrao = ((gmd_padrao / 1000) * dias) / 30
    valor_arrobas_padrao = qtde_arrobas_padrao * (valor_kg_recria * 30) * num_animais
    qtde_arrobas_inbeef = (((gmd_padrao + expectativa_gmd) / 1000) * dias) / 30
    valor_arrobas_inbeef = qtde_arrobas_inbeef * (valor_kg_recria * 30) * num_animais
    # Retorno sobre investimento
    retorno_inbeef = calcular_retorno_inbeef(
        expectativa_gmd, valor_kg_recria, diferenca_investimento, dias
    )

    # Monta dicionário de resultados
    r = {
        'dias': dias,
        'valor_kg_recria': valor_kg_recria,
        'num_animais': num_animais,
        'preco_padrao': preco_padrao,
        'consumo_padrao_g': consumo_padrao_g,
        'preco_inbeef': preco_inbeef,
        'consumo_inbeef_g': consumo_inbeef_g,
        'gmd_padrao': gmd_padrao,
        'expectativa_gmd': expectativa_gmd,
        'custo_padrao_diario': custo_padrao_diario,
        'custo_inbeef_diario': custo_inbeef_diario,
        'diferenca_investimento': diferenca_investimento,
        'ponto_equilibrio': ponto_equilibrio,
        'ganho_liq_por_animal': ganho_liq_por_animal,
        'custo_total_padrao': custo_total_padrao,
        'custo_total_inbeef': custo_total_inbeef,
        'qtde_arrobas_padrao': qtde_arrobas_padrao,
        'valor_arrobas_padrao': valor_arrobas_padrao,
        'qtde_arrobas_inbeef': qtde_arrobas_inbeef,
        'valor_arrobas_inbeef': valor_arrobas_inbeef,
        'retorno_inbeef': retorno_inbeef
    }

    # Apresenta resultados
    st.subheader("Resultados da Simulação")
    col_out1, col_out2 = st.columns(2)
    with col_out1:
        st.metric("Custo diário padrão (R$)", formatar_reais(custo_padrao_diario))
        st.metric("Custo total da suplementação padrão (R$)", formatar_reais(custo_total_padrao))
        st.metric("Quantidade de @ produzidas sistema padrão (Arroba)", f"{qtde_arrobas_padrao:.2f}")
        st.metric("Valor das @ produzidas padrão (R$)", formatar_reais(valor_arrobas_padrao))
        st.metric("Diferença de investimento animal/dia (R$)", formatar_reais(diferenca_investimento))
        st.metric("Ganho líquido por animal (R$)", formatar_reais(ganho_liq_por_animal))
    with col_out2:
        st.metric("Custo diário Inbeef (R$)", formatar_reais(custo_inbeef_diario))
        st.metric("Custo total da suplementação Inbeef (R$)", formatar_reais(custo_total_inbeef))
        st.metric("Quantidade de @ produzidas sistema Inbeef (Arroba)", f"{qtde_arrobas_inbeef:.2f}")
        st.metric("Valor das @ produzidas Inbeef (R$)", formatar_reais(valor_arrobas_inbeef))
        st.metric("Ponto de equilíbrio (g/dia)", f"{ponto_equilibrio:.2f}")
        st.metric("Retorno sobre Investimento", f"{retorno_inbeef:.2f}")

    # Gera e oferece download do PDF
    pdf = render_pdf(r)
    st.download_button(
        "⬇️ Baixar Relatório (PDF)",
        data=pdf,
        file_name=f"sim_inbra_pasto_{dias}d.pdf",
        mime="application/pdf"
    )
