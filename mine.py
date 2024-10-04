import random
from .cartes import *

#%%Mine = plateau de jeu

class Mine:
    def __init__(self):
        self.colonnes=9
        self.lignes=5
        self.depart=[2,0]
        self.arrivee=[[0,8],[2,8],[4,8]]        
        self.__pepite=random.randint(0,2)
        #choix aléatoire de la position du trésor parmi les 3 arrivées
        
        self.mine = [[0 for x in range(self.colonnes)] for y in range(self.lignes)]
        #on construit le tableau correspondant au plateau de jeu : on initialise toutes les valeurs à 0 
        #elles seront remplacées par des cartes au fur et à mesure du jeu
        self.mine[self.depart[0]][self.depart[1]]=CarteDepart
        #on place la carte de départ
        
        for i in range(3):
            self.mine[self.arrivee[i][0]][self.arrivee[i][1]]=CarteArrivee(i==self.__pepite)
        #et les 3 cartes arrivées
        
        
    # Les properties
    @property
    def pepite( self ) :
        return self.__pepite
    
    def __str__(self): #affichage du plateau
        p='Current mine state:\n |'
        for i in range(self.colonnes):
            p+='  '+str(i)+'  '
        p+='\n-+'+self.colonnes*'-----'+'\n'  
        for i in range(self.lignes):
            for a in range(3):
                if a == 1:
                    p+=str(i)+'|'
                else:
                    p+=' |'
                for j in range(self.colonnes):
                    if self.mine[i][j] == 0:
                        p+='     '
                    else:
                        p+=self.mine[i][j].afficherCarte()[a]
                p+='\n'
        return p
    
    def poserCarte(self,cartechemin,ligne,colonne,disp=True):
    #méthode pour poser une cartechemin à un endroit du plateau indiqué par ses coordonées (ligne,colonne)
        
        #changements de variables pour faciliter la lecture
        m = self.mine
        l = ligne
        c = colonne
        
        if not isinstance(cartechemin,CarteChemin) :
            if disp: 
                print('Merci de choisir une carte chemin')
            return False
        
        if m[l][c] !=0:
        #il faut qu'il n'y ait pas déjà une carte à l'emplacement donné
            if disp: 
                print('Vous ne pouvez pas poser cette carte ici!\nMerci de choisir une autre action')
            return False
         
        gauche, droite, haut, bas = False, False, False, False 
        #variables qui vont tester s'il y a une carte dans chaque direction
        nongauche,nondroite,nonhaut,nonbas = True,True,True,True 
        #variables qui vont tester si on peut poser une carte à côté en fonction des chemins
        chg,chd,chb,chh = False,False,False,False
        #variables qui vont servir à tester s'il y a un chemin pour accéder à l'emplacement
        
        if c>0:
            gauche = m[l][c-1] != 0 
            if gauche :
                chg = self.verifierChemin(self.depart,[l,c-1]) and m[l][c-1].chemins[3] == 1
                nongauche = m[l][c-1].chemins[3] != cartechemin.chemins[1] 
                if any([[l,c-1] == a for a in self.arrivee]): nongauche = False
            
        if c<self.colonnes-1:
            droite = m[l][c+1] != 0 
            if droite :
                chd = self.verifierChemin(self.depart,[l,c+1]) and m[l][c+1].chemins[1] == 1
                nondroite = m[l][c+1].chemins[1] != cartechemin.chemins[3] 
                if any([[l,c+1] == self.arrivee[i] for i in range(len(self.arrivee))]): nondroite = False     
                        
        if l<self.lignes-1:
            bas = m[l+1][c] != 0 
            if bas :
                chb = self.verifierChemin(self.depart,[l+1,c]) and m[l+1][c].chemins[0] == 1
                nonbas = m[l+1][c].chemins[0]!=cartechemin.chemins[2] 
                if any([[l+1,c] == self.arrivee[i] for i in range(len(self.arrivee))]): nonbas = False

        if l>0:
            haut = m[l-1][c] != 0 
            if haut :
                chh = self.verifierChemin(self.depart,[l-1,c]) and m[l-1][c].chemins[2] == 1
                nonhaut = m[l-1][c].chemins[2]!=cartechemin.chemins[0]
                if any([[l-1,c] == self.arrivee[i] for i in range(len(self.arrivee))]): nonhaut = False
                      
        if any ([gauche, droite, haut, bas]) and any([chd,chg,chb,chh]) and gauche*nongauche+droite*nondroite+haut*nonhaut+bas*nonbas == 0 :  
            return True
        
        if disp: 
            print('Vous ne pouvez pas poser cette carte ici!\nMerci de choisir une autre action')
        return False
           

    def verifierChemin(self,coord_i,coord_f,strong=False):
        #méthode pour vérifier s'il existe un chemin valide entre deux points
        
        if coord_i == coord_f:
            return True
        
        l0,c0=coord_i[0],coord_i[1]
        visited = [[False for x in range(self.colonnes)] for y in range(self.lignes)]
        noeud=[]
        #tableaux qui servent à stocker les cases explorées et les noeuds d'où partent plusieurs chemin
        fin = False
        
        while fin == False and c0<self.colonnes and l0<self.lignes:
            #on compte le nombre de directions possibles à partir des coordonnées actuelles
            n_ch=0
            for i in [-1,+1]:
                n_ch += isValid(self,visited,l0,l0+i,c0,c0,strong)
                n_ch += isValid(self,visited,l0,l0,c0,c0+i,strong)
                #strong : booléen permettant de choisir si on veut un chemin sans cul de sac (ex : pour arriver à l'arrivée)
                # ou seulement une connexion entre une case et une autre, sans tenir compte des cul de sac (ex : pour poser une carte après un éboulement)
            
            #s'il n'y a aucun chemin possible on retourne au dernier noeud ou on termine s'il n'y en a pas
            if n_ch == 0:
                if len(noeud) == 0:
                    fin = True
                    return False
                else:
                    l0 = noeud[-1][0]
                    c0 = noeud[-1][1]
                    del noeud[-1]
                            
            #si on a plusieurs chemins possibles on garde le noeud en mémoire
            elif n_ch > 1:
                noeud.append([l0,c0])
                
            #et on explore les différentes directions
            if n_ch>=1:
                for l1 in [l0-1,l0+1]:
                    if isValid(self,visited,l0,l1,c0,c0,strong):
                        l0=l1
                        visited[l0][c0] = not([l0,c0] in noeud)
                        if isNextTo([l0,c0],coord_f,self.mine):
                            return True
                        break
                else:
                    for c1 in [c0-1,c0+1]:
                        if isValid(self,visited,l0,l0,c0,c1,strong):
                            c0=c1
                            visited[l0][c0] = not([l0,c0] in noeud)
                            if isNextTo([l0,c0],coord_f,self.mine):
                                return True
                    
        return False                          
                
    def agrandirMine(self,l,c): #ajouter une ligne ou une colonne si besoin
        if 0<=c<self.colonnes and 0<=l<self.lignes:
            return l,c
        
        elif 0<=c<self.colonnes: #on ajoute une ligne
            if l<0:
            #on ajoute une ligne en haut
                self.mine.insert(0,[0 for j in range(self.colonnes)])
                self.depart[0]+=1
                for i in range(len(self.arrivee)):
                    self.arrivee[i][0]+=1
                l+=1
            elif l>=self.lignes:
            #on ajoute une ligne en bas
                self.mine.append([0 for j in range(self.colonnes)])
            self.lignes+=1
        
        elif 0<=l<self.lignes: #on ajoute une colonne
            if c<0:
            #on ajoute une colonne a gauche
                for i in range(self.lignes):
                    self.mine[i].insert(0,0)
                self.depart[1]+=1
                for i in range(len(self.arrivee)):
                    self.arrivee[i][1]+=1
                c+=1
            elif c>=self.colonnes:
            #on ajoute une colonne à droite
                for i in range(self.lignes):
                    self.mine[i].append(0)
            self.colonnes+=1
        return l,c
            
