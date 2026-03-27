-- Table pour stocker les documents de brevets bruts
CREATE TABLE IF NOT EXISTS Brevets (
    id_brevet INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_fichier TEXT UNIQUE NOT NULL, -- ex: CN110675118A_Description
    domaine TEXT, -- ex: Connectivité, AI_Blockchain
    type_document TEXT, -- 'Description' ou 'Revendications'
    contenu_texte TEXT NOT NULL -- Le texte complet extrait du Word
);

-- Table pour l'étape S1 : Extraire et stocker les points d'innovation [cite: 172, 175]
CREATE TABLE IF NOT EXISTS Points_Innovation (
    id_innovation INTEGER PRIMARY KEY AUTOINCREMENT,
    id_brevet INTEGER,
    description_point TEXT NOT NULL,
    FOREIGN KEY (id_brevet) REFERENCES Brevets(id_brevet)
);

-- Table pour l'étape S2 : Affiner et stocker les mots-clés [cite: 173, 175]
CREATE TABLE IF NOT EXISTS Mots_Cles (
    id_mot INTEGER PRIMARY KEY AUTOINCREMENT,
    id_innovation INTEGER,
    mot_cle TEXT NOT NULL,
    FOREIGN KEY (id_innovation) REFERENCES Points_Innovation(id_innovation)
);