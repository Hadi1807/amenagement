from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from io import BytesIO
from .models import Facture
from core.models import Commande

@login_required
def generer_facture_pdf(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id)
    
    # Créer ou récupérer la facture
    facture, created = Facture.objects.get_or_create(
        commande=commande,
        defaults={'montant_ttc': commande.total}
    )
    
    # Créer le PDF en mémoire
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                          rightMargin=2*cm, leftMargin=2*cm,
                          topMargin=2*cm, bottomMargin=2*cm)
    
    styles = getSampleStyleSheet()
    elements = []
    
    # Titre
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1  # Centre
    )
    elements.append(Paragraph("FACTURE", title_style))
    elements.append(Spacer(1, 20))
    
    # Infos facture
    elements.append(Paragraph(f"<b>Numéro:</b> {facture.numero}", styles['Normal']))
    elements.append(Paragraph(f"<b>Date:</b> {facture.date_emission.strftime('%d/%m/%Y')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Infos client
    elements.append(Paragraph(f"<b>Client:</b> {commande.client.nom}", styles['Normal']))
    elements.append(Paragraph(f"<b>Email:</b> {commande.client.email}", styles['Normal']))
    elements.append(Paragraph(f"<b>Téléphone:</b> {commande.client.telephone}", styles['Normal']))
    elements.append(Paragraph(f"<b>Adresse:</b> {commande.client.adresse}", styles['Normal']))
    elements.append(Spacer(1, 30))
    
    # Tableau des produits
    data = [['Produit', 'Quantité', 'Prix Unitaire', 'Total']]
    
    for ligne in commande.lignes.all():
        data.append([
            ligne.meuble.nom,
            str(ligne.quantite),
            f"{ligne.prix_unitaire} €",
            f"{ligne.sous_total()} €"
        ])
    
    # Ajouter total
    data.append(['', '', 'TOTAL TTC:', f"{commande.total} €"])
    
    table = Table(data, colWidths=[8*cm, 3*cm, 3*cm, 3*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a4a4a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (-2, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (-2, -1), (-1, -1), colors.lightgrey),
    ]))
    
    elements.append(table)
    
    # Construire PDF
    doc.build(elements)
    
    # Récupérer le PDF
    pdf = buffer.getvalue()
    buffer.close()
    
    # Sauvegarder sur disque si nécessaire
    if not facture.pdf:
        from django.core.files.base import ContentFile
        facture.pdf.save(f'{facture.numero}.pdf', ContentFile(pdf))
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{facture.numero}.pdf"'
    response.write(pdf)
    return response