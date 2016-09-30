# -*- coding: utf-8 -*-
"""
Created on Tue Jun  7 11:43:06 2016
j'avais un problème sur la partie où il y a des doubles rayons, en fait, 
il faut faire varier le rayon des cercles afin de retrouver des valeurs correctes

ce script est OK pour comparer avec l'altitude du terrain naturel.
Cependant, j'ai une erreur sur les pentes concaves voir les tests unitaires
je trouve des débuts et des fins de raccordement qui sont négatifs...

@author: vandanjon

"""
import math
import copy
import numpy as np

# A EFFACER
# je ne charge qu'une fois le fichier excel
#try:
#   altitude_projet_initial
#except NameError:
#    from openpyxl import load_workbook
#    nom_fichier_excel="calculs_coordonnees.xlsx"
#    donnees_declivite = load_workbook(filename=nom_fichier_excel,   data_only=True)
#    a=donnees_declivite.get_sheet_by_name("Profil initial NS-SN")
#    # dans le fichier la cote du terrain naturel est entre les lignes F4 et F248
#    # soit row=4 et row=248 et column=6
#    debut=6;
#    fin=8816;
#    col1=1;
#    col2=2;
#    n=fin-debut+1;
#    abscisse_projet_initial=np.zeros(n, dtype=np.float64)
#    altitude_projet_initial=np.zeros(n, dtype=np.float64)   
#    for i in np.arange(debut,fin+1):
#        #abscise_projet_initial[i-debut]=a.cell(row=i,column=col1).value
#        altitude_projet_initial[i-debut]=a.cell(row=i,column=col2).value
#    abscisse_projet_initial=np.arange(0,n)
# FIn A EFFACER


# calcul du projet initial 

def equation_droite(pente,point):
    "défini l'équiation de la droite à partir d'une pente et d'un point"
    plongi=point[0]
    altitude=point[1]
    a=pente/100.0;
    b=altitude-a*plongi;# a*point + b = altitude
    return a,b
    
def intersection(a1,b1,a2,b2):
    " défini l'intersection de deux droites "
    W=np.array([[-a1, 1],[-a2,1]])
    Y=np.array([b1,b2])
    sol=np.linalg.solve(W,Y)
    x = sol[0]
    y=  sol[1] 
    #print("intersection", x,y)
    return x,y
    
def perpendiculaire(a,b,x,y):
     if (abs(a)>1e-5) :
         a_perp=-1/a
         b_perp=y-a_perp*x
     else:
         a_perp=1e5
         b_perp=y+a_perp*np.sign(a)*x
     return a_perp,b_perp
     
def parallele1(a,b,r):
    x=0;
    y=a*x+b;
    ap, bp=perpendiculaire(a,0,0,0) 
    x_p = r/(math.sqrt(1+ap*ap)) # calcul du point appartenant après translation de (0,b)
    # a à partir de (0,0), la distance à 0,0 est xp^2 + ap^2 *xp^2 = R^2
    y_p = abs(ap*x_p)*np.sign(r) # gestion de la parallèle entre en dessus et en dessous
    # si c'est convexe, r est posiif et la parallèle est au dessus sinon la parallèle est en dessous
    x_par = x_p + x 
    y_par = y_p + y
    b_par = y_par-a*x_par
    return a, b_par
    
def parallele2(a,b,r):
    c=abs(a*r*math.sqrt(1/(1+a*a)))
    b_par=b+(abs(c/a)+abs(a*c))*np.sign(r)
    return a, b_par
    
def parallele(a,b,r):
    b_par=b+ r*math.sqrt(1+a*a)
    return a, b_par

