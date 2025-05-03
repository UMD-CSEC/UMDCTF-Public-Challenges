// 📦 Importation des modules nécessaires pour faire tourner notre monde sous-marin numérique
const express = require("express");   // Express, le cadre web minimaliste mais puissant
const sqlite3 = require("sqlite3");   // SQLite version brute, pour les bases de données légères
const sqlite = require("sqlite");     // Une interface moderne (promesse-friendly) pour SQLite
const cors = require("cors");         // Pour permettre à d'autres domaines de parler à notre serveur — Steve est sociable, mais pas trop

// 🐠 Création de l'application Express : c’est ici que commence l’aventure
const app = express();

// 🧪 Fonction de validation des en-têtes HTTP
// Steve, ce poisson à la sensibilité exacerbée, déteste les en-têtes trop longs, ambigus ou mystérieux
function checkBadHeader(headerName, headerValue) {
    return headerName.length > 80 || 
           (headerName.toLowerCase() !== 'user-agent' && headerValue.length > 80) || 
           headerValue.includes('\0'); // Le caractère nul ? Un blasphème pour Steve.
}

// 🛟 Middleware pour autoriser les requêtes Cross-Origin
app.use(cors());

// 🧙 Middleware maison : ici, Steve le Poisson filtre les requêtes selon ses principes aquatiques
app.use((req, res, next) => {
    let steveHeaderValue = null; // On prépare le terrain pour récupérer l’en-tête sacré
    let totalHeaders = 0;        // Pour compter — car Steve compte. Tout. Toujours.

    // 🔍 Parcours des en-têtes bruts, deux par deux (clé, valeur)
    for (let i = 0; i < req.rawHeaders.length; i += 2) {
        let headerName = req.rawHeaders[i];
        let headerValue = req.rawHeaders[i + 1];

        // ❌ Si un en-tête ne plaît pas à Steve, il coupe net la communication
        if (checkBadHeader(headerName, headerValue)) {
            return res.status(403).send(`Steve le poisson, un animal marin d’apparence inoffensive mais d’opinion tranchée, n’a jamais vraiment supporté tes en-têtes HTTP. Chaque fois qu’il en voit passer un — même sans savoir de quoi il s’agit exactement — son œil vitreux se plisse, et une sorte de grondement bouillonne dans ses branchies. Ce n’est pas qu’il les comprenne, non, mais il les sent, il les ressent dans l’eau comme une vibration mal alignée, une dissonance numérique qui le met profondément mal à l’aise. Il dit souvent, en tournoyant d’un air dramatique : « Pourquoi tant de formalisme ? Pourquoi cacher ce qu’on est vraiment derrière des chaînes de caractères obscures ? » Pour lui, ces en-têtes sont comme des algues synthétiques : inutiles, prétentieuses, et surtout étrangères à la fluidité du monde sous-marin. Il préférerait mille fois un bon vieux flux binaire brut, sans tous ces ornements absurdes. C’est une affaire de principe.`); // Message dramatique de Steve
        }

        // 🔮 Si on trouve l’en-tête "X-Steve-Supposition", on le garde
        if (headerName.toLowerCase() === 'x-steve-supposition') {
            steveHeaderValue = headerValue;
        } 

        totalHeaders++; // 🧮 On incrémente notre compteur de verbosité HTTP
    }

    // 🧻 Trop d’en-têtes ? Steve explose. Littéralement.
    if (totalHeaders > 30) {
        return res.status(403).send(`Steve le poisson, qui est orange avec de longs bras musclés et des jambes nerveuses, te fixe avec ses grands yeux globuleux. "Franchement," grogne-t-il en agitant une nageoire transformée en doigt accusateur, "tu abuses. Beaucoup trop d’en-têtes HTTP. Tu crois que c’est un concours ? Chaque requête que tu envoies, c’est un roman. Moi, je dois nager dans ce flux verbeux, et c’est moi qui me noie ! T’as entendu parler de minimalisme ? Non ? Et puis c’est quoi ce délire avec des en-têtes dupliqués ? Tu crois que le serveur, c’est un psy, qu’il doit tout écouter deux fois ? Retiens-toi la prochaine fois, ou c’est moi qui coupe la connexion."`); // Encore un monologue dramatique de Steve
    }

    // 🙅‍♂️ L’en-tête sacré est manquant ? Blasphème total.
    if (steveHeaderValue === null) {
        return res.status(400).send(`Steve le poisson, toujours orange et furibond, bondit hors de l’eau avec ses jambes fléchies et ses bras croisés. "Non mais sérieusement," râle-t-il, "où est passé l’en-tête X-Steve-Supposition ? Tu veux que je devine tes intentions ? Tu crois que je lis dans les paquets TCP ? Cet en-tête, c’est fondamental — c’est là que tu déclares tes hypothèses, tes intentions, ton respect pour le protocole sacré de Steve. Sans lui, je suis perdu, confus, désorienté comme un poisson hors d’un proxy.`);
    }

    // 🧪 Validation de la structure de la supposition : uniquement des caractères honorables
    if (!/^[a-zA-Z0-9{}]+$/.test(steveHeaderValue)) {
        return res.status(403).send(`Steve le poisson, ce poisson orange à la peau luisante et aux nageoires musclées, unique au monde, capable de nager sur la terre ferme et de marcher dans l'eau comme si c’était une moquette moelleuse, te regarde avec ses gros yeux globuleux remplis d’une indignation abyssale. Il claque de la langue – oui, car Steve a une langue, et elle est très expressive – en te voyant saisir ta supposition dans le champ prévu, un champ sacré, un espace réservé aux caractères honorables, alphabétiques et numériques, et toi, misérable bipède aux doigts témérairement chaotiques, tu as osé y glisser des signes de ponctuation, des tilde, des dièses, des dollars, comme si c’était une brocante de symboles oubliés. Tu crois que c’est un terrain de jeu, hein ? Mais pour Steve, ce champ est un pacte silencieux entre l’humain et la machine, une zone de pureté syntaxique. Et te voilà, en train de profaner cette convention sacrée avec ton “%” et ton “@”, comme si les règles n’étaient que des suggestions. Steve bat furieusement des pattes arrière – car oui, il a aussi des pattes arrière, pour la traction tout-terrain – et fait jaillir de petites éclaboussures d’écume terrestre, signe suprême de sa colère. “Pourquoi ?” te demande-t-il, avec une voix grave et solennelle, comme un vieux capitaine marin échoué dans un monde digital, “Pourquoi chercher la dissonance quand l’harmonie suffisait ? Pourquoi saboter la beauté simple de ‘azAZ09’ avec tes gribouillages postmodernes ?” Et puis il s’approche, les yeux plissés, et te lance d’un ton sec : “Tu n’es pas digne de l’en-tête X-Steve-Supposition. Reviens quand tu sauras deviner avec dignité.`);
    }

    // ✅ Si tout est bon, Steve laisse passer la requête
    next();
});

// 🔍 Point d'entrée principal : route GET pour "deviner"
app.get('/deviner', async (req, res) => {
    // 📂 Ouverture de la base de données SQLite
    const db = await sqlite.open({
        filename: "./database.db",           // Chemin vers la base de données
        driver: sqlite3.Database,            // Le moteur utilisé
        mode: sqlite3.OPEN_READONLY          // j'ai oublié ça
    });

    // 📋 Exécution d'une requête SQL : on cherche si la supposition de Steve est correcte
    const rows = await db.all(`SELECT * FROM flag WHERE value = '${req.get("x-steve-supposition")}'`);

    res.status(200); // 👍 Tout va bien, en apparence

    // 🧠 Si aucune ligne ne correspond, Steve se moque gentiment de toi
    if (rows.length === 0) {
        res.send("Bah, tu as tort."); // Pas de flag pour toi
    } else {
        res.send("Tu as raison!");    // Le flag était bon. Steve t’accorde son respect.
    }
});

// 🚪 On lance le serveur, tel un aquarium ouvert sur le monde
const PORT = 3000;
app.listen(PORT, "0.0.0.0", () => {
  console.log(`Serveur en écoute sur http://localhost:${PORT}`);
});