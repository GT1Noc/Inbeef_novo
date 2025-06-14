from fpdf import FPDF
import io
from datetime import datetime
from config_pasto_v2 import LOGO_PATH

class PDFReport(FPDF):
    def header(self):
        if LOGO_PATH.exists():
            self.image(str(LOGO_PATH), x=10, y=8, w=25)
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "Relatório Comparativo Inbra", ln=1, align="C")
        self.set_font("Arial", "B", 14)
        self.cell(0, 8, "Inbeef", ln=1, align="C")
        self.set_font("Arial", "", 10)
        subtitle = (
            f"Projeção para {self.dias} dias | "
            f"Data da análise: {datetime.now().strftime('%d/%m/%Y')}"
        )
        self.cell(0, 6, subtitle, ln=1, align="C")
        self.ln(4)


def formatar_reais(valor, casas_decimais=2):
    try:
        v = float(valor)
        if casas_decimais == 0:
            valor_int = int(round(v))
            s = f"{valor_int:,}".replace(",", "X").replace(".", ",").replace("X", ".")
            return s
        else:
            s = f"{v:,.{casas_decimais}f}".replace(",", "X").replace(".", ",").replace("X", ".")
            return s
    except:
        return "0" if casas_decimais == 0 else "0,00"


def render_pdf(dados):
    pdf = PDFReport()
    pdf.dias = dados.get('dias', 0)
    pdf.add_page()

    # Parâmetros de Entrada
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Parâmetros de Entrada", ln=1)
    y0 = pdf.get_y()
    pdf.set_draw_color(200, 200, 200)
    # Caixa de entrada
    pdf.rect(10, y0, 190, 60)
    pdf.ln(2)

    # Layout linha a linha: label: valor
    input_labels = [
        "Número de dias",
        "Valor do kg do peso vivo",
        "Nº de animais",
        "Custo diário padrão (R$/animal)",
        "Custo diário Inbeef (R$/animal)",
        "GMD Padrão (g/dia)",
        "Expectativa GMD adicional (g/dia)"
    ]
    input_vals = [
        str(dados.get('dias', 0)),
        f"R$ {formatar_reais(dados.get('valor_kg_recria', 0))}",
        str(dados.get('num_animais', 0)),
        f"R$ {formatar_reais(dados.get('custo_padrao_diario', 0))}",
        f"R$ {formatar_reais(dados.get('custo_inbeef_diario', 0))}",
        f"{dados.get('gmd_padrao', 0):.2f} g/dia",
        f"{dados.get('expectativa_gmd', 0):.2f} g/dia"
    ]
    pdf.set_font("Courier", "", 10)
    line_h = 6
    col_width = pdf.w - pdf.l_margin - pdf.r_margin
    val_width = 30
    y_start = pdf.get_y()
    for i, (lab, val) in enumerate(zip(input_labels, input_vals)):
        pdf.set_xy(pdf.l_margin, y_start + i * line_h)
        pdf.set_font("Courier", "B", 10)
        pdf.cell(col_width - val_width, line_h, f"{lab}:", border=0, ln=0)
        pdf.set_font("Courier", "", 10)
        pdf.set_x(pdf.l_margin + col_width - val_width)
        pdf.cell(val_width, line_h, val, border=0, align="R")
    pdf.ln(4)

    # Bloco de Resultados
    pdf.ln(30)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Resultados", ln=1)
    y_frame = pdf.get_y()
    pdf.set_draw_color(200, 200, 200)
    frame_height = 6 * 6 + 4
    pdf.rect(10, y_frame, 190, frame_height)
    pdf.ln(2)

    col1_labels = [
        "Custo diário padrão",
        "Custo total da suplem. padrão",
        "Quantidade de @ sistema padrão",
        "Valor das @ produz. padrão",
        "Diferença de invest. animal/dia",
        "Ganho líquido por animal"
    ]
    col1_vals = [
        f"R$ {formatar_reais(dados.get('custo_padrao_diario', 0))}",
        f"R$ {formatar_reais(dados.get('custo_total_padrao', 0), 0)}",
        f"{dados.get('qtde_arrobas_padrao', 0):.2f} @",
        f"R$ {formatar_reais(dados.get('valor_arrobas_padrao', 0), 0)}",
        f"R$ {formatar_reais(dados.get('diferenca_investimento', 0))}",
        f"R$ {formatar_reais(dados.get('ganho_liq_por_animal', 0))}"
    ]
    col2_labels = [
        "Custo diário Inbeef",
        "Custo total da suplem. Inbeef",
        "Quantidade de @ sistema Inbeef",
        "Valor das @ produz. Inbeef",
        "Ponto de equilíbrio",
        "Retorno sobre Invest."
    ]
    col2_vals = [
        f"R$ {formatar_reais(dados.get('custo_inbeef_diario', 0))}",
        f"R$ {formatar_reais(dados.get('custo_total_inbeef', 0), 0)}",
        f"{dados.get('qtde_arrobas_inbeef', 0):.2f} @",
        f"R$ {formatar_reais(dados.get('valor_arrobas_inbeef', 0), 0)}",
        f"{dados.get('ponto_equilibrio', 0):.2f} g/dia",
        f"{dados.get('retorno_inbeef', 0):.2f} x"
    ]

    line_h = 6
    col_width = (pdf.w - pdf.l_margin - pdf.r_margin) / 2
    val_width = 30
    y_start = pdf.get_y()

    # Coluna 1
    for i, (lab, val) in enumerate(zip(col1_labels, col1_vals)):
        pdf.set_xy(pdf.l_margin, y_start + i * line_h)
        pdf.set_font("Courier", "B", 10)
        pdf.cell(col_width - val_width, line_h, f"{lab}:", border=0, ln=0)
        pdf.set_font("Courier", "", 10)
        pdf.set_x(pdf.l_margin + col_width - val_width)
        pdf.cell(val_width, line_h, val, border=0, align="R")

    # Coluna 2
    for i, (lab, val) in enumerate(zip(col2_labels, col2_vals)):
        pdf.set_xy(pdf.l_margin + col_width, y_start + i * line_h)
        pdf.set_font("Courier", "B", 10)
        pdf.cell(col_width - val_width, line_h, f"{lab}:", border=0, ln=0)
        pdf.set_font("Courier", "", 10)
        pdf.set_x(pdf.l_margin + col_width + col_width - val_width)
        pdf.cell(val_width, line_h, val, border=0, align="R")

    pdf.ln(frame_height + 4)

    # Interpretação e Disclaimer
    pdf.ln(30)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Interpretação:", ln=1)
    pdf.set_font("Arial", "", 10)
    texto_interp = (
        f"Em {dados.get('dias', 0)} dias, o investimento extra em Inbeef de R$ "
        f"{formatar_reais(dados.get('diferenca_investimento', 0))} pode gerar "
        f"{dados.get('retorno_inbeef', 0):.2f} vezes o valor adicional investido, "
        f"equivalente a um ganho líquido de R$ {formatar_reais(dados.get('ganho_liq_por_animal', 0))} por animal."
    )
    pdf.multi_cell(0, 6, texto_interp)
    pdf.ln(4)
    pdf.set_font("Arial", "I", 8)
    disclaimer = (
        "Este relatório apresenta apenas uma projeção baseada nos parâmetros informados. "
        "Resultados reais podem variar devido a fatores externos não controláveis "
        "(condições climáticas, qualidade da pastagem, saúde dos animais etc.)."
    )
    pdf.multi_cell(0, 5, disclaimer)

    buffer = io.BytesIO()
    output = pdf.output(dest='S')
    if isinstance(output, str):
        buffer.write(output.encode('latin-1', 'replace'))
    else:
        buffer.write(output)
    return buffer.getvalue()

