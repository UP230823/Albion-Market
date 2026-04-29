# items_db.py
CATEGORIAS = {
    "Árbol: Hachas": {
        "MAIN_AXE": "Hacha de batalla (1H)", "2H_AXE": "Gran hacha", "2H_HALBERD": "Alabarda", "2H_AXE_KEEPER": "Segador de carroña", "2H_AXE_HELL": "Hacha de guadaña", "2H_AXE_RUNIC_WHITELOCK": "Garras de oso", "2H_AXE_AVALON": "Rompe-reinos", "2H_AXE_CRYSTAL": "Hacha de cristal"
    },
    "Árbol: Espadas": {
        "MAIN_SWORD": "Espada ancha (1H)", "2H_CLAYMORE": "Mandoble", "2H_DUALSWORD": "Espadas duales", "MAIN_SCIMITAR_MORGANA": "Hoja de espíritu", "2H_CLEAVER_HELL": "Hojas de carnicero", "2H_CARVINGSWORD": "Espada tallada", "2H_SWORD_AVALON": "Heredera del Rey", "2H_SWORD_CRYSTAL": "Espada de cristal"
    },
    "Árbol: Mazas": {
        "MAIN_MACE": "Maza (1H)", "2H_MACE": "Maza pesada", "2H_FLAIL": "Lucero del alba", "MAIN_ROCKMACE_KEEPER": "Maza de roca", "2H_MACE_HELL": "Maza de íncubo", "2H_MACE_RUNIC_WHITE": "Maza de camlann", "2H_MACE_AVALON": "Guardia del juramento", "2H_MACE_CRYSTAL": "Maza de cristal"
    },
    "Árbol: Martillos": {
        "MAIN_HAMMER": "Martillo (1H)", "2H_HAMMER": "Gran martillo", "2H_POLEHAMMER": "Martillo de polo", "2H_HAMMER_TYPE1_KEEPER": "Martillo de piedra", "2H_HAMMER_HELL": "Forja-almas", "2H_HAMMER_RUNIC_HERCULES": "Mano de justicia", "2H_HAMMER_AVALON": "Custodio del sepulcro", "2H_HAMMER_CRYSTAL": "Martillo cristal"
    },
    "Árbol: Guantes de Guerra": {
        "2H_WARGLOVES_BRAWLER": "Guantes de púgil", "2H_WARGLOVES_BATTLEEYE": "Buscadores de batalla", "2H_WARGLOVES_SPIKED": "Guantes de pinchos", "2H_WARGLOVES_KEEPER": "Guantes de oso", "2H_WARGLOVES_HELL": "Furia de manos", "2H_WARGLOVES_RUNIC_REAPER": "Segadores de almas", "2H_WARGLOVES_AVALON": "Puños de Avalon", "2H_WARGLOVES_CRYSTAL": "Guantes cristal"
    },
    "Árbol: Ballestas": {
        "2H_CROSSBOW": "Ballesta", "MAIN_REPEATINGCROSSBOW": "Ballesta ligera (1H)", "2H_LONGCROSSBOW": "Ballesta pesada", "2H_CROSSBOW_CANNON_MORGANA": "Lanza-virotes", "2H_CROSSBOW_HELL": "Repetidora de asedio", "2H_CROSSBOW_RUNIC_LIGHTORB": "Ballesta francotirador", "2H_CROSSBOW_AVALON": "Creador energía", "2H_CROSSBOW_CRYSTAL": "Ballesta cristal"
    },
    "Árbol: Arcos": {
        "2H_BOW": "Arco", "2H_WARBOW": "Arco de guerra", "2H_LONGBOW": "Arco largo", "2H_BOW_KEEPER": "Arco susurrante", "2H_BOW_HELL": "Arco de aullidos", "2H_BOW_RUNIC_WOLVERINE": "Arco de buey", "2H_BOW_AVALON": "Arco de niebla", "2H_BOW_CRYSTAL": "Arco cristal"
    },
    "Árbol: Dagas": {
        "MAIN_DAGGER": "Daga (1H)", "2H_DAGGERPAIR": "Dagas de par", "2H_CLAW": "Garras", "MAIN_DAGGER_KEEPER": "Daga de sangre", "2H_DAGGER_HELL": "Dagas de demonio", "2H_DUAL_DAGGER_RUNIC_ELLEN": "Colmillos de rabia", "2H_DAGGER_AVALON": "Buscador almas", "2H_DAGGER_CRYSTAL": "Daga cristal"
    },
    "Árbol: Lanzas": {
        "MAIN_SPEAR": "Lanza (1H)", "2H_SPEAR": "Gran lanza", "2H_GLAIVE": "Guja", "MAIN_SPEAR_KEEPER": "Garza", "2H_HARPOON_HELL": "Caza-espíritus", "2H_SPEAR_RUNIC_SLAYER": "Tridente de caza", "2H_SPEAR_AVALON": "Portador del día", "2H_SPEAR_CRYSTAL": "Lanza cristal"
    },
    "Árbol: Varas": {
        "2H_QUARTERSTAFF": "Vara", "2H_IRONCLADSTAFF": "Vara de hierro", "2H_DOUBLEBLADEDSTAFF": "Vara doble hoja", "2H_QUARTERSTAFF_TYPE1_KEEPER": "Bastón de monje", "2H_QUARTERSTAFF_HELL": "Bastón de alma", "2H_QUARTERSTAFF_RUNIC_CHRONOS": "Grial negro", "2H_QUARTERSTAFF_AVALON": "Buscador equilibrio", "2H_QUARTERSTAFF_CRYSTAL": "Vara cristal"
    },
    "Árbol: Naturaleza": {
        "MAIN_NATURESTAFF": "Bastón naturaleza (1H)", "2H_NATURESTAFF": "Gran bastón naturaleza", "2H_WILDSTAFF": "Bastón salvaje", "MAIN_NATURESTAFF_KEEPER": "Bastón druida", "2H_NATURESTAFF_HELL": "Bastón plaga", "2H_NATURESTAFF_RUNIC_WHITELOCK": "Bastón crecimiento", "2H_NATURESTAFF_AVALON": "Bastón de vida", "2H_NATURESTAFF_CRYSTAL": "Naturaleza cristal"
    },
    "Árbol: Sagrado": {
        "MAIN_HOLYSTAFF": "Bastón sagrado (1H)", "2H_HOLYSTAFF": "Gran bastón sagrado", "2H_DIVINESTAFF": "Bastón divino", "MAIN_HOLYSTAFF_MORGANA": "Bastón santuario", "2H_HOLYSTAFF_HELL": "Bastón caída", "2H_HOLYSTAFF_RUNIC_WHITE": "Bastón redención", "2H_HOLYSTAFF_AVALON": "Bastón resurrección", "2H_HOLYSTAFF_CRYSTAL": "Sagrado cristal"
    },
    "Árbol: Malditos": {
        "MAIN_CURSESTAFF": "Bastón maldito (1H)", "2H_CURSESTAFF": "Gran bastón maldito", "2H_DEMONICSTAFF": "Bastón demoníaco", "2H_CURSESTAFF_MORGANA": "Bastón vida muerta", "2H_SKULLORB_HELL": "Cráneo maldito", "2H_CURSESTAFF_OPSIDIAN": "Llamador perdición", "2H_CURSESTAFF_AVALON": "Bastón sombra", "2H_CURSESTAFF_CRYSTAL": "Maldito cristal"
    },
    "Árbol: Arcanos": {
        "MAIN_ARCANESTAFF": "Bastón arcano (1H)", "2H_ARCANESTAFF": "Gran bastón arcano", "2H_ENIGMATICSTAFF": "Bastón enigmático", "MAIN_ARCANESTAFF_MORGANA": "Bastón bruja", "2H_ARCANESTAFF_HELL": "Bastón oculto", "2H_ARCANESTAFF_RUNIC_RED": "Bastón vacío", "2H_ARCANESTAFF_AVALON": "Bastón energía", "2H_ARCANESTAFF_CRYSTAL": "Arcano cristal"
    },
    "Pecheras (Armor N=192)": {
        "ARMOR_PLATE_SET1": "Pechera Soldado", "ARMOR_PLATE_SET2": "Pechera Guardián", "ARMOR_PLATE_SET3": "Pechera Caballero", "ARMOR_LEATHER_SET1": "Chaqueta Mercenario", "ARMOR_LEATHER_SET2": "Chaqueta Cazador", "ARMOR_LEATHER_SET3": "Chaqueta Asesino", "ARMOR_CLOTH_SET1": "Túnica Erudito", "ARMOR_CLOTH_SET2": "Túnica Clérigo", "ARMOR_CLOTH_SET3": "Túnica Mago"
    },
    "Cascos y Botas (N=96)": {
        "HEAD_PLATE_SET1": "Casco Soldado", "HEAD_PLATE_SET2": "Casco Guardián", "HEAD_PLATE_SET3": "Casco Caballero", "HEAD_LEATHER_SET1": "Capucha Mercenario", "HEAD_LEATHER_SET2": "Capucha Cazador", "HEAD_LEATHER_SET3": "Capucha Asesino", "HEAD_CLOTH_SET1": "Caperuza Erudito", "HEAD_CLOTH_SET2": "Caperuza Clérigo", "HEAD_CLOTH_SET3": "Caperuza Mago",
        "SHOES_PLATE_SET1": "Botas Soldado", "SHOES_PLATE_SET2": "Botas Guardián", "SHOES_PLATE_SET3": "Botas Caballero", "SHOES_LEATHER_SET1": "Botas Mercenario", "SHOES_LEATHER_SET2": "Botas Cazador", "SHOES_LEATHER_SET3": "Botas Asesino", "SHOES_CLOTH_SET1": "Sandalias Erudito", "SHOES_CLOTH_SET2": "Sandalias Clérigo", "SHOES_CLOTH_SET3": "Sandalias Mago"
    },
    "Accesorios y Off-hands (N=96)": {
        "BAG": "Bolsa", "CAPE": "Capa", "SHIELD": "Escudo", "TORCH": "Antorcha", "TOME": "Libro de hechizos"
    }
}