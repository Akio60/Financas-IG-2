from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import datetime

def generate_pdf_report(row_data, output_filename="relatorio_solicitacao.pdf"):
    """
    Gera um PDF com dados da solicitação. #7
    row_data: dict ou pandas Series com campos relevantes
    output_filename: nome do arquivo de saída
    """
    c = canvas.Canvas(output_filename, pagesize=A4)

    # Cabeçalho
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2*cm, 28*cm, "Relatório de Solicitação")

    c.setFont("Helvetica", 10)
    now_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    c.drawString(2*cm, 27*cm, f"Gerado em: {now_str}")

    # Conteúdo
    y = 25*cm
    c.setFont("Helvetica", 11)

    for col_name in row_data.index:
        valor = str(row_data[col_name])
        text_line = f"{col_name}: {valor}"
        c.drawString(2*cm, y, text_line)
        y -= 0.8*cm
        if y < 2*cm:
            c.showPage()
            y = 27*cm

    c.showPage()
    c.save()
