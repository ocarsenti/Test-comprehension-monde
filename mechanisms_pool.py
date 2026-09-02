"""
Pool fixe des mécanismes du jeu.

Fichier gravé dans le marbre (voir memoire projet) : le LLM (matcher.py,
dresser.py) ne fait JAMAIS que choisir un id existant ici et l'habiller
avec l'actualité du jour. Il ne peut ni inventer un mécanisme, ni modifier
`explanation`/`source`.

12 catégories, ~4 mécanismes chacune. `connects_to` porte de vraies
relations causales (pas de la simple proximité thématique) — c'est ce
graphe qui alimente l'écran "Ta carte" et les messages de réactivation
croisée.
"""

from dataclasses import dataclass, field
from enum import Enum


class MechanismType(Enum):
    FACT = "FACT"
    DILEMMA = "DILEMMA"


class Category(Enum):
    ECONOMIQUE = "économique"
    INSTITUTIONNEL = "institutionnel"
    COMMERCE = "commerce"
    DEMOGRAPHIE_MIGRATION = "démographie/migration"
    GEOPOLITIQUE = "géopolitique"
    GEOLOGIQUE_CLIMATIQUE = "géologique/climatique"
    VULNERABILITE = "vulnérabilité"
    BIOLOGIQUE = "biologique"
    ECOLOGIQUE = "écologique"
    TECHNOLOGIQUE = "technologique"
    PSYCHOLOGIQUE = "psychologique"
    JURIDIQUE = "juridique"


@dataclass
class Mechanism:
    id: str
    category: Category
    label: str
    base_situation: str
    explanation: str
    source: str
    mechanism_type: MechanismType
    connects_to: list[str] = field(default_factory=list)


