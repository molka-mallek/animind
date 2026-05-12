// ── category values used for filtering ──────────────────────────────────────
// 'pets'    → dogs, cats, eyes, skin
// 'poultry' → chickens, bird droppings
// 'livestock' → calves, fish
// 'wildlife'  → bird species, rabies
// 'neuro'     → behavioral / neurological

export const modules = [

  // ── AVAILABLE ────────────────────────────────────────────────────────────
  {
    id: 'dog-emotion',
    title: 'Dog Emotion Analysis',
    description: 'Upload a photo or video to detect your dog\'s emotional state — happy, sad, angry, relaxed, or fearful.',
    icon: '🐶',
    tag: 'Available',
    category: 'pets',
    route: '/modules/dog-emotion',
  },
  {
    id: 'eye-infection',
    title: 'Eye Infection Detection',
    description: 'Upload a clear eye photo to screen for possible eye infection signs in cats and dogs.',
    icon: '👁️',
    tag: 'Available',
    category: 'pets',
    route: '/modules/eye-infection',
  },
  {
    id: 'skin-disease',
    title: 'Skin Anomaly Detection',
    description: 'Share a close-up photo and find out if your cat or dog has a skin anomaly — with affected area highlighted.',
    icon: '🔬',
    tag: 'Available',
    category: 'pets',
    route: '/modules/skin-anomaly',
  },
  {
    id: 'behavioral-disease',
    title: 'Behavioral Disease Detection',
    description: 'Detect potential behavioral disorders or neurological issues in dogs and cats via video analysis.',
    icon: '🧠',
    tag: 'Available',
    category: 'neuro',
    route: '/modules/behavioral-disease',
  },
  {
    id: 'chicken-fowlpox',
    title: 'Chicken Fowlpox Detection',
    description: 'Upload a clear chicken photo to screen for possible fowlpox symptoms.',
    icon: '🐔',
    tag: 'Available',
    category: 'poultry',
    route: '/modules/chicken-fowlpox',
  },
  {
    id: 'bird-droppings',
    title: 'Bird Droppings Analysis',
    description: 'Upload a droppings image to screen for signs of possible infection in poultry.',
    icon: '🧪',
    tag: 'Available',
    category: 'poultry',
    route: '/modules/bird-droppings',
  },
  {
    id: 'calf-behavior',
    title: 'Real-Time Calf Monitoring',
    description: 'Live behavioral analysis from sensor data — detect if your calf is eating, resting, active, or showing unusual patterns.',
    icon: '🐄',
    tag: 'Available',
    category: 'livestock',
    route: null,
    external: 'http://localhost:8501',
  },
  {
    id: 'fish-freshness',
    title: 'Fish Freshness Analysis',
    description: 'Upload a fish photo and get an instant freshness score (0–100) with a quality grade (C1/C2/C3) and actionable insights.',
    icon: '🐟',
    tag: 'Available',
    category: 'livestock',
    route: '/modules/fish-freshness',
  },
  {
    id: 'rabies',
    title: 'Rabies Detection',
    description: 'Upload a clear animal photo to screen for rabies-related symptoms and get a confidence score.',
    icon: '🧬',
    tag: 'Available',
    category: 'wildlife',
    route: '/rabies',
  },
  {
    id: 'bird-species',
    title: 'Bird Species Classification',
    description: 'Upload a bird audio recording and our AI identifies the species from its song using mel-spectrogram analysis.',
    icon: '🎵',
    tag: 'Available',
    category: 'wildlife',
    route: '/modules/bird-species',
  },

  {
    id: 'cat-sound',
    title: 'Cat Vocalization Classification',
    description: 'Upload a cat audio recording to classify vocalizations into 10 behavioral categories — with clinical pain detection alerts.',
    icon: '🔊',
    tag: 'Available',
    category: 'pets',
    route: '/modules/cat-sound',
  },
  {
    id: 'horse-pain',
    title: 'Horse Pain Detection',
    description: 'Upload a horse video to detect pain indicators through BiLSTM behavioral analysis of movement patterns.',
    icon: '🐴',
    tag: 'Available',
    category: 'livestock',
    route: '/modules/horse-pain',
  },
  {
    id: 'thermal-cat',
    title: 'Thermal Cat Classification',
    description: 'Upload a thermal image of your cat to screen for health issues — ensemble AI detects Healthy vs Sick with high recall.',
    icon: '🌡️',
    tag: 'Available',
    category: 'pets',
    route: '/modules/thermal-cat',
  },

]

export const CATEGORIES = [
  { id: 'all',      label: 'All' },
  { id: 'pets',     label: '🐾 Pets' },
  { id: 'poultry',  label: '🐔 Poultry' },
  { id: 'livestock',label: '🐄 Livestock' },
  { id: 'wildlife', label: '🦜 Wildlife' },
  { id: 'neuro',    label: '🧠 Neurological' },
]
