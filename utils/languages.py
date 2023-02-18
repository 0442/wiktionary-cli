definitions = {
        "en" : [
                "Adjective", "Adverb", "Article", "Conjuction", "Noun", "Numeral", 
                "Adposition", "Preposition", "Postposition", 
                "Participle", "Pronoun", "Verb", "Interjection"
        ],
        "fi" : ["Adjektiivi", "Adverbi", "Artikkeli", "Konjunktio", "Substantiivi", "Numeraali", 
                "Adpositio", "Prepositio", "Postpositio", 
                "Partisiippi", "Pronomini", "Verbi", "Interjektio"
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
                "en" : "Englanti",
                "fi" : "Suomi",
                "sv" : "Ruotsi", 
        },

        "sv" : {
                "en" : "engelska",
                "fi" : "finska",
                "sv" : "svenska",
        }
}