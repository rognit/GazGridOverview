import pandas as pd

# Lire le fichier CSV
df = pd.read_csv('resources/population2019.csv')

# Compter le nombre de lignes
nombre_de_lignes = len(df)

# Afficher le nombre de lignes
print(f"Le nombre de lignes dans le fichier est : {nombre_de_lignes}")

#Le nombre de lignes dans le fichier est : 2 287 884