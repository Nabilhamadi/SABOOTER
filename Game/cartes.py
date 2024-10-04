from abc import ABC, abstractmethod
import os
import random
import time
from .fonctions import restrictedInput

#%%Cartes
class Carte(ABC):
    def __init__(self):pass
    
    @abstractmethod
    def afficherCarte(self): pass

    @abstractmethod
    def jouerCarte(self):pass

    def __str__(self):
        tab=self.afficherCarte()
        s=tab[0]+'\n'+tab[1]+'\n'+tab[2]
        return s
#%% Cartes chemin

class CarteChemin(Carte):
    def __init__(self,chemins):
        super().__init__()
        self.__chemins=chemins
#chemins de la forme [int,int,int,int,str], où les 4 entiers correspondent aux chemins disponibles : 
    # 0 = pas de chemin // 1 = chemin ouvert
#le str correspond au symbole de milieu de carte (+,x,S,G,N)

        self.__culdesac = 0
        if chemins[4] == '+' or chemins[4] == 'S':
            self.__culdesac = 1
#self.culdesac nous permettra de vérifier si la carte permet de construire un chemin valide vers l'arrivée 
#ou si ce chemin est bloqué (culdesac=0 == chemin bloqué)

    # Les properties
    @property
    def chemins( self ) :
        return self.__chemins
    @property
    def culdesac( self ) :
        return self.__culdesac
    @chemins.setter
    def chemins( self, chemins ) :
        if all([(chemins[i]==0 or chemins[i]==1) for i in range(len(chemins))]):
            self.__chemins = chemins
    @culdesac.setter
    def culdesac( self, culdesac ) :
        if culdesac==0 or culdesac == 1:
            self.__culdesac = culdesac


    def afficherCarte(self): 
        c=self.chemins
        l0='( '+c[0]*'|'+(-c[0]+1)*' '+' )'
        l1='('+c[1]*'-'+(-c[1]+1)*' '+c[4]+c[3]*'-'+(-c[3]+1)*' '+')'
        l2='( '+c[2]*'|'+(-c[2]+1)*' '+' )'
        return [l0,l1,l2]
    #afficherCarte retourne les 3 lignes.5colonnes de texte correspondant à la carte, non un affichage à proprement parler
    #elles seront affichées seulement dans les mains des joueurs
    
    def jouerCarte(self,Mine,ligne,colonne):
        
        l,c=Mine.agrandirMine(ligne,colonne)
        #on agrandit la mine si besoin

        if Mine.poserCarte(self,l,c):
            Mine.mine[l][c]=self
            I=[]
            for A in Mine.arrivee:
                if Mine.verifierChemin(Mine.depart,A,strong=True):
                    C,fin = Mine.mine[A[0]][A[1]].revelerCarte()
                    Mine.mine[A[0]][A[1]] = C
                    I.append(Mine.arrivee.index(A))
                    if fin:        
                        print(Mine)
                        return True,True
            for i in I:del Mine.arrivee[i]
            print(Mine)      
            return True, False
        return False, False

    def rotationCarte(self):
    #permet de pivoter une carte de 180°
        a=self.chemins[0]
        b=self.chemins[1]
        c=self.chemins[2]
        d=self.chemins[3]
        e=self.chemins[4]
        return CarteChemin([c,d,a,b,e])
    
#%% Cartes arrivées et départ

class CarteArrivee(CarteChemin):
    def __init__(self,pepite):
        super().__init__([0,0,0,0,'?'])
        self.__pepite=pepite
        paspepite = [CarteChemin([0,1,1,0,'+']),CarteChemin([1,1,0,0,'+'])]
        if self.__pepite==False:
            self.__carteCachee=paspepite[random.randint(0,1)]   
        else:
            self.__carteCachee = CarteChemin([1,1,1,1,'G'])
     
    @property
    def pepite( self ) :
        return self.__pepite
    
    @property
    def carteCachee( self ) :
        return self.__carteCachee
        
    def revelerCarte(self):
        if self.pepite == True:
            return self.carteCachee,True
        else:
            return self.carteCachee,False
        
