const fs = require('fs');
const path = require('path');

// Define final batch of words with their etymologies
const finalWords = [
  // T words
  {
    word: "tradition",
    language: "English",
    year: 1380,
    definition: "the transmission of customs or beliefs from generation to generation",
    etymology: [
      {
        word: "tradicion",
        language: "French",
        year: 1300,
        definition: "transmission, handing over"
      }
    ],
    roots: [
      {
        word: "traditionem",
        language: "Latin",
        definition: "delivery, surrender, a handing down",
        year: null,
        roots: [
          {
            word: "tradere",
            language: "Latin",
            definition: "to hand over, deliver, surrender",
            year: null,
            roots: [
              {
                word: "trans",
                language: "Latin",
                definition: "over, across",
                year: null
              },
              {
                word: "dare",
                language: "Latin",
                definition: "to give",
                year: null
              }
            ]
          }
        ]
      }
    ]
  },
  {
    word: "treasure",
    language: "English",
    year: 1200,
    definition: "valuable objects or money",
    etymology: [
      {
        word: "tresor",
        language: "French",
        year: 1150,
        definition: "treasury, treasure"
      }
    ],
    roots: [
      {
        word: "thesaurus",
        language: "Latin",
        definition: "treasury, storehouse",
        year: null,
        roots: [
          {
            word: "thesauros",
            language: "Greek",
            definition: "treasure, store, treasure house",
            year: null,
            roots: [
              {
                word: "tithenai",
                language: "Greek",
                definition: "to put, place",
                year: null
              }
            ]
          }
        ]
      }
    ]
  },
  
  // U words
  {
    word: "understand",
    language: "English",
    year: 900,
    definition: "perceive the meaning of; comprehend",
    etymology: [
      {
        word: "understandan",
        language: "Old English",
        year: 800,
        definition: "comprehend, grasp the idea of"
      }
    ],
    roots: [
      {
        word: "under",
        language: "Old English",
        definition: "among, between, under",
        year: null,
        roots: []
      },
      {
        word: "standan",
        language: "Old English",
        definition: "to stand",
        year: null,
        roots: []
      }
    ]
  },
  {
    word: "unity",
    language: "English",
    year: 1300,
    definition: "the state of being united or joined as a whole",
    etymology: [
      {
        word: "unite",
        language: "French",
        year: 1250,
        definition: "unity, agreement, oneness"
      }
    ],
    roots: [
      {
        word: "unitatem",
        language: "Latin",
        definition: "oneness, sameness, agreement",
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
    word: "vision",
    language: "English",
    year: 1290,
    definition: "the faculty or state of being able to see",
    etymology: [
      {
        word: "vision",
        language: "French",
        year: 1200,
        definition: "something seen in the imagination or in the supernatural"
      }
    ],
    roots: [
      {
        word: "visionem",
        language: "Latin",
        definition: "act of seeing, sight, thing seen",
        year: null,
        roots: [
          {
            word: "videre",
            language: "Latin",
            definition: "to see",
            year: null
          }
        ]
      }
    ]
  },
  {
    word: "voice",
    language: "English",
    year: 1290,
    definition: "the sound produced in a person's larynx and uttered through the mouth, as speech or song",
    etymology: [
      {
        word: "voiz",
        language: "French",
        year: 1200,
        definition: "voice, sound, noise"
      }
    ],
    roots: [
      {
        word: "vocem",
        language: "Latin",
        definition: "voice, sound, utterance, cry",
        year: null,
        roots: [
          {
            word: "vox",
            language: "Latin",
            definition: "voice",
            year: null
          }
        ]
      }
    ]
  },
  
  // W words
  {
    word: "wonder",
    language: "English",
    year: 900,
    definition: "a feeling of surprise mingled with admiration, caused by something beautiful, unexpected, unfamiliar, or inexplicable",
    etymology: [
      {
        word: "wundor",
        language: "Old English",
        year: 800,
        definition: "marvelous thing, marvel, surprise"
      }
    ],
    roots: [
      {
        word: "wundor",
        language: "Proto-Germanic",
        definition: "wonder",
        year: null,
        roots: []
      }
    ]
  },
  {
    word: "world",
    language: "English",
    year: 900,
    definition: "the earth, together with all of its countries, peoples, and natural features",
    etymology: [
      {
        word: "woruld",
        language: "Old English",
        year: 800,
        definition: "human existence, the affairs of life"
      }
    ],
    roots: [
      {
        word: "weraldi",
        language: "Proto-Germanic",
        definition: "age of man",
        year: null,
        roots: [
          {
            word: "wer",
            language: "Proto-Germanic",
            definition: "man",
            year: null
          },
          {
            word: "ald",
            language: "Proto-Germanic",
            definition: "age",
            year: null
          }
        ]
      }
    ]
  },
  
  // X words
  {
    word: "xylophone",
    language: "English",
    year: 1866,
    definition: "a musical instrument played by striking a row of wooden bars of graduated length with one or more small wooden or plastic mallets",
    etymology: [
      {
        word: "xylophon",
        language: "German",
        year: 1800,
        definition: "xylophone"
      }
    ],
    roots: [
      {
        word: "xylon",
        language: "Greek",
        definition: "wood",
        year: null,
        roots: []
      },
      {
        word: "phone",
        language: "Greek",
        definition: "voice, sound",
        year: null,
        roots: []
      }
    ]
  },
  
  // Y words
  {
    word: "youth",
    language: "English",
    year: 900,
    definition: "the period between childhood and adult age",
    etymology: [
      {
        word: "geoguth",
        language: "Old English",
        year: 800,
        definition: "youth, young people"
      }
    ],
    roots: [
      {
        word: "juwunthiz",
        language: "Proto-Germanic",
        definition: "youth",
        year: null,
        roots: []
      }
    ]
  },
  
  // Z words
  {
    word: "zodiac",
    language: "English",
    year: 1390,
    definition: "a belt of the heavens divided into 12 equal parts, containing the constellations that the sun passes through in its apparent annual journey",
    etymology: [
      {
        word: "zodiaque",
        language: "French",
        year: 1350,
        definition: "zodiac"
      }
    ],
    roots: [
      {
        word: "zodiacus",
        language: "Latin",
        definition: "zodiac",
        year: null,
        roots: [
          {
            word: "zodiakos",
            language: "Greek",
            definition: "zodiac, circle of little animals",
            year: null,
            roots: [
              {
                word: "zodiakos kyklos",
                language: "Greek",
                definition: "zodiac circle",
                year: null,
                roots: [
                  {
                    word: "zoon",
                    language: "Greek",
                    definition: "animal",
                    year: null
                  }
                ]
              }
            ]
          }
        ]
      }
    ]
  },
  // A words
  {
    word: "ancient",
    language: "English",
    year: 1380,
    definition: "belonging to the very distant past and no longer in existence",
    etymology: [
      {
        word: "ancien",
        language: "French",
        year: 1200,
        definition: "old, ancient, former, bygone"
      }
    ],
    roots: [
      {
        word: "anteanus",
        language: "Latin",
        definition: "ancient, former",
        year: null,
        roots: [
          {
            word: "ante",
            language: "Latin",
            definition: "before, in front of",
            year: null
          }
        ]
      }
    ]
  },
  // B words
  {
    word: "balance",
    language: "English",
    year: 1275,
    definition: "an even distribution of weight enabling someone or something to remain upright and steady",
    etymology: [
      {
        word: "balance",
        language: "French",
        year: 1200,
        definition: "scales, weighing device"
      }
    ],
    roots: [
      {
        word: "bilancem",
        language: "Latin",
        definition: "having two scales",
        year: null,
        roots: [
          {
            word: "bi",
            language: "Latin",
            definition: "two",
            year: null
          },
          {
            word: "lanx",
            language: "Latin",
            definition: "plate, scale",
            year: null
          }
        ]
      }
    ]
  },
  // C words
  {
    word: "curiosity",
    language: "English",
    year: 1380,
    definition: "a strong desire to know or learn something",
    etymology: [
      {
        word: "curiosite",
        language: "French",
        year: 1300,
        definition: "desire to know, inquisitiveness"
      }
    ],
    roots: [
      {
        word: "curiositatem",
        language: "Latin",
        definition: "desire of knowledge, inquisitiveness",
        year: null,
        roots: [
          {
            word: "curiosus",
            language: "Latin",
            definition: "careful, diligent",
            year: null,
            roots: [
              {
                word: "cura",
                language: "Latin",
                definition: "care, concern, trouble",
                year: null
              }
            ]
          }
        ]
      }
    ]
  }
];

// Additional words to reach 100+
const additionalWords = [
  // D words
  {
    word: "discovery",
    language: "English",
    year: 1550,
    definition: "the action or process of discovering or being discovered",
    etymology: [
      {
        word: "discoverie",
        language: "French",
        year: 1500,
        definition: "uncovering"
      }
    ],
    roots: [
      {
        word: "discover",
        language: "English",
        definition: "to find (something previously unseen or unknown)",
        year: 1300,
        roots: []
      }
    ]
  },
  // E words
  {
    word: "evolution",
    language: "English",
    year: 1620,
    definition: "the process by which different kinds of living organisms have developed from earlier forms",
    etymology: [
      {
        word: "evolution",
        language: "French",
        year: 1600,
        definition: "unrolling or opening of a book"
      }
    ],
    roots: [
      {
        word: "evolutionem",
        language: "Latin",
        definition: "unrolling (of a book)",
        year: null,
        roots: [
          {
            word: "evolvere",
            language: "Latin",
            definition: "to unroll, unfold",
            year: null,
            roots: [
              {
                word: "ex",
                language: "Latin",
                definition: "out",
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

// Add the additional words
finalWords.push(...additionalWords);

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
finalWords.forEach(word => {
  const firstLetter = word.word.charAt(0).toLowerCase();
  const dirPath = `data/words/${word.language}/${firstLetter}`;
  
  ensureDirectoryExists(dirPath);
  
  const filePath = path.join(dirPath, `${word.word.toLowerCase()}.json`);
  fs.writeFileSync(filePath, JSON.stringify(word, null, 2));
  
  console.log(`Created ${filePath}`);
});

console.log(`Successfully created ${finalWords.length} final etymology files.`); 