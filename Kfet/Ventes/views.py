# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, get_list_or_404
from Commun.models.Produit import *
from Commun.models.Vente import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse


def index(request, erreur=None):
    list_produit = get_list_or_404(Produit)

    if erreur == "1":
        error = "Merci de spécifier un chiffre ou de cliquer directement sur le produit pour une vente unique."
    else:
        error = ""
    
    paginator = Paginator(list_produit, 12) # Show 10 items per page
    page = request.GET.get('page',1)
    try:
        produits = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        produits = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        produits = paginator.page(paginator.num_pages)
    
    try:
        vente = Vente.objects.latest('date')
    except Vente.DoesNotExist:         
        vente = Vente()

    return render_to_response('Ventes/index.html', {'produit':produits, 'vente':vente, 'error':error}, context_instance=RequestContext(request) )

def produit_vente(request, produit_id):
    if request.method == 'POST':
        try:
            quantite = int(request.POST['quantite'])
        except ValueError:
            quantite = 0
    else:
        quantite = 1

    if quantite != 0:
        produit = Produit.objects.get(pk=produit_id)
        produit.quantite = produit.quantite - quantite
        produit.save()

        vente = Vente(produit_id=produit_id, quantite=quantite)
        vente.save()
        return HttpResponseRedirect(reverse('Kfet.Ventes.views.index'))
    else:
        return HttpResponseRedirect(reverse('Kfet.Ventes.views.index', args=["1"]))


    
def annuler_vente(request, vente_id):
    
    vente = Vente.objects.get(pk=vente_id)

    produit = Produit.objects.get(pk=vente.produit.id)
    produit.quantite = produit.quantite + vente.quantite
    produit.save()
    vente.delete()

    return HttpResponseRedirect(reverse('Kfet.Ventes.views.index'))

