import random
import time
from .fonctions import *
from .cartes import *
from .mine import *

#%%
class Joueur:
    def __init__(self,nom,role='',Main=[]):
    #on initialise le joueur en lui assignant un Role au hasard et en lui donnant un paquet de cartes
        self.nom=nom
        self.__role=role
        self.main=Main 
        self.broken = [] #par défaut aucun objet n'est cassé
        self.points = 0
        
    @property
    def role( self ) :
        return self.__role
    
    @role.setter
    def role( self, role ) :
        if role == 'Saboteur' or role == 'Chercheur':
            self.__role = role
    
    def jouer(self,Joueurs,Mine,Paquet):
        fin = False
        last=False
        input(self.nom +', c est à toi ! / appuie sur Entree pour continuer')
        print(self.main)
        
        # affichage des outils cassés de tous les joueurs
        s=''
        for J in Joueurs:
            if J.broken : 
                s+='\n'+J.nom+' : '
                for o in J.broken: s+=o+', '
        if len(s) != 0:
            s='Outils cassés : '+s
            print(s[:-2])
        time.sleep(0.5)
        
        # phase de jeu
        played=False
        while played == False:
            action = int(restrictedInput('Quelle carte/action jouer?',1,self.main.n+2))-1                           
            
            #1ere action possible : défausser une carte et piocher
            if action == self.main.n:
                i = int(restrictedInput('Quelle carte défausser?',1,self.main.n))-1
                del self.main.cartes[i]
                if len(Paquet) != 0: #s'il n'y a plus de cartes dans la pioche on ne pioche pas
                    self.main.piocher(Paquet)
                else:
                    self.main.n-=1
                print(self.main)
                time.sleep(0.5)
                played=True
            
            #2eme action possible : retourner une carte (mais cela ne compte pas comme un tour de jeu)
            elif action == self.main.n+1:
                i=int(restrictedInput('Quelle carte tourner?',1,self.main.n))-1
                while not isinstance(self.main.cartes[i],CarteChemin):
                    print('Vous ne pouvez tourner que les cartes chemin')
                    i=int(restrictedInput('Quelle carte tourner?',1,self.main.n))-1
                self.main.cartes[i]=self.main.cartes[i].rotationCarte()
                print(self.main)
                time.sleep(0.5)
            
            #3eme action possible : jouer une carte
            else:
                
                #si c'est une carte action outil il faut savoir sur quel joueur
                if isinstance(self.main.cartes[action], CarteActionOutil):
                    s=''
                    for i in range(len(Joueurs)):
                        s+=str(i)+' : '+Joueurs[i].nom+' | '
                    J=restrictedInput('Sur quel joueur voulez-vous jouer cette carte?\n'+s,0,len(Joueurs))
                    played = self.main.cartes[action].jouerCarte(Joueurs[J])
            
                #si c'est une carte chemin il ne faut pas que le joueur ait un outil cassé
                elif isinstance(self.main.cartes[action],CarteChemin):
                    if not self.broken:
                        ligne = int(restrictedInput('Quelle ligne?',-1,Mine.lignes))
                        time.sleep(0.2)
                        colonne = int(restrictedInput('Quelle colonne?',-1,Mine.colonnes))
                        time.sleep(0.2)

                        played,fin = self.main.cartes[action].jouerCarte(Mine,ligne,colonne)
                    else:
                        print('Vous devez réparer vos outils avant de jouer')
                
                #sinon on peut jouer directement sur le plateau
                else:
                    played = self.main.cartes[action].jouerCarte(Mine)
                
                #et on repioche une carte s'il en reste dans le paquet
                if played == True:
                    del self.main.cartes[action]
                    if len(Paquet) != 0: 
                        self.main.piocher(Paquet)
                    else:
                        self.main.n-=1
                    # on enregistre etre le dernier joueur ayant joué une carte(utile entre les manches)
                    last=True
        return fin,last

#%% IA

def findMinManhattan(IA,Mine):
    d0=[manhattan([2,0],a) for a in IA.arrivees]
    for l,c in ((lig,col) for lig in range(Mine.lignes) for col in range(Mine.colonnes)):
        if Mine.mine[l][c]!=0:
            for a in range(len(IA.arrivees)):
                if Mine.verifierChemin(Mine.depart,[l,c]) and manhattan([l,c],IA.arrivees[a])<d0[a]:
                    d0[a]=manhattan([l,c],IA.arrivees[a])
    return d0