FULL_POOL: list[Mechanism] = [

    # ── ÉCONOMIQUE ──────────────────────────────────────────────
    Mechanism(
        id="smic_revalorisation_automatique",
        category=Category.ECONOMIQUE,
        label="Revalorisation automatique du SMIC",
        base_situation="Le salaire minimum augmente sans aucun vote, dès que l'inflation ressentie par les ménages modestes dépasse un seuil.",
        explanation="Une règle automatique déclenche la hausse dès que l'indice des prix à la consommation des 20% de ménages les plus modestes dépasse 2% par rapport à la dernière revalorisation — aucune décision politique n'est nécessaire.",
        source="Article L3231-4 du Code du travail français.",
        mechanism_type=MechanismType.FACT,
        connects_to=["nominal_vs_reel"],
    ),
    Mechanism(
        id="nominal_vs_reel",
        category=Category.ECONOMIQUE,
        label="Valeur nominale vs valeur réelle",
        base_situation="Un montant qui augmente en apparence peut correspondre à un pouvoir d'achat stable, voire en baisse.",
        explanation="Une hausse nominale (en euros affichés) ne dit rien du pouvoir d'achat réel tant qu'elle n'est pas comparée à l'inflation sur la même période — un salaire ou une pension peuvent progresser en façade et reculer en réalité.",
        source="Mécanisme économique général (comptabilité nationale).",
        mechanism_type=MechanismType.FACT,
        connects_to=["smic_revalorisation_automatique", "inflation_importee"],
    ),
    Mechanism(
        id="banque_centrale_taux",
        category=Category.ECONOMIQUE,
        label="Relèvement des taux directeurs",
        base_situation="Une banque centrale relève ses taux pour freiner l'inflation, au prix d'un crédit plus cher pour tous.",
        explanation="En rendant le crédit plus cher, la banque centrale ralentit délibérément la consommation et l'investissement — l'objectif est de faire baisser la demande, donc les prix, au prix d'une croissance plus faible à court terme.",
        source="Mécanisme de politique monétaire standard (type BCE/Fed).",
        mechanism_type=MechanismType.FACT,
        connects_to=["dette_souveraine", "independance_banque_centrale"],
    ),
    Mechanism(
        id="inflation_importee",
        category=Category.ECONOMIQUE,
        label="Inflation importée",
        base_situation="Les prix intérieurs grimpent alors que rien n'a changé dans le pays lui-même.",
        explanation="Quand une monnaie se déprécie ou qu'une matière première mondiale flambe, le renchérissement se répercute automatiquement sur les prix intérieurs, sans qu'aucune décision domestique n'en soit la cause.",
        source="Mécanisme macroéconomique standard (transmission des prix mondiaux).",
        mechanism_type=MechanismType.FACT,
        connects_to=["nominal_vs_reel", "choc_matiere_premiere"],
    ),
    Mechanism(
        id="dette_souveraine",
        category=Category.ECONOMIQUE,
        label="Coût de la dette souveraine",
        base_situation="Un État emprunte plus cher du jour au lendemain, sans avoir rien changé à son budget.",
        explanation="Le taux auquel un État emprunte reflète la confiance des marchés dans sa capacité à rembourser — une dégradation de notation ou une hausse générale des taux renchérit mécaniquement le coût de toute nouvelle dette, y compris pour financer des dépenses déjà votées.",
        source="Mécanisme des marchés obligataires souverains.",
        mechanism_type=MechanismType.FACT,
        connects_to=["banque_centrale_taux", "vieillissement_demographique"],
    ),

    # ── INSTITUTIONNEL ──────────────────────────────────────────
    Mechanism(
        id="veto_unanimite_conseil_ue",
        category=Category.INSTITUTIONNEL,
        label="Unanimité et droit de veto au Conseil de l'UE",
        base_situation="Un pays bloque une décision européenne sur un sujet, pour obtenir une concession sur un tout autre sujet.",
        explanation="Certaines décisions du Conseil de l'Union européenne — sanctions, fiscalité, politique étrangère — exigent l'unanimité des 27 pays membres. N'importe lequel peut donc bloquer un vote, même sans lien direct avec le fond, pour l'utiliser comme monnaie d'échange ailleurs.",
        source="Traités européens — règle de l'unanimité au Conseil.",
        mechanism_type=MechanismType.FACT,
        connects_to=["vote_trilogue_delai"],
    ),
    Mechanism(
        id="vote_trilogue_delai",
        category=Category.INSTITUTIONNEL,
        label="Trilogue européen et délai de mise en œuvre",
        base_situation="Un texte européen est \"adopté\" mais ne produit ses effets que des années plus tard.",
        explanation="L'adoption d'un règlement européen suit une négociation à trois (Parlement, Conseil, Commission) puis prévoit presque toujours une période de transition avant application réelle — le vote médiatisé et l'entrée en vigueur effective sont deux moments distincts, parfois séparés de plusieurs années.",
        source="Procédure législative ordinaire de l'Union européenne.",
        mechanism_type=MechanismType.FACT,
        connects_to=["veto_unanimite_conseil_ue", "referendum_ratification"],
    ),
    Mechanism(
        id="cbam_dilemme_strategique",
        category=Category.INSTITUTIONNEL,
        label="Arbitrage décarbonation vs statu quo (CBAM)",
        base_situation="Une taxe carbone aux frontières impose un choix stratégique sans réponse garantie d'avance.",
        explanation="Décarboner tout de suite coûte cher et certain ; ne rien faire expose à un risque croissant mais incertain dans son ampleur et son calendrier. Aucune des deux voies n'est \"la bonne réponse\" universelle — l'issue dépend de décisions politiques futures.",
        source="Règlement (UE) 2023/956 — mécanisme d'ajustement carbone aux frontières.",
        mechanism_type=MechanismType.DILEMMA,
        connects_to=["choc_matiere_premiere"],
    ),
    Mechanism(
        id="independance_banque_centrale",
        category=Category.INSTITUTIONNEL,
        label="Indépendance de la banque centrale",
        base_situation="Un gouvernement ne peut pas ordonner à sa banque centrale de baisser les taux, même en pleine crise politique.",
        explanation="Le statut d'indépendance protège la banque centrale des pressions politiques de court terme — l'objectif est d'empêcher qu'un gouvernement finance ses dépenses en imprimant de la monnaie, au prix de devoir composer avec une politique monétaire qu'il ne contrôle pas.",
        source="Mécanisme institutionnel standard (type statut BCE/Fed).",
        mechanism_type=MechanismType.FACT,
        connects_to=["banque_centrale_taux"],
    ),
    Mechanism(
        id="referendum_ratification",
        category=Category.INSTITUTIONNEL,
        label="Ratification par référendum",
        base_situation="Un accord négocié pendant des années peut être bloqué par un seul vote populaire dans un seul pays.",
        explanation="Certains traités internationaux ou européens exigent une ratification nationale, parfois par référendum — un résultat négatif dans un seul pays peut suspendre ou faire échouer un accord conclu par tous les autres.",
        source="Mécanisme constitutionnel de ratification (variable selon les pays).",
        mechanism_type=MechanismType.FACT,
        connects_to=["vote_trilogue_delai"],
    ),

    # ── COMMERCE ────────────────────────────────────────────────
    Mechanism(
        id="droits_douane_guerre_commerciale",
        category=Category.COMMERCE,
        label="Répercussion d'un droit de douane",
        base_situation="Un pays impose un droit de douane élevé sur des produits importés d'un partenaire commercial.",
        explanation="Face à un droit de douane, une entreprise importatrice répercute typiquement une partie du surcoût sur ses prix et/ou cherche un fournisseur alternatif — la rétorsion du pays visé suit souvent, comme levier de négociation.",
        source="Mécanisme standard de politique commerciale (droits de douane).",
        mechanism_type=MechanismType.FACT,
        connects_to=["repercussion_transport_prix", "substitution_fournisseur", "sanctions_economiques_ricochet"],
    ),
    Mechanism(
        id="repercussion_transport_prix",
        category=Category.COMMERCE,
        label="Répercussion d'un coût de transport",
        base_situation="Un blocage ou un renchérissement du fret fait grimper le prix final d'un produit, loin du lieu du blocage.",
        explanation="Le coût du transport est intégré au prix final à chaque étape de la chaîne — un blocage portuaire, une hausse du carburant ou un détour de route se répercute mécaniquement jusqu'au consommateur, même sans lien apparent avec le produit lui-même.",
        source="Mécanisme standard de chaîne logistique.",
        mechanism_type=MechanismType.FACT,
        connects_to=["droits_douane_guerre_commerciale", "choc_matiere_premiere", "couloir_maritime_strategique"],
    ),
    Mechanism(
        id="substitution_fournisseur",
        category=Category.COMMERCE,
        label="Substitution de fournisseur",
        base_situation="Une entreprise change brutalement de partenaire commercial suite à une contrainte extérieure.",
        explanation="Quand un fournisseur devient trop coûteux ou trop risqué (droit de douane, sanction, rupture politique), une entreprise cherche un substitut — au prix d'une renégociation, d'une perte de qualité ou d'un délai, rarement sans coût.",
        source="Mécanisme standard de gestion de chaîne d'approvisionnement.",
        mechanism_type=MechanismType.FACT,
        connects_to=["droits_douane_guerre_commerciale"],
    ),
    Mechanism(
        id="embargo_contournement",
        category=Category.COMMERCE,
        label="Contournement d'un embargo",
        base_situation="Un produit sous embargo continue de circuler, via un pays tiers qui sert d'intermédiaire.",
        explanation="Un embargo bilatéral n'empêche pas un flux de transiter par un pays tiers non soumis à la même restriction — le volume de commerce de ce pays intermédiaire grimpe alors de façon disproportionnée, signe indirect du contournement.",
        source="Mécanisme standard de contournement des sanctions commerciales.",
        mechanism_type=MechanismType.FACT,
        connects_to=["extraterritorialite_droit", "couloir_maritime_strategique"],
    ),

    # ── DÉMOGRAPHIE / MIGRATION ─────────────────────────────────
    Mechanism(
        id="vieillissement_demographique",
        category=Category.DEMOGRAPHIE_MIGRATION,
        label="Vieillissement démographique",
        base_situation="Un système de retraite ou de santé se tend financièrement sans qu'aucune réforme n'ait changé les règles.",
        explanation="Quand le rapport entre actifs cotisants et retraités se dégrade année après année, les dépenses sociales augmentent mécaniquement à règles inchangées — la pression budgétaire vient de la structure de la population, pas d'une décision politique.",
        source="Mécanisme démographique structurel.",
        mechanism_type=MechanismType.FACT,
        connects_to=["dette_souveraine"],
    ),
    Mechanism(
        id="remittances_developpement",
        category=Category.DEMOGRAPHIE_MIGRATION,
        label="Transferts de fonds des migrants (remittances)",
        base_situation="L'économie d'un pays pauvre dépend plus de l'argent envoyé par sa diaspora que de son aide internationale.",
        explanation="Dans de nombreux pays en développement, les sommes envoyées par les travailleurs expatriés à leur famille dépassent en volume l'aide publique au développement reçue — une crise économique dans le pays d'accueil des migrants se répercute donc directement sur le pays d'origine.",
        source="Mécanisme économique standard (Banque mondiale, données remittances).",
        mechanism_type=MechanismType.FACT,
        connects_to=["crise_accueil_migratoire"],
    ),
    Mechanism(
        id="exode_rural",
        category=Category.DEMOGRAPHIE_MIGRATION,
        label="Exode rural et urbanisation accélérée",
        base_situation="Une ville double de population en une décennie sans que ses infrastructures suivent.",
        explanation="Quand les opportunités économiques se concentrent en ville, la population rurale s'y déplace plus vite que la capacité des infrastructures (logement, eau, transport) à absorber cet afflux — d'où des quartiers informels qui se construisent en dehors de toute planification.",
        source="Mécanisme démographique standard (transition urbaine).",
        mechanism_type=MechanismType.FACT,
        connects_to=["habitat_informel_risque"],
    ),
    Mechanism(
        id="crise_accueil_migratoire",
        category=Category.DEMOGRAPHIE_MIGRATION,
        label="Arbitrage capacité d'accueil vs urgence humanitaire",
        base_situation="Un afflux migratoire soudain met un pays face à un choix sans bonne réponse évidente.",
        explanation="Accueillir au-delà de la capacité d'intégration crée des tensions sociales et budgétaires ; refuser expose à un coût humain et à un report de la pression sur d'autres pays. Aucune des deux options n'est universellement \"la bonne\" — l'équilibre dépend de choix politiques et de moyens disponibles.",
        source="Mécanisme institutionnel standard (politique migratoire).",
        mechanism_type=MechanismType.DILEMMA,
        connects_to=["remittances_developpement"],
    ),

    # ── GÉOPOLITIQUE ────────────────────────────────────────────
    Mechanism(
        id="sanctions_economiques_ricochet",
        category=Category.GEOPOLITIQUE,
        label="Effet de ricochet des sanctions économiques",
        base_situation="Des sanctions visant un pays touchent en premier lieu les entreprises et citoyens d'un pays tiers, allié de celui qui les impose.",
        explanation="Une sanction économique coupe des flux commerciaux ou financiers dans les deux sens — les entreprises du pays qui sanctionne perdent aussi un débouché ou un fournisseur, ce qui explique pourquoi les sanctions les plus dures s'accompagnent souvent de mesures de compensation interne.",
        source="Mécanisme standard de sanctions économiques internationales.",
        mechanism_type=MechanismType.FACT,
        connects_to=["droits_douane_guerre_commerciale", "alliance_defense_collective"],
    ),
    Mechanism(
        id="alliance_defense_collective",
        category=Category.GEOPOLITIQUE,
        label="Clause de défense collective",
        base_situation="Une attaque contre un seul pays membre d'une alliance militaire engage automatiquement tous les autres.",
        explanation="Une clause de défense mutuelle (type article 5 de l'OTAN) transforme une agression bilatérale en engagement collectif — l'objectif est de rendre l'attaque d'un membre trop coûteuse pour être tentée, au prix d'un risque d'escalade partagé par tous les signataires.",
        source="Mécanisme standard des traités de défense collective.",
        mechanism_type=MechanismType.FACT,
        connects_to=["sanctions_economiques_ricochet"],
    ),
    Mechanism(
        id="couloir_maritime_strategique",
        category=Category.GEOPOLITIQUE,
        label="Verrou d'un couloir maritime stratégique",
        base_situation="Un incident dans un détroit étroit fait grimper le prix de l'énergie à l'autre bout du monde.",
        explanation="Une part disproportionnée du commerce mondial (pétrole, conteneurs) transite par un petit nombre de détroits ou canaux — leur blocage, même bref, renchérit immédiatement le fret et les prix de l'énergie bien au-delà de la zone concernée.",
        source="Mécanisme standard de géographie du commerce maritime mondial.",
        mechanism_type=MechanismType.FACT,
        connects_to=["embargo_contournement", "repercussion_transport_prix"],
    ),
    Mechanism(
        id="course_influence_regionale",
        category=Category.GEOPOLITIQUE,
        label="Arbitrage entre puissances rivales",
        base_situation="Un petit pays doit choisir son camp entre deux grandes puissances qui se disputent son influence, sans option neutre garantie sans coût.",
        explanation="Se rapprocher d'une puissance apporte des financements ou une protection immédiats, au prix d'une dépendance et d'une hostilité de l'autre camp ; rester neutre évite de choisir, mais prive des deux soutiens. Il n'y a pas d'issue sans compromis, seulement des paris différents.",
        source="Mécanisme géopolitique standard (compétition d'influence régionale).",
        mechanism_type=MechanismType.DILEMMA,
        connects_to=["desinformation_viralite"],
    ),

    # ── GÉOLOGIQUE / CLIMATIQUE ─────────────────────────────────
    Mechanism(
        id="variabilite_mousson",
        category=Category.GEOLOGIQUE_CLIMATIQUE,
        label="Variabilité de l'intensité de la mousson",
        base_situation="Une région connaît une catastrophe liée aux pluies presque chaque année, mais avec une intensité très différente d'une fois sur l'autre.",
        explanation="La mousson est un système de pluie saisonnier récurrent et prévisible dans son principe — c'est son intensité, variable d'une année à l'autre selon des facteurs océaniques et atmosphériques, qui fait la différence entre une saison normale et une catastrophe.",
        source="Mécanisme climatologique général (systèmes de mousson).",
        mechanism_type=MechanismType.FACT,
        connects_to=["vulnerabilite_differenciee_catastrophe", "secheresse_recurrente"],
    ),
    Mechanism(
        id="subduction_sismique",
        category=Category.GEOLOGIQUE_CLIMATIQUE,
        label="Zone de subduction et récurrence sismique",
        base_situation="Une région subit des séismes réguliers, dont on sait qu'ils reviendront, sans savoir précisément quand.",
        explanation="Le long d'une frontière de plaques tectoniques en subduction, la contrainte s'accumule en continu et se libère par à-coups — la récurrence des séismes majeurs y est statistiquement prévisible sur le temps long, mais leur déclenchement précis reste imprévisible.",
        source="Mécanisme géologique standard (tectonique des plaques).",
        mechanism_type=MechanismType.FACT,
        connects_to=["vulnerabilite_differenciee_catastrophe"],
    ),
    Mechanism(
        id="elevation_niveau_mer",
        category=Category.GEOLOGIQUE_CLIMATIQUE,
        label="Élévation du niveau de la mer",
        base_situation="Une ville côtière voit des inondations de plus en plus fréquentes, sans qu'aucune tempête exceptionnelle ne soit en cause.",
        explanation="La hausse progressive du niveau moyen des mers réduit la marge entre une marée ordinaire et le seuil d'inondation — des événements autrefois rares (grande marée, tempête modérée) suffisent désormais à provoquer des débordements qu'ils ne provoquaient pas auparavant.",
        source="Mécanisme climatologique standard (élévation du niveau marin).",
        mechanism_type=MechanismType.FACT,
        connects_to=["zone_inondable_urbanisation"],
    ),
    Mechanism(
        id="secheresse_recurrente",
        category=Category.GEOLOGIQUE_CLIMATIQUE,
        label="Sécheresse récurrente et déficit cumulatif",
        base_situation="Une région manque d'eau alors que la pluviométrie annuelle semble proche de la moyenne historique.",
        explanation="Un déficit hydrique se construit sur plusieurs années : les nappes et réservoirs ne se rechargent pas totalement d'une saison à l'autre si les précipitations sont même légèrement sous la normale de façon répétée — l'effet est cumulatif, pas visible sur une seule année isolée.",
        source="Mécanisme hydrologique standard (bilan hydrique cumulatif).",
        mechanism_type=MechanismType.FACT,
        connects_to=["variabilite_mousson", "canicule_urbaine_ilot_chaleur"],
    ),

    # ── VULNÉRABILITÉ ───────────────────────────────────────────
    Mechanism(
        id="vulnerabilite_differenciee_catastrophe",
        category=Category.VULNERABILITE,
        label="Vulnérabilité différenciée face à une catastrophe",
        base_situation="Un même aléa naturel fait beaucoup plus de dégâts dans un pays que dans un autre, à intensité comparable.",
        explanation="L'ampleur des dégâts d'une catastrophe dépend autant de la vulnérabilité du territoire (qualité du bâti, systèmes d'alerte, moyens de secours) que de l'intensité de l'aléa lui-même — deux pays frappés par un phénomène équivalent peuvent connaître des bilans très différents.",
        source="Mécanisme standard de gestion des risques de catastrophe (couple aléa/vulnérabilité).",
        mechanism_type=MechanismType.FACT,
        connects_to=["variabilite_mousson", "zone_inondable_urbanisation", "habitat_informel_risque", "subduction_sismique"],
    ),
    Mechanism(
        id="vulnerabilite_composant_reutilise",
        category=Category.VULNERABILITE,
        label="Faille dans un composant technique mutualisé",
        base_situation="Plusieurs organisations sans lien apparent entre elles signalent le même type d'incident, la même semaine.",
        explanation="Toutes les organisations qui utilisent le même composant technique, même sans le savoir, se retrouvent exposées en même temps dès qu'une faille y est découverte — la mutualisation d'un composant mutualise aussi le risque qu'il porte.",
        source="Mécanisme standard de sécurité des chaînes logicielles (composants partagés).",
        mechanism_type=MechanismType.FACT,
        connects_to=[],
    ),
    Mechanism(
        id="zone_inondable_urbanisation",
        category=Category.VULNERABILITE,
        label="Urbanisation d'une zone inondable",
        base_situation="Un quartier récemment construit subit des inondations que la zone ne connaissait pas auparavant.",
        explanation="Construire sur une zone naturellement inondable (ancien lit de rivière, zone d'expansion de crue) supprime l'espace où l'eau se répandait sans dégâts — le risque n'a pas augmenté dans l'absolu, mais l'exposition humaine et matérielle à ce risque, si.",
        source="Mécanisme standard d'aménagement du territoire et risque inondation.",
        mechanism_type=MechanismType.FACT,
        connects_to=["vulnerabilite_differenciee_catastrophe", "elevation_niveau_mer"],
    ),
    Mechanism(
        id="habitat_informel_risque",
        category=Category.VULNERABILITE,
        label="Concentration du risque en habitat informel",
        base_situation="Un même événement climatique tue très majoritairement des habitants d'un même type de quartier.",
        explanation="Les quartiers informels se construisent souvent sur les terrains les moins chers — donc les plus exposés (pentes instables, zones inondables) — avec des matériaux moins résistants et sans accès prioritaire aux systèmes d'alerte, ce qui concentre mécaniquement le risque sur leurs habitants.",
        source="Mécanisme standard de vulnérabilité urbaine (habitat informel).",
        mechanism_type=MechanismType.FACT,
        connects_to=["exode_rural", "vulnerabilite_differenciee_catastrophe"],
    ),

    # ── BIOLOGIQUE ──────────────────────────────────────────────
    Mechanism(
        id="resistance_antibiotique",
        category=Category.BIOLOGIQUE,
        label="Sélection de résistance aux antibiotiques",
        base_situation="Un traitement autrefois efficace cesse de fonctionner contre une infection pourtant courante.",
        explanation="Chaque usage d'un antibiotique élimine les bactéries sensibles et laisse survivre celles porteuses d'une résistance, qui se multiplient alors sans concurrence — plus l'usage est fréquent ou incomplet, plus la sélection de souches résistantes s'accélère.",
        source="Mécanisme standard de sélection naturelle (résistance antimicrobienne).",
        mechanism_type=MechanismType.FACT,
        connects_to=["zoonose_transmission"],
    ),
    Mechanism(
        id="zoonose_transmission",
        category=Category.BIOLOGIQUE,
        label="Transmission zoonotique",
        base_situation="Une maladie jusque-là confinée à une espèce animale se met à infecter des humains.",
        explanation="Un agent pathogène franchit la barrière d'espèce quand le contact entre humains et une population animale infectée s'intensifie (déforestation, élevage intensif, commerce d'animaux sauvages) — plus ce contact est fréquent, plus la probabilité d'un tel saut augmente.",
        source="Mécanisme standard d'épidémiologie (maladies zoonotiques).",
        mechanism_type=MechanismType.FACT,
        connects_to=["resistance_antibiotique", "epidemie_saisonniere"],
    ),
    Mechanism(
        id="epidemie_saisonniere",
        category=Category.BIOLOGIQUE,
        label="Récurrence saisonnière d'une épidémie",
        base_situation="Une maladie infectieuse revient chaque année à la même période, avec une intensité qui varie.",
        explanation="Certains virus se transmettent mieux dans des conditions saisonnières précises (température, humidité, temps passé en intérieur) — la récurrence annuelle est prévisible dans son principe, mais son ampleur dépend de la souche circulante et de l'immunité collective du moment.",
        source="Mécanisme standard d'épidémiologie saisonnière.",
        mechanism_type=MechanismType.FACT,
        connects_to=["zoonose_transmission"],
    ),
    Mechanism(
        id="espece_invasive_ecosysteme",
        category=Category.BIOLOGIQUE,
        label="Déséquilibre par une espèce invasive",
        base_situation="Une récolte s'effondre à cause d'une espèce qui n'a rien à voir avec elle en apparence.",
        explanation="Une espèce introduite sans son cortège de prédateurs ou de parasites naturels peut proliférer sans contrôle et déséquilibrer une chaîne alimentaire entière — y compris les pollinisateurs ou prédateurs naturels dont dépendait une culture agricole.",
        source="Mécanisme standard d'écologie des invasions biologiques.",
        mechanism_type=MechanismType.FACT,
        connects_to=["pollinisateurs_dependance_agricole"],
    ),

    # ── ÉCOLOGIQUE ──────────────────────────────────────────────
    Mechanism(
        id="choc_matiere_premiere",
        category=Category.ECOLOGIQUE,
        label="Choc sur une matière première",
        base_situation="Le prix d'un produit courant grimpe brutalement à cause d'un événement survenu à l'autre bout du monde, sur une matière première qu'on ne voit jamais directement.",
        explanation="Une matière première entre dans la fabrication d'un grand nombre de produits finis différents — un choc sur son prix ou sa disponibilité (climat, conflit, épuisement) se propage donc à toute une chaîne de produits sans rapport apparent entre eux.",
        source="Mécanisme standard de marché des matières premières.",
        mechanism_type=MechanismType.FACT,
        connects_to=["cbam_dilemme_strategique", "repercussion_transport_prix", "surexploitation_ressource", "inflation_importee"],
    ),
    Mechanism(
        id="surexploitation_ressource",
        category=Category.ECOLOGIQUE,
        label="Surexploitation d'une ressource commune",
        base_situation="Une ressource partagée s'effondre alors que chaque acteur individuel se comporte de façon rationnelle.",
        explanation="Quand une ressource est partagée sans limite individuelle contraignante (un stock de poisson, une nappe phréatique), chaque acteur a intérêt à en prélever le plus possible avant les autres — un comportement rationnel à l'échelle individuelle qui conduit collectivement à l'épuisement de la ressource.",
        source="Mécanisme économique standard (tragédie des biens communs).",
        mechanism_type=MechanismType.FACT,
        connects_to=["choc_matiere_premiere", "obsolescence_programmee_reglementee"],
    ),
    Mechanism(
        id="pollinisateurs_dependance_agricole",
        category=Category.ECOLOGIQUE,
        label="Dépendance agricole aux pollinisateurs",
        base_situation="Un déclin d'insectes, loin de tout champ, fait chuter le rendement d'une culture entière.",
        explanation="Une part importante des cultures dépend de la pollinisation par des insectes — un déclin de leurs populations, causé par des facteurs parfois éloignés (pesticides, perte d'habitat, maladie), réduit directement le rendement de ces cultures, sans lien de cause à effet visible sur le terrain agricole lui-même.",
        source="Mécanisme standard d'écologie agricole (services de pollinisation).",
        mechanism_type=MechanismType.FACT,
        connects_to=["espece_invasive_ecosysteme"],
    ),
    Mechanism(
        id="canicule_urbaine_ilot_chaleur",
        category=Category.ECOLOGIQUE,
        label="Îlot de chaleur urbain",
        base_situation="Un quartier d'une ville subit une canicule bien plus intense que la campagne voisine, à quelques kilomètres seulement.",
        explanation="Le bitume, le béton et l'absence de végétation stockent la chaleur le jour et la restituent lentement la nuit — un centre-ville minéralisé peut ainsi rester plusieurs degrés plus chaud que sa périphérie végétalisée, surtout après le coucher du soleil.",
        source="Mécanisme standard de climatologie urbaine (îlot de chaleur).",
        mechanism_type=MechanismType.FACT,
        connects_to=["secheresse_recurrente"],
    ),

    # ── TECHNOLOGIQUE ───────────────────────────────────────────
    Mechanism(
        id="dependance_fournisseur_cloud_unique",
        category=Category.TECHNOLOGIQUE,
        label="Dépendance à un fournisseur cloud unique",
        base_situation="Des dizaines de services très différents tombent en panne au même moment, sans lien apparent entre eux.",
        explanation="De nombreuses entreprises hébergent leurs services chez un petit nombre de grands fournisseurs cloud — une panne chez l'un d'eux se répercute simultanément sur tous ses clients, quels que soient leurs secteurs d'activité respectifs.",
        source="Mécanisme standard d'infrastructure informatique (concentration cloud).",
        mechanism_type=MechanismType.FACT,
        connects_to=["cybersecurite_chaine_approvisionnement"],
    ),
    Mechanism(
        id="obsolescence_programmee_reglementee",
        category=Category.TECHNOLOGIQUE,
        label="Arbitrage durée de vie produit vs coût de réparation",
        base_situation="Un fabricant doit choisir entre concevoir un produit plus durable, plus cher à produire, ou moins durable, plus accessible.",
        explanation="Allonger la durée de vie d'un produit réduit son impact environnemental et son coût total pour l'utilisateur, mais augmente son prix de conception et réduit le renouvellement du marché — il n'existe pas de choix sans compromis entre accessibilité immédiate et durabilité.",
        source="Mécanisme économique standard (cycle de vie produit).",
        mechanism_type=MechanismType.DILEMMA,
        connects_to=["surexploitation_ressource"],
    ),
    Mechanism(
        id="cybersecurite_chaine_approvisionnement",
        category=Category.TECHNOLOGIQUE,
        label="Attaque par la chaîne d'approvisionnement logicielle",
        base_situation="Une entreprise bien protégée se fait pirater via un prestataire tiers auquel elle avait donné accès à ses systèmes.",
        explanation="Un attaquant qui ne parvient pas à percer les défenses d'une cible directe peut viser un fournisseur ou prestataire moins protégé mais ayant un accès légitime à cette cible — la sécurité d'une organisation dépend alors aussi de celle de tous ses partenaires techniques.",
        source="Mécanisme standard de cybersécurité (attaque supply chain).",
        mechanism_type=MechanismType.FACT,
        connects_to=["dependance_fournisseur_cloud_unique"],
    ),

    # ── PSYCHOLOGIQUE ───────────────────────────────────────────
    Mechanism(
        id="biais_ancrage_negociation",
        category=Category.PSYCHOLOGIQUE,
        label="Biais d'ancrage dans une négociation",
        base_situation="Une négociation aboutit à un résultat proche du premier chiffre annoncé, même si ce chiffre était arbitraire.",
        explanation="La première valeur mise sur la table sert de point de référence inconscient pour tout le reste de la négociation — même quand elle est reconnue comme arbitraire, elle influence durablement où se situe l'accord final.",
        source="Mécanisme standard de psychologie cognitive (biais d'ancrage).",
        mechanism_type=MechanismType.FACT,
        connects_to=["aversion_perte_investissement"],
    ),
    Mechanism(
        id="effet_rarete_decision",
        category=Category.PSYCHOLOGIQUE,
        label="Effet de rareté sur la décision",
        base_situation="Une offre présentée comme limitée dans le temps pousse à décider plus vite, sans que rien d'autre n'ait changé.",
        explanation="La perception qu'une opportunité va disparaître déclenche une prise de décision plus rapide et moins réfléchie — le mécanisme fonctionne même quand la rareté annoncée est partiellement artificielle, ce qui explique son usage répandu en marketing comme en diplomatie.",
        source="Mécanisme standard de psychologie de la décision (rareté perçue).",
        mechanism_type=MechanismType.FACT,
        connects_to=[],
    ),
    Mechanism(
        id="aversion_perte_investissement",
        category=Category.PSYCHOLOGIQUE,
        label="Aversion à la perte et coûts irrécupérables",
        base_situation="Un acteur continue d'investir dans un projet manifestement voué à l'échec, uniquement parce qu'il y a déjà beaucoup investi.",
        explanation="La douleur ressentie face à une perte pèse psychologiquement plus lourd que le plaisir d'un gain équivalent — ce déséquilibre pousse à poursuivre un projet perdant pour \"ne pas avoir perdu pour rien\", alors que l'argent déjà dépensé ne devrait, rationnellement, plus entrer dans la décision.",
        source="Mécanisme standard de psychologie de la décision (aversion à la perte).",
        mechanism_type=MechanismType.FACT,
        connects_to=["biais_ancrage_negociation"],
    ),
    Mechanism(
        id="desinformation_viralite",
        category=Category.PSYCHOLOGIQUE,
        label="Viralité de la désinformation",
        base_situation="Une fausse information circule bien plus vite et plus loin qu'un correctif publié juste après.",
        explanation="Un contenu qui déclenche une émotion forte (surprise, indignation) se partage plus spontanément qu'un contenu factuel neutre — un démenti, plus posé, touche structurellement moins de monde et arrive presque toujours après que la fausse version s'est déjà installée dans l'opinion.",
        source="Mécanisme standard de diffusion de l'information sur les réseaux (viralité asymétrique).",
        mechanism_type=MechanismType.FACT,
        connects_to=["course_influence_regionale"],
    ),

    # ── JURIDIQUE ───────────────────────────────────────────────
    Mechanism(
        id="jurisprudence_precedent_contraignant",
        category=Category.JURIDIQUE,
        label="Précédent jurisprudentiel contraignant",
        base_situation="Une décision de justice sur une petite affaire finit par changer les règles pour tout un secteur.",
        explanation="Dans les systèmes qui reconnaissent la force du précédent, une décision de justice ne tranche pas seulement le cas jugé — elle devient une référence que les juridictions inférieures doivent suivre dans des affaires similaires, ce qui démultiplie sa portée bien au-delà des parties initiales.",
        source="Mécanisme standard de droit jurisprudentiel.",
        mechanism_type=MechanismType.FACT,
        connects_to=["class_action_collective"],
    ),
    Mechanism(
        id="extraterritorialite_droit",
        category=Category.JURIDIQUE,
        label="Extraterritorialité du droit",
        base_situation="Une entreprise qui n'opère pas dans un pays donné doit quand même s'y conformer, sous peine de sanctions.",
        explanation="Certaines lois s'appliquent à toute entité qui touche, même indirectement, au marché ou à la monnaie d'un pays (transaction en dollars, présence d'un client local) — une entreprise étrangère peut donc se retrouver soumise à un droit qu'elle n'a jamais choisi.",
        source="Mécanisme standard de droit international (compétence extraterritoriale).",
        mechanism_type=MechanismType.FACT,
        connects_to=["embargo_contournement"],
    ),
    Mechanism(
        id="class_action_collective",
        category=Category.JURIDIQUE,
        label="Arbitrage réparation collective vs procès individuels",
        base_situation="Face à un préjudice de masse, regrouper les victimes en une seule action ou laisser chacune porter plainte séparément ne produit pas le même résultat, sans qu'aucune option ne soit clairement supérieure.",
        explanation="Une action collective mutualise les coûts et augmente le rapport de force face à un défendeur puissant, mais dilue l'indemnisation individuelle et allonge les délais ; les procès séparés permettent une réparation ciblée mais restent hors de portée financière pour beaucoup de victimes isolées.",
        source="Mécanisme standard de procédure civile (action de groupe).",
        mechanism_type=MechanismType.DILEMMA,
        connects_to=["jurisprudence_precedent_contraignant", "prescription_delai_recours"],
    ),
    Mechanism(
        id="prescription_delai_recours",
        category=Category.JURIDIQUE,
        label="Prescription et délai de recours",
        base_situation="Une victime perd le droit de porter plainte pour un fait pourtant réel, simplement parce que trop de temps s'est écoulé.",
        explanation="Le droit fixe des délais au-delà desquels une action en justice n'est plus recevable, pour garantir une sécurité juridique et la fiabilité des preuves dans le temps — un fait établi ne suffit donc pas toujours à obtenir réparation si le délai de prescription est dépassé.",
        source="Mécanisme standard de procédure juridique (prescription).",
        mechanism_type=MechanismType.FACT,
        connects_to=["class_action_collective"],
    ),
]


def get_mechanism(mechanism_id: str) -> Mechanism | None:
    for m in FULL_POOL:
        if m.id == mechanism_id:
            return m
    return None
