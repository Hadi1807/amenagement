from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
import requests
import json
from .models import Conversation

@login_required
@csrf_exempt
def chat_ollama(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        message = data.get('message', '')
        
        # Contexte métier aménagement
        contexte = """Tu es un conseiller expert en aménagement d'intérieur et mobilier. 
        Tu aides les clients à choisir des meubles adaptés à leur espace, style et budget. 
        Sois concis, professionnel et chaleureux. Maximum 3 phrases par réponse."""
        
        try:
            response = requests.post(
                settings.OLLAMA_URL,
                json={
                    'model': settings.OLLAMA_MODEL,
                    'prompt': f"{contexte}\n\nClient: {message}\nConseiller:",
                    'stream': False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                reponse_ia = response.json().get('response', 'Désolé, je ne peux pas répondre pour le moment.')
                
                # Sauvegarder conversation
                Conversation.objects.create(
                    user=request.user,
                    message=message,
                    reponse=reponse_ia
                )
                
                return JsonResponse({'reponse': reponse_ia})
            else:
                return JsonResponse({'reponse': 'Le service IA est temporairement indisponible.'})
                
        except Exception as e:
            return JsonResponse({'reponse': f'Erreur de connexion: {str(e)}'})
    
    return JsonResponse({'error': 'Méthode non autorisée'})

@login_required
def historique_chat(request):
    conversations = Conversation.objects.filter(user=request.user).order_by('-date')[:20]
    data = [{
        'message': c.message,
        'reponse': c.reponse,
        'date': c.date.strftime('%d/%m/%Y %H:%M')
    } for c in conversations]
    return JsonResponse(data, safe=False)