class IA(Joueur):
    def __init__(self,nom,role='',Main=[]):
        super().__init__(nom,role='',Main=[])
        self.arrivees=[[0,8],[2,8],[4,8]]

    def choisirActionChercheur(self,Joueurs,Mine):
        score=[]
        ligne=[]
        colonne=[]
        #on parcourt toutes les cartes de la main et on donne un score à chaque carte. L'ia jouera au hasard une des cartes avec le score le plus élevé
        for carte in self.main.cartes:

            #rating des actions possibles pour les cartes chemin
            if isinstance(carte, CarteChemin):
                #si objet cassé : inutile
                if self.broken:
                    s=0
                    li=0
                    co=0
                else: 
                    d0=findMinManhattan(self,Mine)
                    s=0
                    li=0
                    co=0
                    #on parcourt le plateau pour chercher les emplacements disponibles
                    for l,c in [(lig,col) for lig in range(Mine.lignes) for col in range(Mine.colonnes)]:
                        carte2=carte.rotationCarte()
                        if (Mine.poserCarte(carte,l,c,disp=False) or Mine.poserCarte(carte2,l,c,disp=False)) and carte.chemins[4] == '+': 
                            
                            #meilleure action : finir
                            
                            if any([Mine.verifierChemin(Mine.depart,[l-1,c],True) and carte.chemins[0]==1,\
                                    Mine.verifierChemin(Mine.depart,[l+1,c],True) and carte.chemins[2]==1,\
                                    Mine.verifierChemin(Mine.depart,[l,c-1],True) and carte.chemins[1]==1,\
                                    Mine.verifierChemin(Mine.depart,[l,c+1],True) and carte.chemins[3]==1]):
                                test=[]
                                test2=[]
                                
                                for a in self.arrivees:   
                                    test.append(([l,c] == [a[0]+1,a[1]] and carte.chemins[0] == 1)\
                                        or ([l,c] == [a[0],a[1]+1] and carte.chemins[1] == 1)\
                                        or ([l,c] == [a[0]-1,a[1]] and carte.chemins[2] == 1)\
                                        or ([l,c] == [a[0],a[1]-1] and carte.chemins[3] == 1))
                                    
                                    test2.append(([l,c] == [a[0]+1,a[1]] and carte2.chemins[0] == 1)\
                                        or ([l,c] == [a[0],a[1]+1] and carte2.chemins[1] == 1)\
                                        or ([l,c] == [a[0]-1,a[1]] and carte2.chemins[2] == 1)\
                                        or ([l,c] == [a[0],a[1]-1] and carte2.chemins[3] == 1))
    
                                if any(test) or any(test2):
                                    s=4
                                    li=l
                                    co=c
                                    break
                            
                            #super action : avancer le chemin le plus avancé
                            if any([manhattan([l,c],a)<min(d0) for a in self.arrivees]):
                                s=3
                                li=l
                                co=c
                            
                            #bonne action : avancer un autre chemin
                            elif any([manhattan([l,c],self.arrivees[i])<d0[i] for i in range(len(self.arrivees))]):
                                s=2
                                li=l
                                co=c

                score.append(s)
                ligne.append(li)
                colonne.append(co)

            #rating des actions possibles pour les cartes action
            elif isinstance(carte,CarteActionOutil):

                #action ok : réparer les outils d'un autre joueur
                test=[(any([carte.outil == b for b in J.broken]) or any([carte.outil2 == b for b in J.broken])) for J in Joueurs]
                if carte.status =='reparer' and any(test):
                    score.append(1)
                    ligne.append(0)
                    colonne.append(0)
                else:
                    score.append(0)
                    ligne.append(0)
                    colonne.append(0)

                #très bonne action : regarder les arrivées (si on ne sait pas encore où est la pépite)
            elif isinstance(carte,CartePlan) and len(self.arrivees)>1:
                score.append(3)
                ligne.append(0)
                colonne.append(0)
                
                #bonne action : ébouler une carte 'x' s'il y en a
            elif isinstance(carte,CarteEboulement):
                coord=[]
                for l,c in [(lig,col) for lig in range(Mine.lignes) for col in range(Mine.colonnes)]:
                    if Mine.mine[l][c] != 0 :
                        if Mine.mine[l][c].chemins[4] == 'x': 
                            coord.append([l,c])           
                if len(coord) == 0:
                    s=0
                    li=0
                    co=0
                else:
                    s=2
                    r=random.choice(coord)
                    li=r[0]
                    co=r[1]

                score.append(s)
                ligne.append(li)
                colonne.append(co)
                
                
            else:
                score.append(0)
                ligne.append(0)
                colonne.append(0)
        return score,ligne,colonne
    
    def choisirActionSaboteur(self,Joueurs,Mine):
        score=[]
        ligne=[]
        colonne=[]
        #on parcourt toutes les cartes de la main et on donne un score à chaque carte. L'ia jouera au hasard une des cartes avec le score le plus élevé
        for carte in self.main.cartes:

            #rating des actions possibles pour les cartes chemin
            if isinstance(carte, CarteChemin):
                #si objet cassé : inutile
                if self.broken:
                    s=0
                    li=0
                    co=0
                    
                else: 
                    d0=findMinManhattan(self,Mine)
                    s=0
                    li=0
                    co=0
                    #on parcourt le plateau pour chercher les emplacements disponibles
                    for l,c in [(lig,col) for lig in range(Mine.lignes) for col in range(Mine.colonnes)]:
                        carte2=carte.rotationCarte()
                        if (Mine.poserCarte(carte,l,c,disp=False) or Mine.poserCarte(carte2,l,c,disp=False)) and carte.chemins[4] == 'x': 
                            
                            #très bonne action : poser une carte cul de sac sur le chemin le plus avancé
                            if any([manhattan([l,c],a)<min(d0) for a in self.arrivees]):
                                s=3
                                li=l
                                co=c
                            
                            #bonne action : bloquer un autre chemin
                            elif any([manhattan([l,c],self.arrivees[i])<d0[i] for i in range(len(self.arrivees))]):
                                s=2
                                li=l
                                co=c

                score.append(s)
                ligne.append(li)
                colonne.append(co)

            #rating des actions possibles pour les cartes action
            elif isinstance(carte,CarteActionOutil):

                #meilleure action : casser les outils d'un autre joueur
                if carte.status == 'casser':
                    score.append(4)
                    ligne.append(0)
                    colonne.append(0)
                
                #action ok : réparer son propre outil
                elif carte.status =='reparer' and ( any([carte.outil == b for b in self.broken]) or any([carte.outil2 == b for b in self.broken])):
                    score.append(1)
                    ligne.append(0)
                    colonne.append(0)
                else:
                    score.append(0)
                    ligne.append(0)
                    colonne.append(0)

            #très bonne action : éboulement (random sur carte '+')
            elif isinstance(carte,CarteEboulement):
                coord=[]
                for l,c in [(lig,col) for lig in range(Mine.lignes) for col in range(Mine.colonnes)]:
                    if Mine.mine[l][c] != 0 :
                        if Mine.mine[l][c].chemins[4] == '+': 
                            coord.append([l,c])
                        
                if len(coord) == 0:
                    s=0
                    li=0
                    co=0
                else:
                    s=2
                    r=random.choice(coord)
                    li=r[0]
                    print(li)
                    co=r[1]
                    print(co)

                score.append(s)
                ligne.append(li)
                colonne.append(co)
            
            else:
                score.append(0)
                ligne.append(0)
                colonne.append(0)
                
        return score,ligne,colonne
        

    def jouer(self,Joueurs,Mine,Paquet):
        fin = False
        last=False
        print('C est à '+self.nom)
        print(self.role)
        print(self.main)

        if self.role == 'Chercheur':
            score,ligne,colonne = self.choisirActionChercheur(Joueurs,Mine)
        else:
            score,ligne,colonne = self.choisirActionSaboteur(Joueurs,Mine)
        print(score)

        played=False
        m = max(score)
        bestactions = [i for i, j in enumerate(score) if j == m]
        action = random.choice(bestactions) 
        ligne=ligne[action]
        colonne=colonne[action]  

        #s'il n'y a pas de meilleure action l'ia doit défausser une carte
        if all([s==0 for s in score]):
            print(self.nom+' défausse une carte')
            played=True

        else:                      

            #si c'est une carte action outil 
            if isinstance(self.main.cartes[action], CarteActionOutil):
                #si l'ia est chercheur elle doit réparer un objet au hasard parmi les objets cassés
                if self.role == 'Chercheur':
                    for j in Joueurs:
                        if any([b == self.main.cartes[action].outil or b == self.main.cartes[action].outil2] for b in j.broken):
                            J=j
                            
                #si elle est saboteur elle doit soit réparer son propre outil
                elif self.role == 'Saboteur' :
                    if self.main.cartes[action].status == 'reparer':
                        J=self
                    #soit casser l'outil d'un autre joueur
                    else:
                        J=random.choice(Joueurs)
                        while J == self:
                            J=random.choice(Joueurs)
                
                played = self.main.cartes[action].jouerCarte(J)
                if played:
                    print(self.nom+' a choisi de '+self.main.cartes[action].status+' les outils de '+J.nom)
                else:
                    print('Erreur : '+self.nom+' a essayé de '+self.main.cartes[action].status +' un outil à '+J.nom+' mais n a pas réussi')
            
            #si c'est une carte chemin
            elif isinstance(self.main.cartes[action],CarteChemin):
                played,fin = self.main.cartes[action].jouerCarte(Mine,ligne,colonne)
                print('played = '+ str(played))
                if not played:
                    carte2=self.main.cartes[action].rotationCarte()
                    played,fin = carte2.jouerCarte(Mine,ligne,colonne)
                if played:
                    print(self.nom+' a joué la carte '+str(action+1))
                else:
                    print('Erreur : '+self.nom+' a essayé de poser la carte '+str(action)+' mais n a pas réussi')
                    
            #si c'est une carte plan
            elif isinstance(self.main.cartes[action],CartePlan):
                n=random.randint(0,len(self.arrivees)-1)
                if Mine.pepite == n:
                    self.arrivees=[self.arrivees[n]]
                else:
                    del(self.arrivees[n])
                print(self.nom+' a joué une carte plan')
                played=True
                
            #si c'est une carte éboulement
            elif isinstance(self.main.cartes[action],CarteEboulement):
                played = self.main.cartes[action].jouerCarte(Mine,ligne,colonne)

            # on enregistre etre le dernier joueur ayant joué une carte(utile entre les manches)
            last=True
            print('played = '+str(played))

        #et on repioche une carte s'il en reste dans le paquet
        del self.main.cartes[action]
        if len(Paquet) != 0: 
            self.main.piocher(Paquet)
        else:
            self.main.n-=1

        return fin,last




                






