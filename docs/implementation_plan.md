# TransRapport Speaker Diarization Implementation Plan

## Executive Summary

Integration von TRAPV4-style Speaker Recognition in das bestehende TransRapport marker_system.py mit Fokus auf Echtzeitfähigkeit und therapeutische Genauigkeit.

## Phase 1: Grundlegende Speaker Diarization Integration (Woche 1-2)

### 1.1 Dependencies und Setup

```python
# Neue Abhängigkeiten zu requirements.txt hinzufügen
pyannote.audio>=3.1.0
torch>=2.0.0
torchaudio>=2.0.0
speechbrain>=1.0.3  # bereits vorhanden
scikit-learn>=1.3.0  # bereits vorhanden als 1.7.2
```

### 1.2 Basis Speaker Recognition Klasse

**Neue Datei:** `/src/speaker_recognition.py`

```python
class SpeakerRecognitionSystem:
    """
    TRAPV4-inspirierte Speaker Recognition für therapeutische Anwendungen
    Priorität: Real-time Performance + Therapeutische Genauigkeit
    """
    
    def __init__(self, 
                 embedding_model="speechbrain/spkrec-ecapa-voxceleb",
                 clustering_threshold=0.7,
                 min_segment_duration=1.0,
                 max_speakers=4):
        # ECAPA-TDNN Embedding Model
        # Online Clustering Parameter
        # VAD Integration
        # Speaker Enrollment System
        
    def extract_speaker_embedding(self, audio_chunk: np.ndarray) -> np.ndarray:
        """ECAPA-TDNN basierte Embedding-Extraktion"""
        
    def online_clustering(self, embedding: np.ndarray, timestamp: float) -> int:
        """Real-time Clustering mit adaptive threshold"""
        
    def enroll_speaker(self, speaker_id: str, audio_samples: List[np.ndarray]):
        """Speaker Enrollment für bekannte Therapeut/Patient"""
```

### 1.3 marker_system.py Integration

**Erweiterte Marker-Struktur:**
```python
self.current_markers = {
    'timestamp': None,
    'speaker': {
        'speaker_id': 0,
        'confidence': 0.0,
        'is_enrolled': False,
        'speaker_type': 'unknown'  # 'therapist', 'patient', 'unknown'
    },
    'affect': {...},  # Bestehend, jetzt pro Speaker
    'tempo': {...},   # Bestehend, jetzt pro Speaker
    'prosody': {...}  # Bestehend, jetzt pro Speaker
}
```

## Phase 2: Real-time Online Clustering (Woche 3-4)

### 2.1 Adaptive Clustering Algorithm

**Inspiriert von TRAPV4, optimiert für Therapie:**

```python
class OnlineSpeakerCluster:
    """
    Online Clustering mit therapeutischen Anpassungen
    """
    
    def __init__(self, 
                 tau=0.7,              # Clustering threshold (experimentell angepasst)
                 stickiness_delta=0.1,  # Speaker consistency bonus
                 momentum=0.9,          # Cluster center momentum
                 max_silence_gap=3.0):  # Therapie-spezifisch
        
    def update_cluster(self, embedding, speaker_history):
        """
        Online clustering mit:
        - Momentum-basierte cluster center updates
        - Stickiness für Speaker-Konsistenz
        - Adaptive threshold basierend auf confidence
        """
        
    def handle_overlapping_speech(self, embeddings_list):
        """Überlappende Sprache in Therapiesitzungen"""
```

### 2.2 VAD Integration Enhancement

**Erweiterte VAD-Integration in audio.py:**
```python
class EnhancedVAD:
    """
    Erweiterte VAD mit Speaker-awareness
    """
    
    def __init__(self):
        self.webrtc_vad = webrtcvad.Vad(2)  # Bestehend
        self.speaker_vad_history = {}       # Neu: Pro-Speaker VAD
        
    def speaker_aware_vad(self, audio_chunk, speaker_embedding):
        """VAD mit Speaker-spezifischen Schwellenwerten"""
```

## Phase 3: Therapeutische Optimierungen (Woche 5-6)

### 3.1 Speaker Enrollment System

**Therapeut/Patient Identifikation:**
```python
class TherapeuticSpeakerEnrollment:
    """
    Speaker Enrollment speziell für therapeutische Sitzungen
    """
    
    def __init__(self):
        self.enrolled_speakers = {
            'therapist': None,
            'patient': None
        }
        
    def enroll_from_session_start(self, audio_segments):
        """
        Automatische Enrollement basierend auf:
        - Sprechmuster (Therapeut = mehr Fragen)
        - Sprechdauer-Verhältnis
        - Prosodische Marker
        """
        
    def verify_speaker_consistency(self, current_embedding, speaker_history):
        """Konsistenz-Prüfung zur Vermeidung von ID-Switches"""
```

### 3.2 Pro-Speaker Emotion Analysis

**Erweiterte Emotionserkennung:**
```python
def _analyze_emotion_per_speaker(self, audio_segment, speaker_id):
    """
    Speaker-spezifische Emotionsanalyse:
    - Individualisierte Baseline pro Speaker
    - Therapeut vs Patient unterschiedliche Schwellenwerte
    - Adaptive Kalibrierung über Session-Zeit
    """
```