#%% Fonctions utiles pour tester les chemins

#vérification de l'existence d'un chemin valide entre deux cases adjacentes
def isValid(M,visited,l0,l1,c0,c1,strong):
    m=M.mine
    test=0
    if (l1 < 0) or (l1 >= M.lignes) or (c1 < 0) or (c1 >= M.colonnes):
        return test
    
    if isinstance(m[l1][c1],CarteChemin):
        if strong:
            c=m[l1][c1].culdesac
        else:
            c=1
            
        if l1==l0 and c1==c0+1:
            test = m[l0][c0].chemins[3]*m[l1][c1].chemins[1]*c
        elif l1==l0 and c1==c0-1:
            test = m[l0][c0].chemins[1]*m[l1][c1].chemins[3]*c
        elif l1==l0+1 and c1==c0:
            test = m[l0][c0].chemins[2]*m[l1][c1].chemins[0]*c
        elif l1==l0-1 and c1==c0:
            test = m[l0][c0].chemins[0]*m[l1][c1].chemins[2]*c

    return test*(not visited[l1][c1])

#------------------

def isNextTo(coord0,coord1,M):
    l0,c0,l1,c1=coord0[0],coord0[1],coord1[0],coord1[1]
    return ( ([l0-1,c0] == [l1,c1] and M[l0][c0].chemins[0] == 1)\
          or ([l0+1,c0] == [l1,c1] and M[l0][c0].chemins[2] == 1)\
          or ([l0,c0-1] == [l1,c1] and M[l0][c0].chemins[1] == 1)\
          or ([l0,c0+1] == [l1,c1] and M[l0][c0].chemins[3] == 1))
 
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        