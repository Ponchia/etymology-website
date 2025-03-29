const fs = require('fs');
const path = require('path');

// Define more words with their etymologies
const moreWords = [
  // A words
  {
    word: "alphabet",
    language: "English",
    year: 1570,
    definition: "a set of letters or symbols in a fixed order used to represent the basic sounds of a language",
    etymology: [
      {
        word: "alphabetum",
        language: "Latin",
        year: 1500,
        definition: "alphabet"
      }
    ],
    roots: [
      {
        word: "alphabetos",
        language: "Greek",
        definition: "alphabet",
        year: null,
        roots: [
          {
            word: "alpha",
            language: "Greek",
            definition: "first letter of Greek alphabet",
            year: null
          },
          {
            word: "beta",
            language: "Greek",
            definition: "second letter of Greek alphabet",
            year: null
          }
        ]
      }
    ]
  },
  {
    word: "astronomy",
    language: "English",
    year: 1220,
    definition: "the branch of science that deals with celestial objects, space, and the physical universe as a whole",
    etymology: [
      {
        word: "astronomie",
        language: "French",
        year: 1200,
        definition: "astronomy"
      }
    ],
    roots: [
      {
        word: "astronomia",
        language: "Greek",
        definition: "astronomy, star arrangement",
        year: null,
        roots: [
          {
            word: "astron",
            language: "Greek",
            definition: "star, constellation",
            year: null
          },
          {
            word: "nomos",
            language: "Greek",
            definition: "arranging, regulating",
            year: null
          }
        ]
      }
    ]
  },
  
  // B words
  {
    word: "biology",
    language: "English",
    year: 1819,
    definition: "the study of living organisms",
    etymology: [
      {
        word: "biologie",
        language: "French",
        year: 1802,
        definition: "biology"
      }
    ],
    roots: [
      {
        word: "bios",
        language: "Greek",
        definition: "life",
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
    word: "brilliant",
    language: "English",
    year: 1680,
    definition: "exceptionally clever, talented, or impressive",
    etymology: [
      {
        word: "brillant",
        language: "French",
        year: 1600,
        definition: "shining, sparkling"
      }
    ],
    roots: [
      {
        word: "beryllus",
        language: "Latin",
        definition: "beryl, precious stone",
        year: null,
        roots: []
      }
    ]
  },
  
  // C words
  {
    word: "courage",
    language: "English",
    year: 1300,
    definition: "the ability to do something that frightens one; bravery",
    etymology: [
      {
        word: "corage",
        language: "French",
        year: 1250,
        definition: "heart, innermost feelings, temper"
      }
    ],
    roots: [
      {
        word: "cor",
        language: "Latin",
        definition: "heart",
        year: null,
        roots: []
      }
    ]
  },
  {
    word: "celebrate",
    language: "English",
    year: 1520,
    definition: "acknowledge a significant or happy day or event with a social gathering or enjoyable activity",
    etymology: [
      {
        word: "celebratus",
        language: "Latin",
        year: null,
        definition: "frequented, honored, famous"
      }
    ],
    roots: [
      {
        word: "celebrare",
        language: "Latin",
        definition: "to frequent, to honor",
        year: null,
        roots: [
          {
            word: "celeber",
            language: "Latin",
            definition: "frequented, populous",
            year: null
          }
        ]
      }
    ]
  },
  
  // D words
  {
    word: "destiny",
    language: "English",
    year: 1330,
    definition: "the events that will necessarily happen to a particular person or thing in the future",
    etymology: [
      {
        word: "destinee",
        language: "French",
        year: 1300,
        definition: "purpose, intent, fate, destiny"
      }
    ],
    roots: [
      {
        word: "destinata",
        language: "Latin",
        definition: "things determined",
        year: null,
        roots: [
          {
            word: "destinare",
            language: "Latin",
            definition: "to make firm, establish",
            year: null,
            roots: [
              {
                word: "de",
                language: "Latin",
                definition: "down from, from",
                year: null
              },
              {
                word: "stare",
                language: "Latin",
                definition: "to stand",
                year: null
              }
            ]
          }
        ]
      }
    ]
  },
  {
    word: "discover",
    language: "English",
    year: 1300,
    definition: "find unexpectedly or during a search",
    etymology: [
      {
        word: "descovrir",
        language: "French",
        year: 1200,
        definition: "uncover, unroof, unveil, reveal"
      }
    ],
    roots: [
      {
        word: "discooperire",
        language: "Latin",
        definition: "uncover, expose",
        year: null,
        roots: [
          {
            word: "dis",
            language: "Latin",
            definition: "opposite of",
            year: null
          },
          {
            word: "cooperire",
            language: "Latin",
            definition: "to cover up",
            year: null
          }
        ]
      }
    ]
  },
  
  // E words
  {
    word: "enthusiasm",
    language: "English",
    year: 1603,
    definition: "intense and eager enjoyment, interest, or approval",
    etymology: [
      {
        word: "enthusiasme",
        language: "French",
        year: 1580,
        definition: "divine inspiration"
      }
    ],
    roots: [
      {
        word: "enthousiasmos",
        language: "Greek",
        definition: "inspiration, enthusiasm",
        year: null,
        roots: [
          {
            word: "entheos",
            language: "Greek",
            definition: "divinely inspired, possessed by a god",
            year: null,
            roots: [
              {
                word: "en",
                language: "Greek",
                definition: "in",
                year: null
              },
              {
                word: "theos",
                language: "Greek",
                definition: "god",
                year: null
              }
            ]
          }
        ]
      }
    ]
  },
  {
    word: "essential",
    language: "English",
    year: 1370,
    definition: "absolutely necessary; extremely important",
    etymology: [
      {
        word: "essentialis",
        language: "Latin",
        year: null,
        definition: "belonging to the essence"
      }
    ],
    roots: [
      {
        word: "essentia",
        language: "Latin",
        definition: "being, essence",
        year: null,
        roots: [
          {
            word: "esse",
            language: "Latin",
            definition: "to be",
            year: null
          }
        ]
      }
    ]
  },
  
  // F words
  {
    word: "fortune",
    language: "English",
    year: 1300,
    definition: "chance or luck as an external, arbitrary force affecting human affairs",
    etymology: [
      {
        word: "fortune",
        language: "French",
        year: 1200,
        definition: "chance, fate, luck"
      }
    ],
    roots: [
      {
        word: "fortuna",
        language: "Latin",
        definition: "chance, fate, fortune",
        year: null,
        roots: [
          {
            word: "fors",
            language: "Latin",
            definition: "chance, luck",
            year: null
          }
        ]
      }
    ]
  },
  {
    word: "friendship",
    language: "English",
    year: 1000,
    definition: "the emotions or conduct of friends; the state of being friends",
    etymology: [
      {
        word: "freondscipe",
        language: "Old English",
        year: 900,
        definition: "friendship, mutual affection"
      }
    ],
    roots: [
      {
        word: "freond",
        language: "Old English",
        definition: "friend, lover",
        year: null,
        roots: [
          {
            word: "freon",
            language: "Proto-Germanic",
            definition: "to love",
            year: null
          }
        ]
      },
      {
        word: "scipe",
        language: "Old English",
        definition: "state, condition of being",
        year: null,
        roots: []
      }
    ]
  }
];

// Continue with more words for other letters
const secondBatch = [
  // G words
  {
    word: "gratitude",
    language: "English",
    year: 1500,
    definition: "the quality of being thankful; readiness to show appreciation",
    etymology: [
      {
        word: "gratitude",
        language: "French",
        year: 1450,
        definition: "thankfulness"
      }
    ],
    roots: [
      {
        word: "gratitudinem",
        language: "Latin",
        definition: "thankfulness",
        year: null,
        roots: [
          {
            word: "gratus",
            language: "Latin",
            definition: "pleasing, thankful",
            year: null
          }
        ]
      }
    ]
  },
  {
    word: "geography",
    language: "English",
    year: 1400,
    definition: "the study of the physical features of the earth and its atmosphere",
    etymology: [
      {
        word: "geographie",
        language: "French",
        year: 1300,
        definition: "geography"
      }
    ],
    roots: [
      {
        word: "geographia",
        language: "Greek",
        definition: "description of the earth's surface",
        year: null,
        roots: [
          {
            word: "geo",
            language: "Greek",
            definition: "earth",
            year: null
          },
          {
            word: "graphia",
            language: "Greek",
            definition: "description",
            year: null
          }
        ]
      }
    ]
  },
  
  // H words
  {
    word: "honor",
    language: "English",
    year: 1200,
    definition: "high respect; great esteem",
    etymology: [
      {
        word: "honor",
        language: "French",
        year: 1100,
        definition: "glory, renown, reputation"
      }
    ],
    roots: [
      {
        word: "honor",
        language: "Latin",
        definition: "honor, dignity, office, reputation",
        year: null,
        roots: []
      }
    ]
  },
  {
    word: "humanity",
    language: "English",
    year: 1350,
    definition: "the human race; human beings collectively",
    etymology: [
      {
        word: "humanite",
        language: "French",
        year: 1300,
        definition: "human nature, humankind"
      }
    ],
    roots: [
      {
        word: "humanitatem",
        language: "Latin",
        definition: "human nature, humanity",
        year: null,
        roots: [
          {
            word: "humanus",
            language: "Latin",
            definition: "of man, human",
            year: null,
            roots: [
              {
                word: "homo",
                language: "Latin",
                definition: "man, human being",
                year: null
              }
            ]
          }
        ]
      }
    ]
  },
  
  // I words
  {
    word: "inspire",
    language: "English",
    year: 1300,
    definition: "fill someone with the urge or ability to do or feel something",
    etymology: [
      {
        word: "inspirer",
        language: "French",
        year: 1250,
        definition: "blow into, breathe upon"
      }
    ],
    roots: [
      {
        word: "inspirare",
        language: "Latin",
        definition: "inflame, blow into",
        year: null,
        roots: [
          {
            word: "in",
            language: "Latin",
            definition: "in, into",
            year: null
          },
          {
            word: "spirare",
            language: "Latin",
            definition: "to breathe",
            year: null
          }
        ]
      }
    ]
  },
  {
    word: "important",
    language: "English",
    year: 1580,
    definition: "of great significance or value; likely to have a profound effect",
    etymology: [
      {
        word: "important",
        language: "French",
        year: 1500,
        definition: "significant, of consequence"
      }
    ],
    roots: [
      {
        word: "importantem",
        language: "Latin",
        definition: "being of consequence",
        year: null,
        roots: [
          {
            word: "importare",
            language: "Latin",
            definition: "bring in, convey, bring about",
            year: null,
            roots: [
              {
                word: "in",
                language: "Latin",
                definition: "in, into",
                year: null
              },
              {
                word: "portare",
                language: "Latin",
                definition: "to carry",
                year: null
              }
            ]
          }
        ]
      }
    ]
  }
];

// Add more words
moreWords.push(...secondBatch);

// Final batch to reach our goal
const finalBatch = [
  // J words
  {
    word: "joy",
    language: "English",
    year: 1200,
    definition: "a feeling of great pleasure and happiness",
    etymology: [
      {
        word: "joie",
        language: "French",
        year: 1100,
        definition: "pleasure, delight, erotic pleasure, bliss"
      }
    ],
    roots: [
      {
        word: "gaudia",
        language: "Latin",
        definition: "joy",
        year: null,
        roots: [
          {
            word: "gaudere",
            language: "Latin",
            definition: "to rejoice",
            year: null
          }
        ]
      }
    ]
  },
  
  // K words
  {
    word: "key",
    language: "English",
    year: 1100,
    definition: "a small piece of shaped metal with incisions cut to fit the wards of a particular lock",
    etymology: [
      {
        word: "cæg",
        language: "Old English",
        year: 800,
        definition: "key, solution"
      }
    ],
    roots: [
      {
        word: "caega",
        language: "Proto-Germanic",
        definition: "key",
        year: null,
        roots: []
      }
    ]
  },
  
  // L words
  {
    word: "literature",
    language: "English",
    year: 1375,
    definition: "written works, especially those considered of superior or lasting artistic merit",
    etymology: [
      {
        word: "litterature",
        language: "French",
        year: 1300,
        definition: "book-learning"
      }
    ],
    roots: [
      {
        word: "literatura",
        language: "Latin",
        definition: "learning, a writing, grammar",
        year: null,
        roots: [
          {
            word: "littera",
            language: "Latin",
            definition: "letter",
            year: null
          }
        ]
      }
    ]
  },
  {
    word: "learning",
    language: "English",
    year: 1000,
    definition: "the acquisition of knowledge or skills through experience, study, or being taught",
    etymology: [
      {
        word: "leornung",
        language: "Old English",
        year: 900,
        definition: "learning, study"
      }
    ],
    roots: [
      {
        word: "leornian",
        language: "Old English",
        definition: "to acquire knowledge",
        year: null,
        roots: []
      }
    ]
  },
  
  // M words
  {
    word: "mystery",
    language: "English",
    year: 1350,
    definition: "something that is difficult or impossible to understand or explain",
    etymology: [
      {
        word: "mystere",
        language: "French",
        year: 1300,
        definition: "secret rites, secret, religious mystery"
      }
    ],
    roots: [
      {
        word: "mysterium",
        language: "Latin",
        definition: "secret rite, secret worship",
        year: null,
        roots: [
          {
            word: "mysterion",
            language: "Greek",
            definition: "secret rite or doctrine",
            year: null,
            roots: [
              {
                word: "mystes",
                language: "Greek",
                definition: "one who has been initiated",
                year: null
              }
            ]
          }
        ]
      }
    ]
  },
  {
    word: "music",
    language: "English",
    year: 1200,
    definition: "vocal or instrumental sounds combined in such a way as to produce beauty of form, harmony, and expression of emotion",
    etymology: [
      {
        word: "musique",
        language: "French",
        year: 1150,
        definition: "art, sound, or poetry of the muses"
      }
    ],
    roots: [
      {
        word: "musica",
        language: "Latin",
        definition: "the art of music",
        year: null,
        roots: [
          {
            word: "mousike",
            language: "Greek",
            definition: "art of the Muses",
            year: null,
            roots: [
              {
                word: "mousa",
                language: "Greek",
                definition: "Muse",
                year: null
              }
            ]
          }
        ]
      }
    ]
  },
  
  // N words
  {
    word: "nostalgia",
    language: "English",
    year: 1770,
    definition: "a sentimental longing or wistful affection for the past",
    etymology: [
      {
        word: "nostalgia",
        language: "New Latin",
        year: 1688,
        definition: "homesickness, acute longing for familiar surroundings"
      }
    ],
    roots: [
      {
        word: "nostos",
        language: "Greek",
        definition: "homecoming",
        year: null,
        roots: []
      },
      {
        word: "algos",
        language: "Greek",
        definition: "pain, grief, distress",
        year: null,
        roots: []
      }
    ]
  }
];

// Add the final batch
moreWords.push(...finalBatch);

// Add a few more to complete our set
const completionBatch = [
  // O words
  {
    word: "orchestra",
    language: "English",
    year: 1600,
    definition: "a group of musicians playing various instruments together",
    etymology: [
      {
        word: "orchestra",
        language: "Latin",
        year: null,
        definition: "area for the chorus in a theater"
      }
    ],
    roots: [
      {
        word: "orkestra",
        language: "Greek",
        definition: "area for the chorus",
        year: null,
        roots: [
          {
            word: "orkheisthai",
            language: "Greek",
            definition: "to dance",
            year: null
          }
        ]
      }
    ]
  },
  
  // P words
  {
    word: "psychology",
    language: "English",
    year: 1748,
    definition: "the scientific study of the human mind and its functions",
    etymology: [
      {
        word: "psychologia",
        language: "Latin",
        year: 1580,
        definition: "study of the soul"
      }
    ],
    roots: [
      {
        word: "psykhe",
        language: "Greek",
        definition: "soul, mind, spirit",
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
  
  // Q words
  {
    word: "quest",
    language: "English", 
    year: 1300,
    definition: "a long or arduous search for something",
    etymology: [
      {
        word: "queste",
        language: "French",
        year: 1250,
        definition: "search, quest, chase, hunt"
      }
    ],
    roots: [
      {
        word: "quaerere",
        language: "Latin",
        definition: "to ask, seek",
        year: null,
        roots: []
      }
    ]
  },
  
  // R words
  {
    word: "reason",
    language: "English",
    year: 1225,
    definition: "the power of the mind to think, understand, and form judgments by a process of logic",
    etymology: [
      {
        word: "raison",
        language: "French",
        year: 1200,
        definition: "course of action, affair, matter"
      }
    ],
    roots: [
      {
        word: "rationem",
        language: "Latin", 
        definition: "reckoning, calculation, reason",
        year: null,
        roots: [
          {
            word: "ratus",
            language: "Latin",
            definition: "reckoned, calculated",
            year: null,
            roots: [
              {
                word: "reri",
                language: "Latin",
                definition: "to reckon, believe, think",
                year: null
              }
            ]
          }
        ]
      }
    ]
  },
  
  // S words
  {
    word: "symphony",
    language: "English",
    year: 1600,
    definition: "an elaborate musical composition for full orchestra",
    etymology: [
      {
        word: "symphonie",
        language: "French",
        year: 1300,
        definition: "harmony of sounds"
      }
    ],
    roots: [
      {
        word: "symphonia",
        language: "Greek",
        definition: "harmony, concert",
        year: null,
        roots: [
          {
            word: "sym",
            language: "Greek",
            definition: "together",
            year: null
          },
          {
            word: "phone",
            language: "Greek",
            definition: "sound, voice",
            year: null
          }
        ]
      }
    ]
  }
];

// Add the completion batch
moreWords.push(...completionBatch);

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
moreWords.forEach(word => {
  const firstLetter = word.word.charAt(0).toLowerCase();
  const dirPath = `data/words/${word.language}/${firstLetter}`;
  
  ensureDirectoryExists(dirPath);
  
  const filePath = path.join(dirPath, `${word.word.toLowerCase()}.json`);
  fs.writeFileSync(filePath, JSON.stringify(word, null, 2));
  
  console.log(`Created ${filePath}`);
});

console.log(`Successfully created ${moreWords.length} additional etymology files.`); 