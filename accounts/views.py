from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Profile
import json

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'accounts/login.html', {'error': 'Identifiants invalides'})
    return render(request, 'accounts/login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    if request.user.profile.is_admin():
        return render(request, 'core/dashboard_admin.html')
    elif request.user.profile.is_vendeur():
        return render(request, 'core/dashboard_vendeur.html')
    else:
        return render(request, 'core/dashboard_client.html')

@login_required
@csrf_exempt
def api_users(request):
    if not request.user.profile.is_admin():
        return JsonResponse({'error': 'Accès refusé'}, status=403)
    
    if request.method == 'GET':
        users = User.objects.all().select_related('profile')
        data = []
        for u in users:
            data.append({
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'first_name': u.first_name,
                'last_name': u.last_name,
                'role': u.profile.role,
                'telephone': u.profile.telephone
            })
        return JsonResponse(data, safe=False)
    
    elif request.method == 'POST':
        data = json.loads(request.body)
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', '')
        )
        user.profile.role = data.get('role', 'client')
        user.profile.telephone = data.get('telephone', '')
        user.profile.save()
        return JsonResponse({'success': True, 'id': user.id})
    
    elif request.method == 'PUT':
        data = json.loads(request.body)
        user = User.objects.get(id=data['id'])
        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.save()
        user.profile.role = data.get('role', user.profile.role)
        user.profile.telephone = data.get('telephone', user.profile.telephone)
        user.profile.save()
        return JsonResponse({'success': True})
    
    elif request.method == 'DELETE':
        data = json.loads(request.body)
        User.objects.get(id=data['id']).delete()
        return JsonResponse({'success': True})