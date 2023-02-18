word_classes = {
        "en" : [
                "Adjective", "Adverb", "Article", "Conjuction", "Noun", "Numeral", 
                "Adposition", "Preposition", "Postposition", 
                "Participle", "Pronoun", "Verb"
        ],
        "fi" : ["Adjektiivi", "Adverbi", "Artikkeli", "Konjunktio", "Substantiivi", "Numeraali", 
                "Adpositio", "Prepositio", "Postpositio", 
                "Partisiippi", "Pronomini", "Verbi"
        ],
        "sv" : [""],
}

supported = ["en", "fi"]

# lookup tables for how languages used in e.g. titles are written in different languages in wiki.
abbrev_table = {
        "en" : {
                "en" : "English",
                "fi" : "Finnish",
                "sv" : "Swedish",
        },

        "fi" : {        
                "en" : "englanti",
                "fi" : "suomi",
                "sv" : "ruotsi", 
        },

        "sv" : {
                "en" : "engelska",
                "fi" : "finska",
                "sv" : "svenska",
        }
}