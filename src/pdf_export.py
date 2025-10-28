"""
Módulo de exportação PDF - Ilheus North Hotel (INH)
Geração de comprovantes de check-out em PDF profissional
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from datetime import datetime
from pathlib import Path
import io
from PIL import Image

from . import database as db


def gerar_pdf_checkout(quarto_numero, categoria_nome, resumo, consumos_por_hospede,
                       totais_por_hospede, subtotal, taxa_servico, total_final,
                       data_checkin, cobrar_taxa=True):
    """
    Gera PDF profissional de check-out com todas as informações de consumo

    Args:
        quarto_numero: Número da UH
        categoria_nome: Nome da categoria (Residence, Hotel, etc)
        resumo: Dicionário com resumo de consumo do database
        consumos_por_hospede: Dict com lista de consumos por hóspede
        totais_por_hospede: Dict com totais por hóspede
        subtotal: Valor subtotal sem taxa
        taxa_servico: Valor da taxa de serviço
        total_final: Valor total final
        data_checkin: Data/hora do check-in (string ou datetime)
        cobrar_taxa: Se taxa de serviço foi aplicada

    Returns:
        bytes: Conteúdo do PDF gerado
    """
    # Criar buffer de memória para o PDF
    buffer = io.BytesIO()

    # Criar canvas
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Cores da identidade visual
    COR_DOURADO = (0.82, 0.69, 0.18)  # #d2b02d
    COR_AZUL_ESCURO = (0.09, 0.18, 0.30)  # #182D4C

    # Margem
    margin = 2*cm
    y_position = height - margin

    # ===== CABEÇALHO =====
    # Logo
    logo_path = Path("assets/logo.png")
    if logo_path.exists():
        logo = ImageReader(str(logo_path))
        pdf.drawImage(logo, margin, y_position - 3*cm, width=4*cm, height=3*cm, preserveAspectRatio=True)

    # Título
    pdf.setFont("Helvetica", 18)
    pdf.setFillColorRGB(*COR_AZUL_ESCURO)
    pdf.drawString(margin + 5*cm, y_position - 1*cm, "Extrato para conferência")

    # Subtítulo
    pdf.setFont("Helvetica", 12)
    pdf.setFillColorRGB(0, 0, 0)
    pdf.drawString(margin + 5*cm, y_position - 1.6*cm, f"UH: {quarto_numero} • Categoria: {categoria_nome}")

    # Datas de check-in e check-out
    pdf.setFont("Helvetica", 10)

    # Formatar data de check-in
    if isinstance(data_checkin, str):
        try:
            data_checkin_obj = datetime.strptime(data_checkin, "%Y-%m-%d %H:%M:%S")
            data_checkin_br = data_checkin_obj.strftime("%d/%m/%Y às %H:%M")
        except:
            data_checkin_br = data_checkin
    else:
        data_checkin_br = data_checkin.strftime("%d/%m/%Y às %H:%M") if data_checkin else "N/A"

    # Data de check-out (agora)
    data_checkout_br = datetime.now().strftime("%d/%m/%Y às %H:%M")

    pdf.drawString(margin + 5*cm, y_position - 2.1*cm, f"Check-in: {data_checkin_br}")
    pdf.drawString(margin + 5*cm, y_position - 2.5*cm, f"Check-out: {data_checkout_br}")

    y_position -= 3.8*cm

    # Linha separadora
    pdf.setStrokeColorRGB(*COR_DOURADO)
    pdf.setLineWidth(2)
    pdf.line(margin, y_position, width - margin, y_position)
    y_position -= 0.6*cm

    # ===== DETALHAMENTO DE CONSUMOS =====
    pdf.setFont("Helvetica-Bold", 14)
    pdf.setFillColorRGB(0, 0, 0)
    pdf.drawString(margin, y_position, "Detalhamento de Consumo")
    y_position -= 0.8*cm

    # Largura das colunas
    col_info_width = 10*cm  # Coluna esquerda: informações
    col_assinatura_x = margin + col_info_width + 0.5*cm  # Coluna direita: assinatura

    # Iterar por hóspede
    for hospede_nome, consumos in consumos_por_hospede.items():
        # Verificar se precisa de nova página
        if y_position < 8*cm:
            pdf.showPage()
            y_position = height - margin

        # Nome do hóspede
        pdf.setFont("Helvetica-Bold", 12)
        pdf.setFillColorRGB(*COR_AZUL_ESCURO)
        pdf.drawString(margin, y_position, hospede_nome)
        y_position -= 0.6*cm

        # Consumos do hóspede
        for idx, consumo in enumerate(consumos, 1):
            # Verificar espaço para pedido completo (layout em colunas precisa de ~2.5cm)
            if y_position < 8*cm:
                pdf.showPage()
                y_position = height - margin

            # Salvar posição inicial do pedido para alinhar assinatura
            pedido_y_start = y_position

            # ===== COLUNA ESQUERDA: INFORMAÇÕES =====

            # Data/hora
            try:
                data_obj = datetime.strptime(consumo['data_hora'], "%Y-%m-%d %H:%M:%S")
                data_br = data_obj.strftime("%d/%m/%Y às %H:%M:%S")
            except:
                data_br = consumo['data_hora']

            # PEDIDO #N com data
            pdf.setFont("Helvetica-Bold", 10)
            pdf.setFillColorRGB(*COR_DOURADO)
            pdf.drawString(margin + 0.3*cm, y_position, f"PEDIDO #{idx}: autorizado em: {data_br}")
            y_position -= 0.5*cm

            # Detalhes do pedido
            pdf.setFont("Helvetica", 9)
            pdf.setFillColorRGB(0, 0, 0)

            # Produto
            pdf.drawString(margin + 0.5*cm, y_position, f"{consumo['produto']}")
            y_position -= 0.4*cm

            # Valor
            pdf.drawString(margin + 0.5*cm, y_position,
                          f"Quantidade: {consumo['quantidade']} x R$ {consumo['valor_unitario']:.2f} = R$ {consumo['valor_total']:.2f}")
            y_position -= 0.4*cm

            # ===== COLUNA DIREITA: ASSINATURA =====

            # Assinatura (se disponível) - alinhada ao topo do pedido
            assinatura_bytes = db.obter_assinatura(consumo['id'])
            if assinatura_bytes:
                try:
                    assinatura_img = Image.open(io.BytesIO(assinatura_bytes))
                    # Salvar temporariamente para ImageReader
                    temp_img = io.BytesIO()
                    assinatura_img.save(temp_img, format='PNG')
                    temp_img.seek(0)

                    img_reader = ImageReader(temp_img)
                    # Desenhar assinatura na coluna direita, alinhada ao topo do pedido
                    # Ajustar para ficar centralizada verticalmente no bloco de informações
                    assinatura_height = 1.8*cm
                    assinatura_y = pedido_y_start - assinatura_height

                    pdf.drawImage(img_reader, col_assinatura_x, assinatura_y,
                                width=5*cm, height=assinatura_height, preserveAspectRatio=True)

                    # Texto "Assinatura" abaixo da imagem
                    pdf.setFont("Helvetica-Oblique", 7)
                    pdf.setFillColorRGB(0.5, 0.5, 0.5)
                    pdf.drawString(col_assinatura_x, assinatura_y - 0.3*cm, "Assinatura do hóspede")
                    pdf.setFillColorRGB(0, 0, 0)
                except:
                    pdf.setFont("Helvetica-Oblique", 8)
                    pdf.drawString(col_assinatura_x, pedido_y_start - 0.5*cm, "Assinatura não disponível")

            # Espaço entre pedidos
            y_position -= 0.5*cm

        # Total do hóspede
        pdf.setFont("Helvetica-Bold", 10)
        pdf.setFillColorRGB(*COR_AZUL_ESCURO)
        total_hospede = totais_por_hospede[hospede_nome]
        pdf.drawString(margin + 0.5*cm, y_position, f"Total de {hospede_nome}: R$ {total_hospede:.2f}")
        y_position -= 0.9*cm

    # ===== RESUMO FINANCEIRO =====
    # Verificar se precisa de nova página
    if y_position < 10*cm:
        pdf.showPage()
        y_position = height - margin

    # Linha separadora antes do resumo
    pdf.setStrokeColorRGB(*COR_DOURADO)
    pdf.setLineWidth(2)
    pdf.line(margin, y_position, width - margin, y_position)
    y_position -= 0.8*cm

    # Título do resumo
    pdf.setFont("Helvetica-Bold", 14)
    pdf.setFillColorRGB(0, 0, 0)
    pdf.drawString(margin, y_position, "RESUMO FINANCEIRO")
    y_position -= 0.8*cm

    # Breakdown por hóspede
    pdf.setFont("Helvetica", 10)
    for hospede_nome, total in totais_por_hospede.items():
        pdf.drawString(margin + 0.5*cm, y_position, hospede_nome)
        pdf.drawRightString(width - margin, y_position, f"R$ {total:.2f}")
        y_position -= 0.5*cm

    y_position -= 0.3*cm

    # Linha
    pdf.setStrokeColorRGB(0.5, 0.5, 0.5)
    pdf.setLineWidth(1)
    pdf.line(margin, y_position, width - margin, y_position)
    y_position -= 0.6*cm

    # Subtotal
    pdf.setFont("Helvetica", 11)
    pdf.drawString(margin + 0.5*cm, y_position, "Subtotal:")
    pdf.drawRightString(width - margin, y_position, f"R$ {subtotal:.2f}")
    y_position -= 0.5*cm

    # Taxa de serviço
    if cobrar_taxa:
        pdf.drawString(margin + 0.5*cm, y_position, "Taxa de Serviço (10%):")
        pdf.drawRightString(width - margin, y_position, f"R$ {taxa_servico:.2f}")
    else:
        pdf.setFillColorRGB(0.5, 0.5, 0.5)
        pdf.drawString(margin + 0.5*cm, y_position, "Taxa de Serviço (10%): NÃO COBRADA")
        pdf.drawRightString(width - margin, y_position, f"R$ 0,00")
        pdf.setFillColorRGB(0, 0, 0)
    y_position -= 0.8*cm

    # Linha antes do total
    pdf.setStrokeColorRGB(*COR_DOURADO)
    pdf.setLineWidth(2)
    pdf.line(margin, y_position, width - margin, y_position)
    y_position -= 0.8*cm

    # TOTAL GERAL
    pdf.setFont("Helvetica-Bold", 16)
    pdf.setFillColorRGB(*COR_DOURADO)
    pdf.drawString(margin + 0.5*cm, y_position, "TOTAL GERAL:")
    pdf.drawRightString(width - margin, y_position, f"R$ {total_final:.2f}")

    # Rodapé
    pdf.setFont("Helvetica-Oblique", 8)
    pdf.setFillColorRGB(0.5, 0.5, 0.5)
    pdf.drawCentredString(width/2, 1.5*cm, "Ilheus North Hotel - Obrigado pela preferência!")
    pdf.drawCentredString(width/2, 1*cm, f"Documento gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}")

    # Salvar PDF
    pdf.save()

    # Retornar bytes
    buffer.seek(0)
    return buffer.getvalue()