CarteDepart = CarteChemin([1,1,1,1,'S']) 

#%% Cartes action : Outil

class CarteActionOutil(Carte):
    def __init__(self,status,outil,outil2 = ''):
        super().__init__()
        self.__outil = outil
        self.__outil2 = outil2
        self.__status = status
    
    @property
    def outil( self ) :
        return self.__outil
    @property
    def outil2( self ) :
        return self.__outil2
    @property
    def status( self ) :
        return self.__status
    
    def jouerCarte(self,Joueur):
        if self.status == 'casser':
            Joueur.broken.append(self.outil)
            return True
        elif self.status == 'reparer':
            try:
                Joueur.broken.remove(self.outil)
            except:
                try:
                    Joueur.broken.remove(self.outil2)
                except:
                    print('Ce n est pas le bon outil pour réparer les dégâts :(\n')
                    return False
            return True

    def afficherCarte(self):
        tab=['(ACT)','(   )','(   )']
        if self.status == 'casser':
            tab[1] = '( - )'
        else:
            tab[1] = '( + )'
        if self.outil == 'pioche':
            tab[2] = '( P )'
        elif self.outil == 'lampe':
            tab[2] = '( L )'
        elif self.outil == 'wagon':
            tab[2] = '( W )'
        if self.outil2 == 'pioche':
            tab[2] = tab[2][:3]+'P'+tab[2][4:]
        if self.outil2 == 'lampe':
            tab[2] = tab[2][:3]+'L'+tab[2][4:]
        if self.outil2 == 'wagon':
            tab[2] = tab[2][:3]+'W'+tab[2][4:]
        return tab
        
#%% Cartes éboulement

class CarteEboulement(Carte):
    def __init__(self):
        super().__init__()

    def jouerCarte(self,Mine,ligne=0,colonne=0,input=True):
        if input:
            ligne = int(restrictedInput('Quelle ligne?',0,Mine.lignes-1))
            colonne = int(restrictedInput('Quelle colonne?',0,Mine.colonnes-1))
        if isinstance(Mine.mine[ligne][colonne],CarteChemin) and not isinstance(Mine.mine[ligne][colonne],CarteArrivee) and Mine.mine[ligne][colonne]!=CarteDepart:
            Mine.mine[ligne][colonne]=0
            return True
        else:
            print('Impossible de supprimer une carte ici')
        return False

    def afficherCarte(self):
        return ['(ACT)','(ebo)','(ule)']

#%% Cartes plan secret

class CartePlan(Carte):
    def __init__(self):
        super().__init__()
        
    def jouerCarte(self,Mine):
        s=''
        for i in range(len(Mine.arrivee)):
            s+=str(i)+': '+str(Mine.arrivee[i])+' '
        n=int(restrictedInput('Quelle carte regarder? '+s,0,len(Mine.arrivee)))        
        l=Mine.arrivee[n][0]
        c=Mine.arrivee[n][1]
        input('Attention : cache l ecran pour regarder la carte! Quand tu es prêt appuie sur Entree')
        print(Mine.mine[l][c].carteCachee)
        time.sleep(0.5)
        input('Quand tu es prêt rappuie sur Entree pour effacer la carte')
        os.system('cls' if os.name == 'nt' else 'clear')  
        return True
    
    def afficherCarte(self):
        return ['(ACT)','(pl )','( an)']

#%% Cartes pépites pour attribution des points

class CartePepite(Carte):
    def __init__(self,points):
        super().__init__()
        self.__points = points
     
    @property
    def points( self ) :
        return self.__points
    
    def afficherCarte(self):
        return['(   )','('+self.points*'*'+(3-self.points)*' '+')','(   )']
    
    def jouerCarte(self):
        pass
#%% Mains