def raccordement(a1,b1,a2,b2,r):
    " raccordement de deux droites par un cercle de rayon r"
    convexe=np.sign(a2-a1) # si c'est convexe convexe=1,  concave = convexe=-1
    rsigne = convexe*r
    a1_par, b1_par = parallele(a1,b1,rsigne)
    a2_par, b2_par = parallele(a2,b2,rsigne)  
    xc,yc = intersection(a1_par,b1_par,a2_par,b2_par)
    a_perp,b_perp=perpendiculaire(a1_par, b1_par, xc, yc)
    xdeb_cercle, ydeb_cercle = intersection(a_perp, b_perp, a1, b1)
    a_perp,b_perp=perpendiculaire(a2_par, b2_par, xc, yc)
    xfin_cercle, yfin_cercle = intersection(a_perp, b_perp, a2, b2)
    return xdeb_cercle, ydeb_cercle, xfin_cercle, yfin_cercle
    
    
# Test unitaire effectuté graphiquement sur le cahier pour vérifier
# que la fonction raccordement fonctionne bien
#pente1=-1/2*100
#x1=0
#y1=0
#point1=np.array([x1,y1])
#pente2=1/5*100
#x2=0
#y2=-7.5
#point2=np.array([x2,y2])
#r=4
#
#a1,b1 = equation_droite(pente1,point1)
#a2,b2 = equation_droite(pente2,point2)    
#xd,yd,xf,yf=raccordement(a1,b1,a2,b2,r)


def profil_en_long(point_de_depart, pente1,point_de_fin,pente2,pas,r,drapeau_fin)    :
    if abs(pente1-pente2)>1e-4:
        a1,b1= equation_droite(pente1, point_de_depart)
        a2,b2= equation_droite(pente2, point_de_fin)
        xd,yd,xf,yf=raccordement(a1,b1,a2,b2,r)
        extension=10000*pas
        abscisse = np.arange(point_de_depart[0]-extension, point_de_fin[0]+extension, pas) 
        abscisse1 = abscisse[abscisse<xd] ;
        abscisse1c= abscisse[abscisse>=xd] ;
        
        abscisse2 = abscisse[abscisse>xf] ;
        abscisse2c= abscisse[abscisse<=xf] ;
        
        altitude1= a1*abscisse1+b1
        altitude2= a2*abscisse2+b2
        
        abscisse_debut_rac = abscisse1c[0]
        abscisse_fin_rac = abscisse2c[-1]
        
        n_rac = round((abscisse_fin_rac-abscisse_debut_rac)/pas+1) 
        abscisse_cercle = np.linspace(abscisse_debut_rac, abscisse_fin_rac, n_rac, endpoint=True) 
        altitude_cercle= np.zeros_like(abscisse_cercle)
        dpente = (pente2/100.0-pente1/100.0)/n_rac ;
        pentek=pente1/100.0
        altitude_cercle[0]=altitude1[-1]+pentek*pas;
        k=1
        for abscissek in abscisse_cercle[1:].tolist():
            pentek=pentek+dpente
            altitude_cercle[k]=altitude_cercle[k-1]+pentek*pas
            k=k+1
        altitude=np.concatenate((altitude1, altitude_cercle, altitude2))
        
        k_drapeau=-1 
        if drapeau_fin: 
            k_drapeau=1
        indice=np.where((abscisse>(point_de_depart[0]-pas/2.0)) & (abscisse <(point_de_fin[0]+k_drapeau*pas/2.0)))
        abscisse=abscisse[indice[0]]
        altitude=altitude[indice[0]] 
    else:
        abscisse=np.arange(point_de_depart[0],point_de_fin[0],pas)
        altitude = point_de_depart[1]+(abscisse-abscisse[0])*(point_de_fin[1]-point_de_depart[1])/(point_de_fin[0]-point_de_depart[0])
    return abscisse, altitude
    
    
