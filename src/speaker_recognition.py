#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TransRapport - TRAPV4-Style Speaker Recognition System
ECAPA-TDNN based Speaker Diarization für therapeutische Anwendungen
Fokus: Real-time Performance + Therapeutische Genauigkeit
"""

import numpy as np
import torch
import threading
import queue
import collections
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from PyQt6.QtCore import QObject, pyqtSignal

# SpeechBrain für ECAPA-TDNN
try:
    from speechbrain.pretrained import EncoderClassifier
    SPEECHBRAIN_AVAILABLE = True
except ImportError:
    SPEECHBRAIN_AVAILABLE = False
    logging.warning("SpeechBrain nicht verfügbar - Speaker Recognition deaktiviert")

# Sklearn für Clustering
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity

@dataclass
class SpeakerProfile:
    """Speaker-Profil für therapeutische Sitzungen"""
    speaker_id: int
    speaker_type: str  # 'therapist', 'patient', 'unknown'
    enrollment_embeddings: List[np.ndarray]
    confidence_history: List[float]
    last_seen: datetime
    total_speaking_time: float
    average_embedding: Optional[np.ndarray] = None

class OnlineSpeakerCluster:
    """
    Online Clustering für Real-time Speaker Diarization
    TRAPV4-inspiriert mit therapeutischen Anpassungen
    """
    
    def __init__(self, 
                 tau: float = 0.7,              # Clustering threshold
                 stickiness_delta: float = 0.1,  # Speaker consistency bonus
                 momentum: float = 0.9,          # Cluster center momentum  
                 max_silence_gap: float = 3.0):  # Max gap before new speaker consideration
        
        self.tau = tau
        self.stickiness_delta = stickiness_delta
        self.momentum = momentum
        self.max_silence_gap = max_silence_gap
        
        # Cluster state
        self.cluster_centers = {}  # speaker_id -> embedding centroid
        self.speaker_profiles = {}  # speaker_id -> SpeakerProfile
        self.current_speaker = None
        self.last_speech_time = None
        self.next_speaker_id = 0
        
        # History für adaptive thresholds
        self.embedding_history = collections.deque(maxlen=100)
        self.confidence_history = collections.deque(maxlen=50)
        
    def update_cluster(self, embedding: np.ndarray, timestamp: datetime) -> Tuple[int, float]:
        """
        Online clustering update mit TRAPV4-style parameters
        
        Returns:
            (speaker_id, confidence)
        """
        # Normalisieren des embeddings
        embedding = embedding / np.linalg.norm(embedding)
        
        # Check for silence gap
        silence_gap = 0.0
        if self.last_speech_time:
            silence_gap = (timestamp - self.last_speech_time).total_seconds()
        
        # Berechne similarities zu bestehenden clustern
        similarities = {}
        for speaker_id, center in self.cluster_centers.items():
            sim = cosine_similarity([embedding], [center])[0][0]
            
            # Stickiness bonus für aktuellen Speaker (außer bei langen Pausen)
            if (speaker_id == self.current_speaker and 
                silence_gap < self.max_silence_gap):
                sim += self.stickiness_delta
                
            similarities[speaker_id] = sim
        
        # Bestimme besten match
        if similarities:
            best_speaker = max(similarities.items(), key=lambda x: x[1])
            best_similarity = best_speaker[1]
            best_speaker_id = best_speaker[0]
            
            # Adaptive threshold basierend auf history
            adaptive_tau = self._get_adaptive_threshold()
            
            if best_similarity > adaptive_tau:
                # Assign zu bestehendem Speaker
                self._update_cluster_center(best_speaker_id, embedding)
                self.current_speaker = best_speaker_id
                confidence = min(best_similarity, 1.0)
            else:
                # Neuer Speaker
                new_speaker_id = self._create_new_speaker(embedding, timestamp)
                self.current_speaker = new_speaker_id
                confidence = 0.5  # Initial confidence für neuen Speaker
        else:
            # Erster Speaker
            new_speaker_id = self._create_new_speaker(embedding, timestamp)
            self.current_speaker = new_speaker_id
            confidence = 0.8
        
        # Update history
        self.embedding_history.append(embedding)
        self.confidence_history.append(confidence)
        self.last_speech_time = timestamp
        
        # Update speaker profile
        if self.current_speaker in self.speaker_profiles:
            profile = self.speaker_profiles[self.current_speaker]
            profile.confidence_history.append(confidence)
            profile.last_seen = timestamp
        
        return self.current_speaker, confidence
    
    def _get_adaptive_threshold(self) -> float:
        """Adaptive threshold basierend auf recent performance"""
        if len(self.confidence_history) < 5:
            return self.tau
        
        # Höhere threshold wenn confidence history gut ist
        avg_confidence = np.mean(list(self.confidence_history)[-10:])
        if avg_confidence > 0.8:
            return self.tau + 0.05
        elif avg_confidence < 0.6:
            return self.tau - 0.05
        else:
            return self.tau
    
    def _update_cluster_center(self, speaker_id: int, new_embedding: np.ndarray):
        """Update cluster center mit momentum"""
        if speaker_id in self.cluster_centers:
            old_center = self.cluster_centers[speaker_id]
            new_center = (self.momentum * old_center + 
                         (1 - self.momentum) * new_embedding)
            self.cluster_centers[speaker_id] = new_center / np.linalg.norm(new_center)
        else:
            self.cluster_centers[speaker_id] = new_embedding
    
    def _create_new_speaker(self, embedding: np.ndarray, timestamp: datetime) -> int:
        """Erstelle neuen Speaker"""
        speaker_id = self.next_speaker_id
        self.next_speaker_id += 1
        
        # Initialize cluster center
        self.cluster_centers[speaker_id] = embedding
        
        # Create speaker profile
        profile = SpeakerProfile(
            speaker_id=speaker_id,
            speaker_type='unknown',
            enrollment_embeddings=[embedding],
            confidence_history=[0.8],
            last_seen=timestamp,
            total_speaking_time=0.0,
            average_embedding=embedding
        )
        self.speaker_profiles[speaker_id] = profile
        
        return speaker_id
    
    def get_speaker_profiles(self) -> Dict[int, SpeakerProfile]:
        """Aktuelle Speaker-Profile abrufen"""
        return self.speaker_profiles.copy()

class SpeakerRecognitionSystem(QObject):
    """
    TRAPV4-inspirierte Speaker Recognition für therapeutische Anwendungen
    Integration mit TransRapport marker_system.py
    """
    
    # Qt Signale
    speaker_detected = pyqtSignal(int, float, str)  # speaker_id, confidence, speaker_type
    speaker_enrolled = pyqtSignal(int, str)         # speaker_id, speaker_type
    speaker_changed = pyqtSignal(int, int)          # old_speaker_id, new_speaker_id
    
    def __init__(self, 
                 embedding_model: str = "speechbrain/spkrec-ecapa-voxceleb",
                 clustering_threshold: float = 0.7,
                 min_segment_duration: float = 1.0,
                 max_speakers: int = 4,
                 sample_rate: int = 16000):
        super().__init__()
        
        self.embedding_model_name = embedding_model
        self.clustering_threshold = clustering_threshold
        self.min_segment_duration = min_segment_duration
        self.max_speakers = max_speakers
        self.sample_rate = sample_rate
        
        # Model loading
        self.embedding_model = None
        self.is_model_loaded = False
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Online clustering
        self.online_cluster = OnlineSpeakerCluster(
            tau=clustering_threshold,
            stickiness_delta=0.1,
            momentum=0.9,
            max_silence_gap=3.0
        )
        
        # Audio buffer für embeddings
        self.audio_buffer = collections.deque(maxlen=1000)
        self.embedding_buffer = collections.deque(maxlen=100)
        
        # Threading für async processing
        self.processing_queue = queue.Queue(maxsize=50)
        self.is_processing = False
        self.processing_thread = None
        
        # Speaker enrollment
        self.enrolled_speakers = {
            'therapist': None,
            'patient': None
        }
        
        # Performance monitoring
        self.processing_times = collections.deque(maxlen=100)
        
        self._initialize_model()
    
    def _initialize_model(self):
        """ECAPA-TDNN Model initialization"""
        if not SPEECHBRAIN_AVAILABLE:
            logging.error("SpeechBrain nicht verfügbar - Speaker Recognition deaktiviert")
            return
        
        try:
            logging.info(f"Lade ECAPA-TDNN Model: {self.embedding_model_name}")
            self.embedding_model = EncoderClassifier.from_hparams(
                source=self.embedding_model_name,
                savedir=f"models/{self.embedding_model_name.split('/')[-1]}",
                run_opts={"device": self.device}
            )
            self.is_model_loaded = True
            logging.info("ECAPA-TDNN Model erfolgreich geladen")
            
        except Exception as e:
            logging.error(f"Fehler beim Laden des ECAPA-TDNN Models: {e}")
            self.is_model_loaded = False
    
    def start_processing(self):
        """Start async processing thread"""
        if not self.is_model_loaded:
            logging.warning("Model nicht geladen - Speaker Recognition nicht verfügbar")
            return False
        
        if self.is_processing:
            return True
        
        self.is_processing = True
        self.processing_thread = threading.Thread(target=self._processing_loop)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        
        logging.info("Speaker Recognition Processing gestartet")
        return True
    
    def stop_processing(self):
        """Stop processing thread"""
        if not self.is_processing:
            return
        
        self.is_processing = False
        if self.processing_thread:
            self.processing_thread.join(timeout=2.0)
        
        # Clear queues
        while not self.processing_queue.empty():
            try:
                self.processing_queue.get_nowait()
            except queue.Empty:
                break
        
        logging.info("Speaker Recognition Processing gestoppt")
    
    def process_audio_chunk(self, audio_data: np.ndarray, timestamp: datetime = None) -> Dict:
        """
        Process audio chunk für Speaker Recognition
        
        Returns:
            Dict mit Speaker-Informationen
        """
        if not self.is_model_loaded or not self.is_processing:
            return self._get_default_speaker_data()
        
        if timestamp is None:
            timestamp = datetime.now()
        
        # Audio zu processing queue hinzufügen (non-blocking)
        try:
            self.processing_queue.put_nowait((audio_data.copy(), timestamp))
        except queue.Full:
            # Queue voll - ältesten eintrag entfernen
            try:
                self.processing_queue.get_nowait()
                self.processing_queue.put_nowait((audio_data.copy(), timestamp))
            except queue.Empty:
                pass
        
        # Aktuelle Speaker-Info zurückgeben
        return self._get_current_speaker_data()
    
    def _processing_loop(self):
        """Async processing loop für Speaker Recognition"""
        while self.is_processing:
            try:
                # Audio data aus queue abrufen
                audio_data, timestamp = self.processing_queue.get(timeout=0.1)
                
                # Speaker embedding extrahieren
                start_time = datetime.now()
                embedding = self._extract_speaker_embedding(audio_data)
                
                if embedding is not None:
                    # Online clustering
                    speaker_id, confidence = self.online_cluster.update_cluster(
                        embedding, timestamp
                    )
                    
                    # Speaker type determination
                    speaker_type = self._determine_speaker_type(speaker_id)
                    
                    # Signal senden
                    self.speaker_detected.emit(speaker_id, confidence, speaker_type)
                    
                    # Performance monitoring
                    processing_time = (datetime.now() - start_time).total_seconds()
                    self.processing_times.append(processing_time)
                
            except queue.Empty:
                continue
            except Exception as e:
                logging.error(f"Fehler in Speaker Recognition processing loop: {e}")
    
    def _extract_speaker_embedding(self, audio_data: np.ndarray) -> Optional[np.ndarray]:
        """ECAPA-TDNN Embedding extraction"""
        try:
            # Audio preprocessing
            if len(audio_data) < self.sample_rate * self.min_segment_duration:
                return None  # Zu kurzes segment
            
            # Ensure correct format
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)
            
            # Normalize
            audio_data = audio_data / np.max(np.abs(audio_data))
            
            # Convert to tensor
            audio_tensor = torch.tensor(audio_data).unsqueeze(0).to(self.device)
            
            # Extract embedding
            with torch.no_grad():
                embedding = self.embedding_model.encode_batch(audio_tensor)
                embedding = embedding.squeeze().cpu().numpy()
            
            return embedding
            
        except Exception as e:
            logging.error(f"Fehler bei Embedding-Extraktion: {e}")
            return None
    
    def _determine_speaker_type(self, speaker_id: int) -> str:
        """Bestimme Speaker-Type basierend auf patterns"""
        if speaker_id in self.online_cluster.speaker_profiles:
            profile = self.online_cluster.speaker_profiles[speaker_id]
            
            # Check enrolled speakers
            for speaker_type, enrolled_id in self.enrolled_speakers.items():
                if enrolled_id == speaker_id:
                    profile.speaker_type = speaker_type
                    return speaker_type
            
            # Heuristic basierend auf speaking patterns
            if profile.total_speaking_time > 30.0:  # Viel geredet = wahrscheinlich Therapeut
                if len(profile.confidence_history) > 10:
                    avg_confidence = np.mean(profile.confidence_history[-10:])
                    if avg_confidence > 0.8:
                        return 'therapist'
            
            return 'unknown'
        
        return 'unknown'
    
    def enroll_speaker(self, speaker_type: str, audio_samples: List[np.ndarray]) -> bool:
        """
        Speaker Enrollment für bekannte Therapeut/Patient
        
        Args:
            speaker_type: 'therapist' oder 'patient'
            audio_samples: List von audio chunks für enrollment
        """
        if not self.is_model_loaded:
            return False
        
        try:
            # Extract embeddings aus allen samples
            embeddings = []
            for audio_sample in audio_samples:
                embedding = self._extract_speaker_embedding(audio_sample)
                if embedding is not None:
                    embeddings.append(embedding)
            
            if len(embeddings) < 2:
                logging.warning(f"Nicht genug gültige embeddings für {speaker_type} enrollment")
                return False
            
            # Durchschnitts-embedding berechnen
            avg_embedding = np.mean(embeddings, axis=0)
            avg_embedding = avg_embedding / np.linalg.norm(avg_embedding)
            
            # Finde oder erstelle Speaker
            speaker_id = self._find_or_create_enrolled_speaker(
                avg_embedding, speaker_type, embeddings
            )
            
            # Update enrollment
            self.enrolled_speakers[speaker_type] = speaker_id
            
            # Signal senden
            self.speaker_enrolled.emit(speaker_id, speaker_type)
            
            logging.info(f"Speaker enrollment erfolgreich: {speaker_type} -> ID {speaker_id}")
            return True
            
        except Exception as e:
            logging.error(f"Fehler bei Speaker enrollment: {e}")
            return False
    
    def _find_or_create_enrolled_speaker(self, avg_embedding: np.ndarray, 
                                       speaker_type: str, 
                                       embeddings: List[np.ndarray]) -> int:
        """Finde bestehenden oder erstelle neuen enrolled speaker"""
        # Check existing speakers
        best_match = None
        best_similarity = 0.0
        
        for speaker_id, center in self.online_cluster.cluster_centers.items():
            similarity = cosine_similarity([avg_embedding], [center])[0][0]
            if similarity > best_similarity and similarity > 0.8:  # High threshold für enrollment
                best_similarity = similarity
                best_match = speaker_id
        
        if best_match is not None:
            # Update existing speaker
            profile = self.online_cluster.speaker_profiles[best_match]
            profile.speaker_type = speaker_type
            profile.enrollment_embeddings.extend(embeddings)
            profile.average_embedding = avg_embedding
            return best_match
        else:
            # Create new speaker
            timestamp = datetime.now()
            speaker_id = self.online_cluster._create_new_speaker(avg_embedding, timestamp)
            profile = self.online_cluster.speaker_profiles[speaker_id]
            profile.speaker_type = speaker_type
            profile.enrollment_embeddings = embeddings
            profile.average_embedding = avg_embedding
            return speaker_id
    
    def get_current_speaker_data(self) -> Dict:
        """Aktuelle Speaker-Daten für marker_system.py"""
        return self._get_current_speaker_data()
    
    def _get_current_speaker_data(self) -> Dict:
        """Internal method für aktuelle Speaker-Daten"""
        current_speaker = self.online_cluster.current_speaker
        
        if current_speaker is not None and current_speaker in self.online_cluster.speaker_profiles:
            profile = self.online_cluster.speaker_profiles[current_speaker]
            confidence = np.mean(profile.confidence_history[-5:]) if profile.confidence_history else 0.0
            
            return {
                'speaker_id': current_speaker,
                'confidence': float(confidence),
                'speaker_type': profile.speaker_type,
                'is_enrolled': profile.speaker_type in ['therapist', 'patient'],
                'total_speakers': len(self.online_cluster.speaker_profiles)
            }
        else:
            return self._get_default_speaker_data()
    
    def _get_default_speaker_data(self) -> Dict:
        """Default Speaker-Daten wenn keine Recognition aktiv"""
        return {
            'speaker_id': 0,
            'confidence': 0.0,
            'speaker_type': 'unknown',
            'is_enrolled': False,
            'total_speakers': 0
        }
    
    def get_performance_stats(self) -> Dict:
        """Performance-Statistiken"""
        if not self.processing_times:
            return {'avg_processing_time': 0.0, 'max_processing_time': 0.0}
        
        times = list(self.processing_times)
        return {
            'avg_processing_time': np.mean(times),
            'max_processing_time': np.max(times),
            'min_processing_time': np.min(times),
            'processing_samples': len(times)
        }
    
    def is_real_time_capable(self) -> bool:
        """Check ob system real-time capable ist"""
        stats = self.get_performance_stats()
        if stats['avg_processing_time'] == 0.0:
            return False
        
        # Real-time wenn average processing time < 500ms
        return stats['avg_processing_time'] < 0.5
    
    def get_speaker_profiles(self) -> Dict[int, Dict]:
        """Speaker-Profile für UI/Analysis"""
        profiles = {}
        for speaker_id, profile in self.online_cluster.speaker_profiles.items():
            profiles[speaker_id] = {
                'speaker_id': profile.speaker_id,
                'speaker_type': profile.speaker_type,
                'confidence_avg': np.mean(profile.confidence_history) if profile.confidence_history else 0.0,
                'last_seen': profile.last_seen.isoformat() if profile.last_seen else None,
                'total_speaking_time': profile.total_speaking_time,
                'enrollment_samples': len(profile.enrollment_embeddings)
            }
        return profiles