## Phase 4: Performance Optimierung (Woche 7-8)

### 4.1 Real-time Optimierungen

**Memory und Speed Optimierungen:**
```python
class OptimizedSpeakerSystem:
    """
    Performance-optimierte Implementierung
    """
    
    def __init__(self):
        # Model Quantization für ECAPA-TDNN
        self.embedding_model = self.load_quantized_model()
        
        # Sliding Window für Embeddings (Memory-efficient)
        self.embedding_buffer = collections.deque(maxlen=100)
        
        # Async Processing für Non-blocking inference
        self.async_processor = AsyncProcessor()
        
    def batched_embedding_extraction(self, audio_chunks):
        """Batch processing für bessere GPU-Utilization"""
        
    def incremental_clustering_update(self, new_embedding):
        """Incremental updates statt full re-clustering"""
```

### 4.2 Caching und Pre-computation

```python
class SpeakerCache:
    """
    Intelligent Caching für Speaker Recognition
    """
    
    def __init__(self):
        self.speaker_templates = {}  # Pre-computed speaker centroids
        self.embedding_cache = {}    # Recently computed embeddings
        
    def warm_up_cache(self, known_speakers):
        """Pre-compute häufig verwendete Embeddings"""
```

## Phase 5: Integration und Testing (Woche 9-10)

### 5.1 Vollständige marker_system.py Integration

**Erweiterte process_audio_chunk Methode:**
```python
def process_audio_chunk(self, audio_data: np.ndarray, timestamp: datetime = None) -> Dict:
    """
    Erweiterte Audio-Verarbeitung mit Speaker Recognition:
    
    1. Audio preprocessing
    2. VAD (bestehend)
    3. Speaker embedding extraction (NEU)
    4. Online clustering (NEU) 
    5. Speaker identification (NEU)
    6. Pro-Speaker emotion analysis (ERWEITERT)
    7. Pro-Speaker prosody analysis (ERWEITERT)
    8. Marker aggregation und output
    """
```

### 5.2 Testing Framework

**Neue Datei:** `/tests/test_speaker_recognition.py`
```python
class TestSpeakerRecognition:
    """
    Comprehensive testing für Speaker Recognition
    """
    
    def test_real_time_performance(self):
        """Performance unter Real-time Bedingungen"""
        
    def test_therapeutic_scenarios(self):
        """Therapie-spezifische Szenarien"""
        
    def test_speaker_consistency(self):
        """Speaker-ID Konsistenz über Zeit"""
        
    def test_overlapping_speech(self):
        """Überlappende Sprache handling"""
```

## Hardware und Deployment Anforderungen

### Minimale Anforderungen:
- **GPU:** RTX 3060 (6GB VRAM) oder Apple M1/M2
- **RAM:** 16GB (für ECAPA-TDNN models)
- **CPU:** Multi-core für parallel processing

### Optimale Konfiguration:
- **GPU:** RTX 4060/4070 (8-12GB VRAM)
- **RAM:** 32GB
- **Storage:** SSD für model loading

## Risiken und Mitigation

### Technische Risiken:
1. **Latenz:** ECAPA-TDNN inference Zeit
   - **Mitigation:** Model quantization, async processing
   
2. **Memory:** Large embedding models
   - **Mitigation:** Sliding windows, efficient caching
   
3. **Accuracy:** Speaker switches in therapeutischen Dialogen
   - **Mitigation:** Stickiness parameter, enrollment system

### Therapeutische Risiken:
1. **Falsche Speaker Attribution:** Kann Analyse verfälschen
   - **Mitigation:** Confidence thresholds, manual override
   
2. **Privacy:** Speaker identification data
   - **Mitigation:** Local processing, anonymized IDs

## Timeline und Meilensteine

| Woche | Meilenstein | Deliverable |
|-------|-------------|-------------|
| 1-2   | Basic Integration | SpeakerRecognitionSystem Klasse |
| 3-4   | Online Clustering | Real-time clustering algorithm |
| 5-6   | Therapeutic Features | Speaker enrollment, pro-speaker analysis |
| 7-8   | Optimization | Performance tuning, caching |
| 9-10  | Integration Testing | Vollständige marker_system.py Integration |

## Erfolgsmetriken

### Technische Metriken:
- **Real-time Factor:** <1.5x (Ziel: 1.2x)
- **Diarization Error Rate:** <8% (therapeutische Qualität)
- **Speaker ID Accuracy:** >95%
- **Memory Footprint:** <4GB during inference

### Therapeutische Metriken:
- **Speaker Consistency:** >98% (keine falschen Switches)
- **Emotion Attribution Accuracy:** >90% correct speaker
- **System Responsiveness:** <500ms marker updates

## Implementation Priority

### High Priority (Must-Have):
1. Basic ECAPA-TDNN integration
2. Real-time online clustering
3. VAD-Speaker integration
4. Pro-speaker emotion analysis

### Medium Priority (Should-Have):
1. Speaker enrollment system
2. Performance optimizations
3. Overlapping speech handling
4. Advanced caching

### Low Priority (Nice-to-Have):
1. Advanced clustering algorithms
2. Multi-modal speaker features
3. Cloud model alternatives
4. Advanced visualization