def profil_en_long_model_new(point_de_depart, pente1,point_de_fin,pente2,pas,r,drapeau_fin)    :
    if abs(pente1-pente2)>1e-4:
        a1,b1= equation_droite(pente1, point_de_depart)
        a2,b2= equation_droite(pente2, point_de_fin)
        
        xd,yd,xf,yf=raccordement(a1,b1,a2,b2,r)
        extension=10000*pas
        abscisse = np.arange(point_de_depart[0]-extension, point_de_fin[0]+extension, pas) 
        abscisse1 = abscisse[abscisse<xd] ;
        abscisse1c= abscisse[abscisse>=xd] ;
        
        abscisse2 = abscisse[abscisse>xf] ;
        abscisse2c= abscisse[abscisse<=xf] ;
        
        altitude1= a1*abscisse1+b1
        altitude2= a2*abscisse2+b2
        
        abscisse_debut_rac = abscisse1c[0]
        abscisse_fin_rac = abscisse2c[-1]
        
        n_rac = round((abscisse_fin_rac-abscisse_debut_rac)/pas+1) 
        abscisse_cercle = np.linspace(abscisse_debut_rac, abscisse_fin_rac, n_rac, endpoint=True) 
        altitude_cercle= np.zeros_like(abscisse_cercle)
        dpente = (pente2/100.0-pente1/100.0)/n_rac ;
    
        pentek=pente1/100.0
        altitude_cercle[0]=altitude1[-1]+pentek*pas;
        k=1
        for abscissek in abscisse_cercle[1:].tolist():
            pentek=pentek+dpente
            altitude_cercle[k]=altitude_cercle[k-1]+pentek*pas
            k=k+1
        altitude=np.concatenate((altitude1, altitude_cercle, altitude2))
        
        k_drapeau=-1 
        if drapeau_fin: 
            k_drapeau=1
            indice=np.where((abscisse>(point_de_depart[0]+pas/2.0)) & (abscisse <(point_de_fin[0]+k_drapeau*pas/2.0)))
        else:
            indice= np.where((abscisse>(point_de_depart[0]+pas/2.0)) & (abscisse <(abscisse_fin_rac+k_drapeau*pas/2.0)))
        abscisse=abscisse[indice[0]]
        altitude=altitude[indice[0]]    
    else:
        abscisse=np.arange(point_de_depart[0],point_de_fin[0],pas)
        altitude = point_de_depart[1]+(abscisse-abscisse[0])*(point_de_fin[1]-point_de_depart[1])/(point_de_fin[0]-point_de_depart[0])
    return abscisse, altitude
    
#test unitaire en comparaiant avec calcul coordonnees.xlsx
# cela fonctionne impeccable
# j'ai vérifié sur certains points
# le calcul du cercle fonctionne bien
# le code suivant fonctionne
#pente1=-5.215
#point_de_depart=np.array([0,375.42])
#r=3015.17891
#pente2=-0.502
#point_de_fin=np.array([711,352.51])
#pas=1
#x,y=profil_en_long(point_de_depart, pente1,point_de_fin,pente2,pas,r,True) 

# Le code suivant bogue
#pente1=-0.502
#point_de_depart==np.array([480,353.67])
#r=13508.0
#pente2=-1.883
#point_de_fin==np.array([2169,326.36])
#pas=1
#x,y=profil_en_long(point_de_depart, pente1,point_de_fin,pente2,pas,r,True) 


#pente1=2.032
#point_de_depart=np.array([4600.0,323.57])
#r=50000.0
#pente2=0.923
#point_de_fin=np.array([6457.0,331.57])
#pas=1
#x,y=profil_en_long(point_de_depart, pente1,point_de_fin,pente2,pas,r,True) 



# Cela marche super sauf pour les cas où il y a deux rayons qui s'enchainent...
# dans ce cas, c'est problématique
# il faut mettre une pente de valeur nulle





def profil_rn7(limites):
    pas=1.0
    limite_prec=limites[0]
    n=len(limites)
    #recouvrement = 120 # on prend un point 120m avant pour éviter que le rayon soit nul
    for k in range(1,n,1):
            limite=limites[k]    
            point_de_depart=np.array(limite_prec[0:2])
            pente1=limite_prec[2]
            r=limite_prec[3]
            point_de_fin=np.array(limite[0:2])
            pente2=limite[2]
            drapeau_fin= (k==n)
            x,y=profil_en_long(point_de_depart, pente1,point_de_fin,pente2,pas,r, drapeau_fin) 
            limite_prec=limite       
            if k==1:
                abscisse=np.copy(x)
                altitude=np.copy(y)
            else:
                abscisse=np.concatenate((abscisse,x))
                altitude=np.concatenate((altitude,y))
    return abscisse, altitude
    