class Main:
    def __init__(self,n,Paquet):
    #on crée la main en piochant n cartes au hasard dans le paquet
        self.n=n
        pioche=random.sample(range(len(Paquet)),self.n)
        pioche.sort(reverse=True)
        self.cartes=[]
        for i in pioche:
            self.cartes.append(Paquet[i])
            del Paquet[i]  
            #on enlève les cartes piochées du paquet au fur et à mesure
        
    def __str__(self):
        #afficher les cartes disponibles dans la main du joueur 
        #+ les actions possibles : défausser une carte ou retourner une carte
        
        p='Votre main:\n'
        text1=['     '+str(self.n+1)+'     |','          |','défausser |','          |']
        text2=['    '+str(self.n+2)+'    ','         ',' tourner ','  carte  ']
        for i in range(self.n):
            p+='   '+str(i+1)+'   |'
        p+=text1[0]+text2[0]+'\n'
        for a in range(3):
            p+=' '
            for i in range(self.n):
                p+=self.cartes[i].afficherCarte()[a]+' | '
            p+=text1[a+1]+text2[a+1]+'\n'
        return p
        
            
    def piocher(self,Paquet):
    #piocher une carte dans le paquet
        pioche=random.randint(0,len(Paquet)-1)
        self.cartes.append(Paquet[pioche])
        del Paquet[pioche]
        
class MainPepites(Main):
    def __init__(self,n,Paquet):
        super().__init__(n,Paquet)
        
    def __str__(self):
        #on a créé une classe héritée car on n'affiche pas de la même manière une main de jeu ou de points 
        p=''
        for i in range(self.n):
            p+='   '+str(i+1)+'   |'
        p+='\n'
        for a in range(3):
            p+=' '
            for i in range(self.n):
                p+=self.cartes[i].afficherCarte()[a]+' | '
            p+='\n'
        return p
        
#%% Création du paquet de cartes

#construction du paquet de cartes en ajoutant les cartes en fonction de leur 'chemin'

def createPaquet():
    Paquet = []
    
    #URDL
    for i in range(5):
        Paquet.append(CarteChemin([1,1,1,1,'+']))
    Paquet.append(CarteChemin([1,1,1,1,'x']))
    #URD
    for i in range(5):
        Paquet.append(CarteChemin([1,0,1,1,'+']))
    Paquet.append(CarteChemin([1,0,1,1,'x']))
    #URL
    for i in range(5):
        Paquet.append(CarteChemin([1,1,0,1,'+']))
    Paquet.append(CarteChemin([1,1,0,1,'x']))
    #UR
    for i in range(5):
        Paquet.append(CarteChemin([1,0,0,1,'+']))
    Paquet.append(CarteChemin([1,0,0,1,'x']))
    #UL
    for i in range(4):
        Paquet.append(CarteChemin([1,1,0,0,'+']))
    Paquet.append(CarteChemin([1,1,0,0,'x']))
    #UD
    for i in range(4):
        Paquet.append(CarteChemin([1,0,1,0,'+']))
    Paquet.append(CarteChemin([1,0,1,0,'x']))
    #RL
    for i in range(3):
        Paquet.append(CarteChemin([0,1,0,1,'+']))
    Paquet.append(CarteChemin([0,1,0,1,'x']))
    #U
    Paquet.append(CarteChemin([1,0,0,0,'x']))
    #R
    Paquet.append(CarteChemin([0,0,0,1,'x']))

    #Cartes action : casser/réparer outils
    status=['casser','reparer']
    outils=['pioche','lampe','wagon']
    for s in status:
        for o in outils:
            for i in range(2):
                Paquet.append(CarteActionOutil(s,o))
    for o in outils:
        Paquet.append(CarteActionOutil('casser',o))
    Paquet.append(CarteActionOutil('reparer','pioche','lampe'))
    Paquet.append(CarteActionOutil('reparer','wagon','lampe'))
    Paquet.append(CarteActionOutil('reparer','pioche','wagon'))
    
    #Cartes eboulement
    for i in range(3):
        Paquet.append(CarteEboulement())
        
    #Cartes plan secret
    for i in range(6):
        Paquet.append(CartePlan())
                    
    return Paquet

def createDeckPepite():
    DeckPepite=[]
    for i in range(16):
        DeckPepite.append(CartePepite(1))
    for i in range(8):
        DeckPepite.append(CartePepite(2))
    for i in range(4):
        DeckPepite.append(CartePepite(3))
        
    return DeckPepite






















