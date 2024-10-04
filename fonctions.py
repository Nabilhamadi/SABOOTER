#%% Fonction pour restreindre l'input dans une plage de valeurs d'entiers

def restrictedInput(message,a,b): #on restreint la valeur de l'input entre les entiers a et b compris
    test = False
    while test == False:
        res = input(message)
        if res.lstrip('-').isdigit() == False:
            print('Merci de choisir un entier entre '+str(a)+' et '+str(b))
        else:
            r=int(res)
            if (r <a or r >b) == True:
                print('Merci de choisir un entier entre'+str(a)+' et '+str(b))
            else:
                test=True          
    return r
            

#%% Définition des rôles en fonction du nombre de joueurs

def Roles(N):
    if N==3:
        R=['Saboteur']+3*['Chercheur']
    elif N==4:
        R=['Saboteur']+4*['Chercheur']
    elif N==5:
        R=2*['Saboteur']+4*['Chercheur']
    elif N==6:
        R=2*['Saboteur']+5*['Chercheur']
    elif N==7:
        R=3*['Saboteur']+5*['Chercheur']
    elif N==8:
        R=3*['Saboteur']+6*['Chercheur']
    elif N==9:
        R=3*['Saboteur']+7*['Chercheur']
    elif N==10:
        R=4*['Saboteur']+7*['Chercheur']
    return R


#%% Fonction pour calculer et afficher le vainqueur

def classement(Joueurs):
    print('Classement final :\n')
    names=[]
    points=[]
    for J in Joueurs:
        names.append(J.nom)
        points.append(J.points)
    for item in sorted(zip(points,names),reverse=True):
        print(item)

                    
                
#%% Fonction pour calculer la distance de Manhattan entre deux points du plateau

def manhattan(coord1,coord2):
    return abs(coord2[0]-coord1[0])+abs(coord2[1]-coord1[1])
                
                
                