def profil_rn(limites):
    pas=1
    depart_profil=limites[0]
    abscisse=np.array([depart_profil[1]],dtype='f8')
    altitude=np.array([depart_profil[0]],dtype='f8' )
    
    altitude_point_intersection_precedent=depart_profil[0]
    abscisse_point_intersection_precedent=depart_profil[1]
    pente_precedente=depart_profil[2]    
    point_de_depart=np.array([abscisse_point_intersection_precedent, altitude_point_intersection_precedent],dtype='f8')
    n=len(limites)
    for k in range(1,n-1,1):
            limite=limites[k]
            abscisse_point_intersection=limite[0]
            pente=limite[1]
            abscisse_point_intersection_suivant=limites[k+1][0]
            rayon=limite[2]
            
            difference_abscisse= abscisse_point_intersection-abscisse_point_intersection_precedent
            altitude_point_intersection=altitude_point_intersection_precedent + pente_precedente*difference_abscisse/100.0
            
            difference_abscisse= abscisse_point_intersection_suivant-abscisse_point_intersection
            altitude_point_intersection_suivant=altitude_point_intersection + pente*difference_abscisse/100.0
            
            drapeau_fin= (k==(n-2))
            point_de_fin=np.array([abscisse_point_intersection_suivant, altitude_point_intersection_suivant], dtype='f8')
            
            x,y=profil_en_long_model_new(point_de_depart, pente_precedente,point_de_fin,pente,pas,rayon, drapeau_fin) 
            #limite_prec=limite       
#            if k==1:
#                abscisse=np.copy(x)
#                altitude=np.copy(y)
#            else : # drapeau_fin :
            
            abscisse=np.concatenate((abscisse,x))
            altitude=np.concatenate((altitude,y))
#            else:
#                indice=np.where(x < (abscisse[-1]+pas/2) )
#                np.delete(x,indice)
#                np.delete(y,indice)
#                abscisse=np.concatenate((abscisse,x))
#                altitude=np.concatenate((altitude,y))
#                
                
            altitude_point_intersection_precedent=altitude_point_intersection
            abscisse_point_intersection_precedent=abscisse_point_intersection
            pente_precedente=pente 
            point_de_depart=np.array([abscisse[-1], altitude[-1]], dtype='f8')
            
                
                
    return abscisse, altitude




# Cela fonctionne sauf pour le cas où deux rayons se suivent.
# Dans ce cas, il faut réfléchir et créer une pente virtuelle
# Mais je m'arrête au point final 
# je donne une pente et un point, je fais l'abscisse comme je veux
# mais je ne sélectionne que jusqu'au point final et là cela doit fonctionner


        
    

limites_de_section=[[0,375.42, -5.215, 3015], 
                    [711, 352.51, -0.502,13508],
[2169, 326.36 ,-1.883, 30023],
[2871, 319.60, -0.620, 10073],
[3131, 321.37,1.985, 14969], 
[4035, 318.99, -0.996, 14955],
[4300, 318.68, 0.75,14657],
[4900, 329.67, 2.032, 10491],
[5435, 326.92, -3.15, 8014],
[5860, 325.19, 2.3, 9872],
[6457,331.57,0.923, 7789], 
[6532,332.61,1.871, 10539], 
[7260, 338.18, 0.656, 14622],
[8365, 334.87,-0.372,14825],
[8810, 328.29,-1.843]]




