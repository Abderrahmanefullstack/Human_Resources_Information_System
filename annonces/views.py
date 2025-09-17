from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import AnnonceRH
from .forms import AnnonceRHForm


@login_required
def annonce_list(request):
    q = (request.GET.get("q") or "").strip()
    qs = AnnonceRH.objects.all()
    if q:
        qs = qs.filter(titre__icontains=q) | qs.filter(contenu__icontains=q)
    return render(request, "annonces/annonce_list.html", {"annonces": qs, "q": q})


@login_required
def annonce_create(request):
    if request.method == "POST":
        form = AnnonceRHForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Annonce créée.")
            return redirect("annonces:list")
    else:
        form = AnnonceRHForm()
    return render(request, "annonces/annonce_form.html", {"form": form, "create": True})


@login_required
def annonce_update(request, pk):
    obj = get_object_or_404(AnnonceRH, pk=pk)
    if request.method == "POST":
        form = AnnonceRHForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Annonce mise à jour.")
            return redirect("annonces:list")
    else:
        form = AnnonceRHForm(instance=obj)
    return render(
        request, "annonces/annonce_form.html", {"form": form, "create": False}
    )


@login_required
def annonce_delete(request, pk):
    obj = get_object_or_404(AnnonceRH, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Annonce supprimée.")
        return redirect("annonces:list")
    return render(request, "annonces/annonce_confirm_delete.html", {"obj": obj})
