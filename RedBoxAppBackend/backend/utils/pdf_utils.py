import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from backend.models import Usuario_planes

def generar_pdf_historial_pagos(pagos, usuario_actual, fecha_inicio, fecha_fin):
    """
    Genera un PDF con el historial de pagos filtrado por fechas.
    
    Args:
        pagos: QuerySet de Pagos
        usuario_actual: Objeto Usuarios (para mostrar quién solicitó)
        fecha_inicio: String fecha inicio
        fecha_fin: String fecha fin
    
    Returns:
        BytesIO: Archivo PDF en memoria
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    styles = getSampleStyleSheet()
    story = []
    
    # Estilos
    titulo_style = ParagraphStyle(
        'Titulo',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#FF3B30'),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    subtitulo_style = ParagraphStyle(
        'Subtitulo',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    # Título
    story.append(Paragraph("Historial de Pagos", titulo_style))
    story.append(Paragraph(
        f"Periodo: {fecha_inicio} al {fecha_fin}",
        subtitulo_style
    ))
    story.append(Spacer(1, 10))
    
    # Tabla de pagos
    data = [
        ['#', 'Usuario', 'Plan', 'Monto', 'Moneda', 'Método', 'Fecha', 'Estado']
    ]
    
    for idx, pago in enumerate(pagos, 1):
        # Obtener usuario del pago
        plan = pago.id_usuario_plan
        usuario_pago = Usuario_planes.objects.filter(id_plan=plan).first()
        usuario = usuario_pago.id_usuario if usuario_pago else None
        nombre_usuario = f"{usuario.pnombre_usuario} {usuario.papellido_usuario}" if usuario else 'Desconocido'
        
        data.append([
            str(idx),
            nombre_usuario,
            plan.nombre_plan if plan else 'N/A',
            str(pago.monto),
            pago.moneda,
            pago.metodo_pago,
            pago.fecha_pago.strftime('%d/%m/%Y'),
            pago.estado_pago,
        ])
    
    # Configurar tabla
    table = Table(data, colWidths=[0.5*inch, 1.5*inch, 0.8*inch, 0.8*inch, 0.8*inch, 1*inch, 1*inch, 0.8*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF3B30')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(table)
    
    # Resumen de totales
    story.append(Spacer(1, 20))
    
    total_pagos = len(pagos)
    total_monto = sum(float(p.monto) for p in pagos)
    
    resumen_style = ParagraphStyle(
        'Resumen',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_RIGHT,
        spaceAfter=10
    )
    
    story.append(Paragraph(f"Total de pagos: {total_pagos}", resumen_style))
    story.append(Paragraph(f"Monto total: {total_monto:.2f} USD", resumen_style))
    story.append(Spacer(1, 20))
    
    # Pie de página
    pie_style = ParagraphStyle(
        'Pie',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.grey
    )
    
    usuario_nombre = f"{usuario_actual.pnombre_usuario} {usuario_actual.papellido_usuario}"
    story.append(Paragraph(
        f"Reporte generado por: {usuario_nombre} ({usuario_actual.email_usuario})",
        pie_style
    ))
    story.append(Paragraph(
        f"Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        pie_style
    ))
    story.append(Paragraph(
        "© RedBox App - Todos los derechos reservados",
        pie_style
    ))
    
    doc.build(story)
    buffer.seek(0)
    return buffer