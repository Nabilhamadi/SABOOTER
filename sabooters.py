from jeu import *

#%% Definition des fonctions permettant de jouer une manche

def jouerManche(Joueurs):
    #réinitialisation du plateau de jeu et du paquet de cartes             
    M=Mine()
    
    Paquet = createPaquet()
    last=''
                 
    #distribution des roles
    R=Roles(len(Joueurs))
    print('Nous allons distribuer les rôles')
    print('')
    time.sleep(0.5)
    for J in Joueurs:
        #assignement du role
        r=random.randint(0,len(R)-1)
        J.role=R[r]
        del R[r] #on enlève son rôle de la liste des rôles disponibles
        
        #affichage
        if not isinstance(J,IA):
            input(J.nom +', quand tu es prêt à découvrir ton role appuie sur Entree')
            print('Tu es '+J.role)
            time.sleep(0.5)
            input(J.nom +', mémorise ton role et appuie sur Entree de nouveau avant de donner l ordinateur au joueur suivant')
            os.system('cls' if os.name == 'nt' else 'clear')                   
    
    #distribution des cartes
    #nombre de cartes en fonction du nombre de joueurs
    N=len(Joueurs)
    if 3<=N<=5:
        n=6
    elif 6<=N<=7:
        n=5
    elif 8<=N<=10:
        n=4
    for J in Joueurs:
        J.main=Main(n,Paquet)
        
    #jeu
    fin = False
    while fin==False:
        for j in range(len(Joueurs)):
            J=Joueurs[j]
            print(M)
            time.sleep(0.5)
            if J.main.n>0:
                fin,last = J.jouer(Joueurs,M,Paquet)
            else:
                print('Pioche vide')
            
            #on garde en mémoire le dernier joueur ayant joué une carte
            if last:
                dernierjoueur = j
                
            #si l'arrivee est atteinte les chercheurs ont gagné
            if fin:
                win='Chercheur'
                print('Bravo, les chercheurs d or ont gagné')
                break
            
            #si les cartes sont épuisées les saboteurs ont gagné
            if all([Joueurs[j].main.n == 0 for j in range(N)]) and len(Paquet)==0:
                print('Bravo, les saboteurs ont gagné')
                win='Saboteur'
                fin=True
                break

    return win,dernierjoueur

def distribPoints(win,dernierjoueur,Joueurs,DeckPepites):
    if win == 'Chercheur':
        #piocher une main de cartes pépites
        Reward = MainPepites(len(Joueurs),DeckPepites)

        # faire choisir aux joueurs les cartes en commencant par le joueur ayant joué la dernière carte
        while Reward.n > 0:    
            for j in range(len(Joueurs)):
                newj = (j+dernierjoueur)%len(Joueurs)   
                if Joueurs[newj].role == win:
                    if isinstance(Joueurs[newj],IA):
                        pts=0
                    else:
                        print(Joueurs[newj].nom+', voici les points disponibles\n'+str(Reward))
                        pts = int(restrictedInput('Quelle carte souhaitez-vous prendre?',1,len(Reward.cartes)))-1
                    Joueurs[newj].points += Reward.cartes[pts].points
                    del Reward.cartes[pts]
                    Reward.n -=1
                    if Reward.n == 0:
                        break
    
    if win == 'Saboteur':
        #on compte le nombre de saboteurs (il y a une partie aléatoire dans le choix des 
        #roles donc pas toujours le même nombre pour un nb de joueurs identique)
        n_sab =0
        for J in Joueurs:
            if J.role == 'Saboteur':
                n_sab+=1
        if n_sab == 1:
            pts = 4
        elif 2<=n_sab<4:
            pts = 3
        elif n_sab == 4:
            pts = 2
        
        for J in Joueurs:
            if J.role == win:
                print(J.nom+' vous gagnez '+str(pts)+' points:')
                P=0
                while P!=pts:
                    r=random.randint(0,len(DeckPepites)-1)
                    if P+DeckPepites[r].points <=pts:
                        P+=DeckPepites[r].points
                        print(DeckPepites[r])
                        del DeckPepites[r]
                J.points += pts 
    
    # affichage des points
    s='----\nPoints totaux'
    for J in Joueurs:
        s+='\n'+J.nom+' : '+str(J.points)
    s+='\n----'
    print(s)

def Regles():
    print('Bienvenue dans Sabooteur!')
    print('\n')
    print('Avant de commencer, voici quelques points de règles:')
    print('- Le but du jeu si vous êtes chercheur d or est de créér un tunnel ininterrompu entre la carte de départ et les cartes d arrivée afin de trouver la pépite (symbolisée par un G en son centre) qui se cache sous l une des trois cartes')
    print('- Le but du jeu si vous êtes saboteur est d empecher les chercheurs d acceder à la pépite, jusqu à ce qu il n y ait plus de carte à jouer')
    print('\n')
    print(5*'-'+'Détail des cartes'+5*'-')
    print('- Les cartes chemin servent à construire le tunnel, lorsqu elles présentent un + en leur centre le tunnel est accessible:\n'+str(CarteChemin([1,1,1,1,'+']))\
        +'\nlorsqu elles présentent un x le chemin est un cul de sac:\n'+str(CarteChemin([1,1,1,1,'x']))\
        +'\nOn ne peut poser une carte qu à côté d une autre carte et ses chemins doivent se connecter avec ceux des cartes déjà posées. Il est également impossible de poursuivre un chemin qui n est plus relié à la carte de départ.'\
            +' Le plateau de jeu est dynamique: vous pouvez l agrandir autant que vous le voulez en posant une carte sur une nouvelle ligne ou une nouvelle colonne')
    print('- Les cartes action vous permettent d effectuer des actions spéciales:\
        \nLes cartes éboulement permettent d enlever une carte du plateau\n'+str(CarteEboulement())\
        +'\nLes cartes plan vous permettent de regarder le dessous des cartes arrivée pour savoir où se cache la pépite\n'+str(CartePlan())\
        +'\nLes cartes outil vous permettent de casser (-) ou réparer (+) vos outils (lampe:L, wagon:W et pioche:P) ou ceux des autres joueurs. Si un outil est cassé le joueur ne peut pas poser de carte chemin. Par exemple la carte suivante permet de casser une pioche\n'+str(CarteActionOutil('casser','pioche')))

    input('Si vous êtes prêts à jouer, appuyez sur Entrée!')

#%% Creation des joueurs

Regles()

N=int(restrictedInput('Combien de joueurs? Sabooteurs se joue de 3 à 10 joueurs',3,10))
Joueurs=[]
DeckPepites = createDeckPepite()


for i in range(N):
    nom,ia=input('Entrez le nom du joueur '+str(i+1)+' et son statut (Joueur : 0 / IA : 1), séparés par un espace ').split()
    if ia=='1':
        Joueurs.append(IA(nom))
    else:
        Joueurs.append(Joueur(nom))

manches =range(int(restrictedInput('Combien de manches souhaitez-vous jouer? (partie normale : 3 manches)',1,5)))

#%% Jeu

for i in manches:
    
    print('.\nMANCHE N°'+str(i+1)+'\n.')
    
    #on réinitialise les objets cassés
    for J in Joueurs:
        J.broken=[]
    
    win,dernierjoueur = jouerManche(Joueurs)
    distribPoints(win,dernierjoueur,Joueurs,DeckPepites)
    Joueurs = Joueurs[dernierjoueur:]+Joueurs[:dernierjoueur]
        

classement(Joueurs)
