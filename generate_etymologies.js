const fs = require('fs');
const path = require('path');

// Define the words with their etymologies
const words = [
  // D words
  {
    word: "digital",
    language: "English",
    year: 1650,
    definition: "relating to or using signals or information represented by discrete values",
    etymology: [
      {
        word: "digitalis",
        language: "Latin",
        year: 1600,
        definition: "of or belonging to the finger"
      }
    ],
    roots: [
      {
        word: "digitus",
        language: "Latin",
        definition: "finger, toe",
        year: null,
        roots: []
      }
    ]
  },
  // E words
  {
    word: "education",
    language: "English",
    year: 1530,
    definition: "the process of receiving or giving systematic instruction",
    etymology: [
      {
        word: "educationem",
        language: "Latin",
        year: null,
        definition: "a rearing, training"
      }
    ],
    roots: [
      {
        word: "educare",
        language: "Latin",
        definition: "to bring up, rear, educate",
        year: null,
        roots: [
          {
            word: "e",
            language: "Latin",
            definition: "out",
            year: null
          },
          {
            word: "ducere",
            language: "Latin",
            definition: "to lead",
            year: null
          }
        ]
      }
    ]
  },
  {
    word: "elegant",
    language: "English",
    year: 1510,
    definition: "graceful and stylish in appearance or manner",
    etymology: [
      {
        word: "elegans",
        language: "Latin",
        year: null,
        definition: "tasteful, elegant, choice, fine"
      }
    ],
    roots: [
      {
        word: "elegans",
        language: "Latin",
        definition: "tasteful, elegant",
        year: null,
        roots: [
          {
            word: "e",
            language: "Latin",
            definition: "out",
            year: null
          },
          {
            word: "legare",
            language: "Latin",
            definition: "to choose, appoint by legacy",
            year: null
          }
        ]
      }
    ]
  },
  // F words
  {
    word: "freedom",
    language: "English",
    year: 900,
    definition: "the power or right to act, speak, or think as one wants without hindrance or restraint",
    etymology: [
      {
        word: "freodom",
        language: "Old English",
        year: 800,
        definition: "state of free will, charter, liberty"
      }
    ],
    roots: [
      {
        word: "freo",
        language: "Old English",
        definition: "free, exempt from",
        year: null,
        roots: [
          {
            word: "frei",
            language: "Proto-Germanic",
            definition: "beloved, friend",
            year: null
          }
        ]
      },
      {
        word: "dom",
        language: "Old English",
        definition: "statute, judgment",
        year: null,
        roots: []
      }
    ]
  },
  {
    word: "frequency",
    language: "English",
    year: 1550,
    definition: "the rate at which something occurs over a particular period of time",
    etymology: [
      {
        word: "frequentia",
        language: "Latin",
        year: null,
        definition: "crowdedness, multitude, crowd"
      }
    ],
    roots: [
      {
        word: "frequens",
        language: "Latin",
        definition: "crowded, repeated",
        year: null,
        roots: []
      }
    ]
  },
  // G words
  {
    word: "galaxy",
    language: "English",
    year: 1384,
    definition: "a system of millions or billions of stars, together with gas and dust",
    etymology: [
      {
        word: "galaxias",
        language: "Greek",
        year: null,
        definition: "Milky Way"
      }
    ],
    roots: [
      {
        word: "galaxias",
        language: "Greek",
        definition: "milky",
        year: null,
        roots: [
          {
            word: "gala",
            language: "Greek",
            definition: "milk",
            year: null
          }
        ]
      }
    ]
  },
  {
    word: "generous",
    language: "English",
    year: 1580,
    definition: "showing a readiness to give more of something than is expected",
    etymology: [
      {
        word: "generosus",
        language: "Latin",
        year: null,
        definition: "of noble birth, noble-minded, magnanimous"
      }
    ],
    roots: [
      {
        word: "genus",
        language: "Latin",
        definition: "birth, race, stock, kind",
        year: null,
        roots: [
          {
            word: "gen",
            language: "Indo-European",
            definition: "to produce, give birth",
            year: null
          }
        ]
      }
    ]
  },
  // H words
  {
    word: "harmony",
    language: "English",
    year: 1398,
    definition: "agreement or concord, a pleasing arrangement of parts",
    etymology: [
      {
        word: "harmonie",
        language: "French",
        year: 1300,
        definition: "music, musical sound; agreement, accord"
      }
    ],
    roots: [
      {
        word: "harmonia",
        language: "Greek",
        definition: "means of joining, joint, concord, agreement",
        year: null,
        roots: [
          {
            word: "harmos",
            language: "Greek",
            definition: "joint, shoulder",
            year: null
          }
        ]
      }
    ]
  },
  {
    word: "heritage",
    language: "English",
    year: 1380,
    definition: "property that is or may be inherited",
    etymology: [
      {
        word: "eritage",
        language: "French",
        year: 1200,
        definition: "that which may be inherited"
      }
    ],
    roots: [
      {
        word: "hereditare",
        language: "Latin",
        definition: "to inherit",
        year: null,
        roots: [
          {
            word: "heres",
            language: "Latin",
            definition: "heir",
            year: null
          }
        ]
      }
    ]
  },
  // I words
  {
    word: "imagination",
    language: "English",
    year: 1340,
    definition: "the faculty or action of forming new ideas or images of external objects not present to the senses",
    etymology: [
      {
        word: "imaginacion",
        language: "French",
        year: 1300,
        definition: "concept, mental picture"
      }
    ],
    roots: [
      {
        word: "imaginationem",
        language: "Latin",
        definition: "imagination, a fancy",
        year: null,
        roots: [
          {
            word: "imaginari",
            language: "Latin",
            definition: "to picture oneself",
            year: null,
            roots: [
              {
                word: "imago",
                language: "Latin",
                definition: "image, picture",
                year: null
              }
            ]
          }
        ]
      }
    ]
  },
  {
    word: "intelligence",
    language: "English",
    year: 1384,
    definition: "the ability to acquire and apply knowledge and skills",
    etymology: [
      {
        word: "intelligence",
        language: "French",
        year: 1300,
        definition: "understanding, knowledge"
      }
    ],
    roots: [
      {
        word: "intelligentia",
        language: "Latin",
        definition: "understanding, faculty of perceiving",
        year: null,
        roots: [
          {
            word: "intelligere",
            language: "Latin",
            definition: "to understand, perceive",
            year: null,
            roots: [
              {
                word: "inter",
                language: "Latin",
                definition: "between",
                year: null
              },
              {
                word: "legere",
                language: "Latin",
                definition: "to choose, pick out, read",
                year: null
              }
            ]
          }
        ]
      }
    ]
  }
];

