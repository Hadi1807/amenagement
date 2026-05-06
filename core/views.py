import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from .models import Client, Meuble, Commande, LigneCommande

# Vues pages (rendu HTML)
@login_required
def clients_page(request):
    return render(request, 'core/clients.html')

@login_required
def meubles_page(request):
    return render(request, 'core/meubles.html')

@login_required
def commandes_page(request):
    return render(request, 'core/commandes.html')

# ==================== API CLIENTS ====================
@login_required
@csrf_exempt
def api_clients(request):
    if request.method == 'GET':
        try:
            clients = Client.objects.all().values('id', 'nom', 'email', 'telephone', 'adresse')
            return JsonResponse(list(clients), safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            client = Client.objects.create(
                nom=data['nom'],
                email=data['email'],
                telephone=data.get('telephone', ''),
                adresse=data.get('adresse', '')
            )
            return JsonResponse({
                'success': True, 
                'id': client.id,
                'nom': client.nom,
                'email': client.email,
                'telephone': client.telephone,
                'adresse': client.adresse
            })
        except Exception as e:
            print(f"Erreur création client: {e}")
            return JsonResponse({'error': str(e)}, status=400)
    
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            client = Client.objects.get(id=data['id'])
            client.nom = data.get('nom', client.nom)
            client.email = data.get('email', client.email)
            client.telephone = data.get('telephone', client.telephone)
            client.adresse = data.get('adresse', client.adresse)
            client.save()
            return JsonResponse({
                'success': True,
                'id': client.id,
                'nom': client.nom,
                'email': client.email,
                'telephone': client.telephone,
                'adresse': client.adresse
            })
        except Exception as e:
            print(f"Erreur modification client: {e}")
            return JsonResponse({'error': str(e)}, status=400)
    
    elif request.method == 'DELETE':
        try:
            data = json.loads(request.body)
            client_id = data.get('id')
            Client.objects.get(id=client_id).delete()
            return JsonResponse({'success': True, 'id': client_id})
        except Exception as e:
            print(f"Erreur suppression client: {e}")
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)


# ==================== API MEUBLES ====================
@login_required
@csrf_exempt
def api_meubles(request):
    if request.method == 'GET':
        try:
            meubles = Meuble.objects.all()
            data = []
            for m in meubles:
                data.append({
                    'id': m.id,
                    'nom': m.nom,
                    'categorie': m.categorie,
                    'categorie_display': m.get_categorie_display(),
                    'prix': str(m.prix),
                    'stock': m.stock,
                    'description': m.description,
                    'image': m.image.url if m.image else None
                })
            return JsonResponse(data, safe=False)
        except Exception as e:
            print(f"Erreur chargement meubles: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            meuble = Meuble.objects.create(
                nom=data['nom'],
                categorie=data['categorie'],
                prix=float(data['prix']),
                stock=int(data.get('stock', 0)),
                description=data.get('description', '')
            )
            return JsonResponse({
                'success': True, 
                'id': meuble.id,
                'nom': meuble.nom,
                'categorie': meuble.categorie,
                'prix': str(meuble.prix),
                'stock': meuble.stock
            })
        except Exception as e:
            print(f"Erreur création meuble: {e}")
            return JsonResponse({'error': str(e)}, status=400)
    
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            meuble = Meuble.objects.get(id=data['id'])
            meuble.nom = data.get('nom', meuble.nom)
            meuble.categorie = data.get('categorie', meuble.categorie)
            meuble.prix = float(data.get('prix', meuble.prix))
            meuble.stock = int(data.get('stock', meuble.stock))
            meuble.description = data.get('description', meuble.description)
            meuble.save()
            return JsonResponse({
                'success': True,
                'id': meuble.id,
                'nom': meuble.nom,
                'categorie': meuble.categorie,
                'categorie_display': meuble.get_categorie_display(),
                'prix': str(meuble.prix),
                'stock': meuble.stock
            })
        except Exception as e:
            print(f"Erreur modification meuble: {e}")
            return JsonResponse({'error': str(e)}, status=400)
    
    elif request.method == 'DELETE':
        try:
            data = json.loads(request.body)
            meuble_id = data.get('id')
            Meuble.objects.get(id=meuble_id).delete()
            return JsonResponse({'success': True, 'id': meuble_id})
        except Exception as e:
            print(f"Erreur suppression meuble: {e}")
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

# ==================== API COMMANDES ====================
@login_required
@csrf_exempt
def api_commandes(request):

    if request.method == 'GET':
        try:
            commandes = Commande.objects.all().select_related('client').order_by('-date_creation')
            data = []
            for c in commandes:
                data.append({
                    'id': c.id,
                    'client': c.client.nom if c.client else 'N/A',
                    'date': c.date_creation.strftime('%d/%m/%Y %H:%M') if c.date_creation else '',
                    'statut': c.statut,
                    'statut_display': c.get_statut_display(),
                    'total': str(c.total)
                })
            return JsonResponse(data, safe=False)
        except Exception as e:
            print(f"ERREUR API COMMANDES GET: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    # POST : Créer une commande (AJAX - NE DOIT PAS REDIRIGER)
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            client_id = data.get('client_id')
            lignes_data = data.get('lignes', [])
            
            if not client_id:
                return JsonResponse({'error': 'client_id manquant'}, status=400)
            
            client = Client.objects.get(id=client_id)
            
            # Créer la commande
            commande = Commande.objects.create(
                client=client,
                vendeur=request.user,
                statut='en_attente',
                total=0
            )
            
            # Créer les lignes de commande
            for ligne in lignes_data:
                meuble = Meuble.objects.get(id=ligne['meuble_id'])
                LigneCommande.objects.create(
                    commande=commande,
                    meuble=meuble,
                    quantite=ligne['quantite'],
                    prix_unitaire=meuble.prix
                )
                # Décrémenter stock
                meuble.stock -= int(ligne['quantite'])
                meuble.save()
            
            # Calculer total
            commande.calculer_total()
            
            # IMPORTANT : Retourne JSON, pas de redirect, pas de render !
            return JsonResponse({
                'success': True, 
                'id': commande.id,
                'message': 'Commande créée avec succès'
            })
            
        except Exception as e:
            print(f"ERREUR API COMMANDES POST: {e}")
            return JsonResponse({'error': str(e)}, status=400)
    
    # PUT : Modifier statut
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            commande = Commande.objects.get(id=data['id'])
            commande.statut = data.get('statut', commande.statut)
            commande.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

# Détail d'une commande
@login_required
def api_commande_detail(request, commande_id):
    try:
        commande = get_object_or_404(Commande, id=commande_id)
        lignes = []
        for l in commande.lignes.all():
            lignes.append({
                'id': l.id,
                'meuble': l.meuble.nom,
                'quantite': l.quantite,
                'prix_unitaire': str(l.prix_unitaire),
                'sous_total': str(l.sous_total())
            })
        
        return JsonResponse({
            'id': commande.id,
            'client': commande.client.nom,
            'statut': commande.statut,
            'total': str(commande.total),
            'lignes': lignes
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)