def model_old2model_new(limites_old):
    n=len(limites_old)
    limites_new=[]
    liste_de_depart=[]
    liste_courante=[]
    liste_de_depart.append(limites_old[0][1]) # altitude de départ
    liste_de_depart.append(limites_old[0][0]) # abscisse de départ
    liste_de_depart.append(limites_old[0][2]) # pente de départ
    limites_new.append(copy.deepcopy(liste_de_depart))
    for k in range(1,n,1):
        # calcul de l'abscisse du point d'intersection
        a1,b1= equation_droite(limites_old[k-1][2], np.array([limites_old[k-1][0], limites_old[k-1][1]],dtype='f8'))
        a2,b2= equation_droite(limites_old[k][2], [limites_old[k][0], limites_old[k][1]])
        abscisse_intersection, altitude_intersection=intersection(a1,b1,a2,b2)                     
        liste_courante[:]=[] # vide la liste
        liste_courante.append(abscisse_intersection) # ajout de l'abscisse de l'intersection
        liste_courante.append(limites_old[k][2]) # ajout de la pente
        liste_courante.append(limites_old[k-1][3]) # ajout du rayon
        limites_new.append(copy.deepcopy(liste_courante))

    limites_new.append([limites_old[n-1][0]])
    return limites_new
    
limites_nouvelles=model_old2model_new(limites_de_section)
xx,yy=profil_rn(limites_nouvelles)


# nouvelle modélisation du profil modifié par Michel Dauvergne

profil_modifie_michel=[[0.0,375.42, -5.215, 3015],
[711 , 352.51, -0.502, 13508],
[1762, 334.03, -1.883, 15127],
[2596, 324.39, -1.1, 20000],
[3405, 323.99, 0.140, 20000],
[3814, 321.20, -1.000, 30000],
[4804, 325.92, 1.230, 30000],
[5440, 326.99, -0.880, 29544],
[6457, 331.57, 0.923, 7789],
[6532, 332.61, 1.871, 10539],
[7260, 338.18, 0.656, 14622],
[8365, 334.87, -0.372, 14825],
[8810, 328.29, -1.843]]


profil_modifie_michel_new=model_old2model_new(profil_modifie_michel)
xxx,yyy=profil_rn(profil_modifie_michel_new)

profil_modifie_michel_incremente=copy.deepcopy(profil_modifie_michel_new);
increment=0.01;
profil_modifie_michel_incremente[4][1]=profil_modifie_michel_incremente[4][1]+increment;
xxxinc,yyyinc=profil_rn(profil_modifie_michel_incremente)
deriveeX8=(yyyinc[-1]-yyy[-1])/increment
deriveeX8_symbolique=(profil_modifie_michel_incremente[5][0]-profil_modifie_michel_incremente[4][0])/100.00


profil_modifie_michel_incremente=copy.deepcopy(profil_modifie_michel_new);
increment=0.01;
profil_modifie_michel_incremente[3][0]=profil_modifie_michel_incremente[3][0]+increment;
profil_modifie_michel_incremente[4][0]=profil_modifie_michel_incremente[4][0]+increment;
profil_modifie_michel_incremente[5][0]=profil_modifie_michel_incremente[5][0]+increment;
profil_modifie_michel_incremente[6][0]=profil_modifie_michel_incremente[6][0]+increment;
profil_modifie_michel_incremente[7][0]=profil_modifie_michel_incremente[7][0]+increment;
profil_modifie_michel_incremente[8][0]=profil_modifie_michel_incremente[8][0]+increment;
xxxinc,yyyinc=profil_rn(profil_modifie_michel_incremente)
deriveeX1=(yyyinc[-1]-yyy[-1])/increment
deriveeX1_symbolique=(profil_modifie_michel_incremente[2][1]-profil_modifie_michel_incremente[8][1])/100


profil_modifie_michel_incremente=copy.deepcopy(profil_modifie_michel_new);
increment=0.01;
profil_modifie_michel_incremente[8][1]=profil_modifie_michel_incremente[8][1]+increment;
xxxinc,yyyinc=profil_rn(profil_modifie_michel_incremente)
deriveeX12=(yyyinc[-1]-yyy[-1])/increment
deriveeX12_symbolique=(profil_modifie_michel_incremente[9][0]-profil_modifie_michel_incremente[8][0])/100




    