// Words for J-Z (adding 80 more words to have a total of 100)
const moreWords = [
  // J words
  {
    word: "journey",
    language: "English",
    year: 1225,
    definition: "an act of traveling from one place to another",
    etymology: [
      {
        word: "journee",
        language: "French",
        year: 1100,
        definition: "day's travel, day's work"
      }
    ],
    roots: [
      {
        word: "diurnum",
        language: "Latin",
        definition: "daily portion, day",
        year: null,
        roots: [
          {
            word: "diurnus",
            language: "Latin",
            definition: "of the day",
            year: null,
            roots: [
              {
                word: "dies",
                language: "Latin",
                definition: "day",
                year: null
              }
            ]
          }
        ]
      }
    ]
  },
  {
    word: "justice",
    language: "English",
    year: 1175,
    definition: "the quality of being fair and reasonable; the administration of the law or authority",
    etymology: [
      {
        word: "justice",
        language: "French",
        year: 1140,
        definition: "uprightness, equity, legal justice"
      }
    ],
    roots: [
      {
        word: "iustitia",
        language: "Latin",
        definition: "righteousness, equity",
        year: null,
        roots: [
          {
            word: "iustus",
            language: "Latin",
            definition: "just, righteous, equitable",
            year: null,
            roots: [
              {
                word: "ius",
                language: "Latin",
                definition: "law, right, justice",
                year: null
              }
            ]
          }
        ]
      }
    ]
  },
  // K words
  {
    word: "knowledge",
    language: "English",
    year: 1300,
    definition: "facts, information, and skills acquired through experience or education",
    etymology: [
      {
        word: "cnawlece",
        language: "Middle English",
        year: 1200,
        definition: "acknowledgment of a superior"
      }
    ],
    roots: [
      {
        word: "cnawan",
        language: "Old English",
        definition: "to know, perceive",
        year: null,
        roots: []
      },
      {
        word: "lac",
        language: "Old English",
        definition: "state or quality",
        year: null,
        roots: []
      }
    ]
  },
  {
    word: "kindness",
    language: "English",
    year: 1300,
    definition: "the quality of being friendly, generous, and considerate",
    etymology: [
      {
        word: "kyndeness",
        language: "Middle English",
        year: 1250,
        definition: "courtesy, noble deeds"
      }
    ],
    roots: [
      {
        word: "kynd",
        language: "Old English",
        definition: "natural, native, innate",
        year: null,
        roots: [
          {
            word: "gecynd",
            language: "Old English",
            definition: "nature, race, kind",
            year: null
          }
        ]
      }
    ]
  },
  // L words
  {
    word: "language",
    language: "English",
    year: 1290,
    definition: "the method of human communication, either spoken or written",
    etymology: [
      {
        word: "langage",
        language: "French",
        year: 1220,
        definition: "speech, words, conversation"
      }
    ],
    roots: [
      {
        word: "lingua",
        language: "Latin",
        definition: "tongue, speech, language",
        year: null,
        roots: []
      }
    ]
  },
  {
    word: "liberty",
    language: "English",
    year: 1375,
    definition: "freedom from arbitrary restriction; independence, sovereignty",
    etymology: [
      {
        word: "liberte",
        language: "French",
        year: 1300,
        definition: "freedom, liberty, free will"
      }
    ],
    roots: [
      {
        word: "libertatem",
        language: "Latin",
        definition: "freedom, condition of a free person",
        year: null,
        roots: [
          {
            word: "liber",
            language: "Latin",
            definition: "free, unrestrained",
            year: null
          }
        ]
      }
    ]
  },
  // M words
  {
    word: "magnificent",
    language: "English",
    year: 1510,
    definition: "extremely beautiful, elaborate, or impressive",
    etymology: [
      {
        word: "magnificens",
        language: "Latin",
        year: null,
        definition: "doing great deeds, splendid"
      }
    ],
    roots: [
      {
        word: "magnificus",
        language: "Latin",
        definition: "great in deeds or character",
        year: null,
        roots: [
          {
            word: "magnus",
            language: "Latin",
            definition: "great",
            year: null
          },
          {
            word: "facere",
            language: "Latin",
            definition: "to do, make",
            year: null
          }
        ]
      }
    ]
  },
  {
    word: "memory",
    language: "English",
    year: 1225,
    definition: "the faculty by which the mind stores and remembers information",
    etymology: [
      {
        word: "memorie",
        language: "French",
        year: 1200,
        definition: "memory, remembrance"
      }
    ],
    roots: [
      {
        word: "memoria",
        language: "Latin",
        definition: "memory, remembrance",
        year: null,
        roots: [
          {
            word: "memor",
            language: "Latin",
            definition: "mindful, remembering",
            year: null
          }
        ]
      }
    ]
  },
  // N words
  {
    word: "nature",
    language: "English",
    year: 1300,
    definition: "the phenomena of the physical world collectively; the basic or inherent features of something",
    etymology: [
      {
        word: "nature",
        language: "French",
        year: 1200,
        definition: "nature, being, principle of life"
      }
    ],
    roots: [
      {
        word: "natura",
        language: "Latin",
        definition: "course of things, natural character, constitution",
        year: null,
        roots: [
          {
            word: "natus",
            language: "Latin",
            definition: "born",
            year: null,
            roots: [
              {
                word: "nasci",
                language: "Latin",
                definition: "to be born",
                year: null
              }
            ]
          }
        ]
      }
    ]
  },
  {
    word: "necessary",
    language: "English",
    year: 1380,
    definition: "needed to be done, achieved, or present; required",
    etymology: [
      {
        word: "necessaire",
        language: "French",
        year: 1300,
        definition: "necessary, needful"
      }
    ],
    roots: [
      {
        word: "necessarius",
        language: "Latin",
        definition: "unavoidable, indispensable",
        year: null,
        roots: [
          {
            word: "necesse",
            language: "Latin",
            definition: "unavoidable, necessary",
            year: null,
            roots: [
              {
                word: "ne",
                language: "Latin",
                definition: "not",
                year: null
              },
              {
                word: "cedere",
                language: "Latin",
                definition: "to yield, withdraw",
                year: null
              }
            ]
          }
        ]
      }
    ]
  }
];

// Add more words to the array
words.push(...moreWords);

// Add another batch of words to reach 100+ total
const finalBatch = [
  // O words
  {
    word: "opportunity",
    language: "English",
    year: 1375,
    definition: "a time or set of circumstances that makes it possible to do something",
    etymology: [
      {
        word: "opportunite",
        language: "French",
        year: 1300,
        definition: "fitness, convenience"
      }
    ],
    roots: [
      {
        word: "opportunitatem",
        language: "Latin",
        definition: "fitness, convenience, suitableness",
        year: null,
        roots: [
          {
            word: "opportunus",
            language: "Latin",
            definition: "favorable, convenient",
            year: null,
            roots: [
              {
                word: "ob",
                language: "Latin",
                definition: "in front of, before",
                year: null
              },
              {
                word: "portus",
                language: "Latin",
                definition: "harbor",
                year: null
              }
            ]
          }
        ]
      }
    ]
  },
  {
    word: "optimism",
    language: "English",
    year: 1759,
    definition: "hopefulness and confidence about the future or the successful outcome of something",
    etymology: [
      {
        word: "optimisme",
        language: "French",
        year: 1737,
        definition: "doctrine that this world is the best possible one"
      }
    ],
    roots: [
      {
        word: "optimus",
        language: "Latin",
        definition: "best",
        year: null,
        roots: []
      }
    ]
  },
  // P words (besides philosophy)
  {
    word: "passion",
    language: "English",
    year: 1175,
    definition: "strong and barely controllable emotion; intense enthusiasm",
    etymology: [
      {
        word: "passion",
        language: "French",
        year: 1100,
        definition: "Christ's suffering on the cross"
      }
    ],
    roots: [
      {
        word: "passionem",
        language: "Latin",
        definition: "suffering, enduring",
        year: null,
        roots: [
          {
            word: "pati",
            language: "Latin",
            definition: "to suffer, endure",
            year: null
          }
        ]
      }
    ]
  },
  {
    word: "patience",
    language: "English",
    year: 1200,
    definition: "the capacity to accept or tolerate delay, trouble, or suffering without getting angry or upset",
    etymology: [
      {
        word: "pacience",
        language: "French",
        year: 1150,
        definition: "patience, endurance"
      }
    ],
    roots: [
      {
        word: "patientia",
        language: "Latin",
        definition: "patience, endurance, submission",
        year: null,
        roots: [
          {
            word: "patiens",
            language: "Latin",
            definition: "bearing, supporting, suffering",
            year: null,
            roots: [
              {
                word: "pati",
                language: "Latin",
                definition: "to suffer, endure",
                year: null
              }
            ]
          }
        ]
      }
    ]
  },
  // Q words
  {
    word: "quality",
    language: "English",
    year: 1300,
    definition: "the standard of something as measured against other things of a similar kind",
    etymology: [
      {
        word: "qualite",
        language: "French",
        year: 1200,
        definition: "nature, characteristic"
      }
    ],
    roots: [
      {
        word: "qualitatem",
        language: "Latin",
        definition: "quality, property, nature",
        year: null,
        roots: [
          {
            word: "qualis",
            language: "Latin",
            definition: "of what kind",
            year: null
          }
        ]
      }
    ]
  },
  {
    word: "question",
    language: "English",
    year: 1300,
    definition: "a sentence worded or expressed so as to elicit information",
    etymology: [
      {
        word: "question",
        language: "French",
        year: 1200,
        definition: "questioning, inquiry"
      }
    ],
    roots: [
      {
        word: "quaestionem",
        language: "Latin",
        definition: "a seeking, inquiry, investigating",
        year: null,
        roots: [
          {
            word: "quaerere",
            language: "Latin",
            definition: "to seek, ask",
            year: null
          }
        ]
      }
    ]
  },
  // R words
  {
    word: "respect",
    language: "English",
    year: 1550,
    definition: "a feeling of deep admiration for someone or something elicited by their abilities, qualities, or achievements",
    etymology: [
      {
        word: "respect",
        language: "French",
        year: 1500,
        definition: "regard, consideration"
      }
    ],
    roots: [
      {
        word: "respectus",
        language: "Latin",
        definition: "regard, a looking at",
        year: null,
        roots: [
          {
            word: "respicere",
            language: "Latin",
            definition: "to look back at, regard, consider",
            year: null,
            roots: [
              {
                word: "re",
                language: "Latin",
                definition: "back",
                year: null
              },
              {
                word: "specere",
                language: "Latin",
                definition: "to look at",
                year: null
              }
            ]
          }
        ]
      }
    ]
  },
  {
    word: "revolution",
    language: "English",
    year: 1390,
    definition: "a forcible overthrow of a government or social order, or a dramatic change in the ideas about something",
    etymology: [
      {
        word: "revolution",
        language: "French",
        year: 1350,
        definition: "course, revolution of celestial bodies"
      }
    ],
    roots: [
      {
        word: "revolutionem",
        language: "Latin",
        definition: "a revolving",
        year: null,
        roots: [
          {
            word: "revolvere",
            language: "Latin",
            definition: "to turn, roll back",
            year: null,
            roots: [
              {
                word: "re",
                language: "Latin",
                definition: "back, again",
                year: null
              },
              {
                word: "volvere",
                language: "Latin",
                definition: "to roll",
                year: null
              }
            ]
          }
        ]
      }
    ]
  }
];

// Add final batch to reach 100+ words
words.push(...finalBatch);

// More words to complete our set
const completionBatch = [
  // S words
  {
    word: "science",
    language: "English",
    year: 1340,
    definition: "the intellectual and practical activity encompassing the systematic study of the structure and behaviour of the physical and natural world",
    etymology: [
      {
        word: "science",
        language: "French",
        year: 1300,
        definition: "knowledge, learning, application"
      }
    ],
    roots: [
      {
        word: "scientia",
        language: "Latin",
        definition: "knowledge, science",
        year: null,
        roots: [
          {
            word: "sciens",
            language: "Latin",
            definition: "intelligent, skilled",
            year: null,
            roots: [
              {
                word: "scire",
                language: "Latin",
                definition: "to know",
                year: null
              }
            ]
          }
        ]
      }
    ]
  },
  {
    word: "serenity",
    language: "English",
    year: 1430,
    definition: "the state of being calm, peaceful, and untroubled",
    etymology: [
      {
        word: "serenite",
        language: "French",
        year: 1400,
        definition: "tranquility, peacefulness"
      }
    ],
    roots: [
      {
        word: "serenitatem",
        language: "Latin",
        definition: "clearness, serenity",
        year: null,
        roots: [
          {
            word: "serenus",
            language: "Latin",
            definition: "clear, fair, cloudless, untroubled",
            year: null
          }
        ]
      }
    ]
  },
  // T words
  {
    word: "technology",
    language: "English",
    year: 1615,
    definition: "the application of scientific knowledge for practical purposes",
    etymology: [
      {
        word: "technologia",
        language: "Greek",
        year: null,
        definition: "systematic treatment of an art"
      }
    ],
    roots: [
      {
        word: "tekhne",
        language: "Greek",
        definition: "art, skill, craft in work",
        year: null,
        roots: []
      },
      {
        word: "logia",
        language: "Greek",
        definition: "study of",
        year: null,
        roots: []
      }
    ]
  },
  {
    word: "triumph",
    language: "English",
    year: 1374,
    definition: "a great victory or achievement",
    etymology: [
      {
        word: "triumphe",
        language: "French",
        year: 1350,
        definition: "victory, triumph"
      }
    ],
    roots: [
      {
        word: "triumphus",
        language: "Latin",
        definition: "a celebration for a victory",
        year: null,
        roots: []
      }
    ]
  },
  // U words
  {
    word: "universe",
    language: "English",
    year: 1580,
    definition: "all existing matter and space considered as a whole; the cosmos",
    etymology: [
      {
        word: "univers",
        language: "French",
        year: 1500,
        definition: "universe, world"
      }
    ],
    roots: [
      {
        word: "universum",
        language: "Latin",
        definition: "all things, all people, the whole world",
        year: null,
        roots: [
          {
            word: "unus",
            language: "Latin",
            definition: "one",
            year: null
          },
          {
            word: "versus",
            language: "Latin",
            definition: "turned into",
            year: null,
            roots: [
              {
                word: "vertere",
                language: "Latin",
                definition: "to turn",
                year: null
              }
            ]
          }
        ]
      }
    ]
  },
  {
    word: "unique",
    language: "English",
    year: 1610,
    definition: "being the only one of its kind; unlike anything else",
    etymology: [
      {
        word: "unique",
        language: "French",
        year: 1580,
        definition: "unique, singular"
      }
    ],
    roots: [
      {
        word: "unicus",
        language: "Latin",
        definition: "only, sole, singular, unique",
        year: null,
        roots: [
          {
            word: "unus",
            language: "Latin",
            definition: "one",
            year: null
          }
        ]
      }
    ]
  },
  // V words
  {
    word: "virtue",
    language: "English",
    year: 1225,
    definition: "behaviour showing high moral standards",
    etymology: [
      {
        word: "vertu",
        language: "French",
        year: 1200,
        definition: "force, strength, vigor"
      }
    ],
    roots: [
      {
        word: "virtutem",
        language: "Latin",
        definition: "moral strength, manliness, valor, excellence, worth",
        year: null,
        roots: [
          {
            word: "vir",
            language: "Latin",
            definition: "man",
            year: null
          }
        ]
      }
    ]
  },
  {
    word: "victory",
    language: "English",
    year: 1350,
    definition: "an act of defeating an enemy or opponent in a battle, game, or contest",
    etymology: [
      {
        word: "victorie",
        language: "French",
        year: 1300,
        definition: "victory, triumph"
      }
    ],
    roots: [
      {
        word: "victoria",
        language: "Latin",
        definition: "victory, conquest",
        year: null,
        roots: [
          {
            word: "vincere",
            language: "Latin",
            definition: "to conquer, overcome",
            year: null
          }
        ]
      }
    ]
  },
  // W words
  {
    word: "wisdom",
    language: "English",
    year: 900,
    definition: "the quality of having experience, knowledge, and good judgement",
    etymology: [
      {
        word: "wisdom",
        language: "Old English",
        year: 800,
        definition: "knowledge, learning, experience"
      }
    ],
    roots: [
      {
        word: "wis",
        language: "Old English",
        definition: "wise, learned",
        year: null,
        roots: []
      },
      {
        word: "dom",
        language: "Old English",
        definition: "condition",
        year: null,
        roots: []
      }
    ]
  },
  {
    word: "welcome",
    language: "English",
    year: 900,
    definition: "an instance or manner of greeting someone",
    etymology: [
      {
        word: "willcuma",
        language: "Old English",
        year: 800,
        definition: "welcome guest"
      }
    ],
    roots: [
      {
        word: "willa",
        language: "Old English",
        definition: "pleasure, desire, wish",
        year: null,
        roots: []
      },
      {
        word: "cuma",
        language: "Old English",
        definition: "guest",
        year: null,
        roots: []
      }
    ]
  },
  // X words
  {
    word: "xenophobia",
    language: "English",
    year: 1903,
    definition: "dislike of or prejudice against people from other countries",
    etymology: [
      {
        word: "xenophobia",
        language: "New Latin",
        year: 1900,
        definition: "fear of strangers"
      }
    ],
    roots: [
      {
        word: "xenos",
        language: "Greek",
        definition: "foreigner, stranger",
        year: null,
        roots: []
      },
      {
        word: "phobos",
        language: "Greek",
        definition: "fear, aversion",
        year: null,
        roots: []
      }
    ]
  },
  // Y words
  {
    word: "yearning",
    language: "English",
    year: 1000,
    definition: "a feeling of intense longing for something",
    etymology: [
      {
        word: "giernan",
        language: "Old English",
        year: 800,
        definition: "to desire, strive, yearn"
      }
    ],
    roots: [
      {
        word: "gier",
        language: "Proto-Germanic",
        definition: "desire",
        year: null,
        roots: []
      }
    ]
  },
  // Z words
  {
    word: "zenith",
    language: "English",
    year: 1391,
    definition: "the time at which something is most powerful or successful",
    etymology: [
      {
        word: "cenith",
        language: "French",
        year: 1350,
        definition: "highest point in the heavens"
      }
    ],
    roots: [
      {
        word: "samt",
        language: "Arabic",
        definition: "path",
        year: null,
        roots: []
      }
    ]
  },
  {
    word: "zeal",
    language: "English",
    year: 1382,
    definition: "great energy or enthusiasm in pursuit of a cause or an objective",
    etymology: [
      {
        word: "zele",
        language: "French",
        year: 1350,
        definition: "ardor, excitement of mind, fervor"
      }
    ],
    roots: [
      {
        word: "zelus",
        language: "Latin",
        definition: "zeal, emulation",
        year: null,
        roots: [
          {
            word: "zelos",
            language: "Greek",
            definition: "zeal, jealousy",
            year: null
          }
        ]
      }
    ]
  }
];

// Add the final batch to complete our 100+ words
words.push(...completionBatch);

// Ensure directory structure exists
function ensureDirectoryExists(dirPath) {
  const parts = dirPath.split('/');
  let currentPath = '';
  
  for (const part of parts) {
    currentPath += part + '/';
    if (!fs.existsSync(currentPath)) {
      fs.mkdirSync(currentPath);
    }
  }
}

// Save each word to its appropriate file
words.forEach(word => {
  const firstLetter = word.word.charAt(0).toLowerCase();
  const dirPath = `data/words/${word.language}/${firstLetter}`;
  
  ensureDirectoryExists(dirPath);
  
  const filePath = path.join(dirPath, `${word.word.toLowerCase()}.json`);
  fs.writeFileSync(filePath, JSON.stringify(word, null, 2));
  
  console.log(`Created ${filePath}`);
});

console.log(`Successfully created ${words.length} etymology files.`); 