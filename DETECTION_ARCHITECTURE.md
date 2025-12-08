# SpotBot Advanced Detection Architecture

## Multi-Method Detection System

SpotBot uses an **ensemble approach** combining multiple detection methods for maximum accuracy.

### Detection Methods - we should build more and more over time by reading research papers and doing esting, eventually traing models to identify other models

#### 1. **Metadata & Provenance Checks** (Highest Trust)
- **C2PA Content Credentials**: Cryptographically signed metadata
- **EXIF Data Analysis**: Camera/software fingerprints
- **Signed Manifests**: Tool-embedded provenance
- **Implementation**: `MetadataDetector` class
- **Confidence**: 90-100% when signatures verify

#### 2. **Watermark Detection** (High Trust)
- **Invisible Watermarks**: Statistical/frequency-domain analysis
- **Vendor Watermarks**: OpenAI, Google, Adobe watermarks
- **Tamper Detection**: Identify modified watermarks
- **Implementation**: `WatermarkDetector` class
- **Confidence**: 70-95% with known watermarks

#### 3. **ML Classifiers** (Medium-High Trust)
- **Sentence-Level**: BERT/RoBERTa fine-tuned for AI text
- **Document-Level**: Ensemble of multiple models
- **Log-Probability Analysis**: Statistical likelihood scoring
- **Stylometric Features**: Writing style fingerprinting
- **Implementation**: `MLDetector` class with model ensemble
- **Confidence**: 60-85% depending on text length

#### 4. **Fingerprint/Attribution Models** (Medium Trust)
- **Model-Specific Patterns**: GPT, Claude, Gemini, Llama signatures
- **Token Distribution**: N-gram analysis
- **Sampling Statistics**: Temperature/top-p detection
- **Instruction Artifacts**: Prompt leakage detection
- **Implementation**: `AttributionDetector` class (currently text_detector.py)
- **Confidence**: 40-70% for attribution

#### 5. **Content Source Matching** (For Human Content)
- **Web Retrieval**: Search engine queries for similar text
- **Plagiarism Detection**: Fuzzy matching algorithms
- **Academic Sources**: CrossRef, arXiv, PubMed search
- **Quote Attribution**: Exact phrase matching
- **Implementation**: `SourceMatchDetector` class
- **Confidence**: High for exact matches, lower for similarity

#### 6. **Multimodal Detection**
- **Images**: 
  - C2PA/EXIF analysis
  - GAN artifact detection
  - Reverse image search
  - AI-image classifiers (detect DALL-E, Midjourney, etc.)
- **Audio/Video**:
  - ASR → text analysis pipeline
  - Audio watermark detection
  - Spectrogram analysis for synthetic speech
  - Frame-level GAN detection
- **Implementation**: Separate detector classes per modality

## Detection Pipeline

```
Input Content
    ↓
┌───────────────────────────────────┐
│  1. Content Type Detection        │
│     (text/image/audio/video/url)  │
└───────────────────────────────────┘
    ↓
┌───────────────────────────────────┐
│  2. Metadata Analysis (C2PA)      │
│     ↓ If verified → HIGH TRUST    │
│     ↓ If missing → Continue       │
└───────────────────────────────────┘
    ↓
┌───────────────────────────────────┐
│  3. Watermark Detection           │
│     ↓ If detected → HIGH TRUST    │
│     ↓ If not found → Continue     │
└───────────────────────────────────┘
    ↓
┌───────────────────────────────────┐
│  4. ML Classifier Ensemble        │
│     • Run 3-5 different models    │
│     • Combine predictions         │
│     • Output: AI probability      │
└───────────────────────────────────┘
    ↓
┌───────────────────────────────────┐
│  5. Attribution Analysis          │
│     • If likely AI → Which model? │
│     • Pattern matching            │
│     • Output: Model + confidence  │
└───────────────────────────────────┘
    ↓
┌───────────────────────────────────┐
│  6. Source Matching (if human)    │
│     • Web search                  │
│     • Plagiarism check            │
│     • Output: Original sources    │
└───────────────────────────────────┘
    ↓
┌───────────────────────────────────┐
│  7. Ensemble Scoring              │
│     • Weight all methods          │
│     • Calculate final confidence  │
│     • Two-tier output:            │
│       - Tier 1: Is AI? (0-100%)   │
│       - Tier 2: Which model?      │
└───────────────────────────────────┘
    ↓
Final Result with Explanations
```

## Weight Distribution

| Method | Weight | Notes |
|--------|--------|-------|
| C2PA Verified | 95% | Cryptographic proof |
| Watermark Detected | 85% | Vendor cooperation required |
| ML Ensemble | 40% | Domain-dependent |
| Pattern Attribution | 30% | Model-specific signals |
| Source Matching | 20% | Best effort search |

**Final confidence = Weighted average of all applicable methods**

## Implementation Roadmap

### Phase 1: Current (MVP) ✅
- Pattern-based text detection
- Simple attribution (GPT, Claude, etc.)
- Basic two-tier confidence

### Phase 2: ML Integration (Next)
- Add transformer-based classifiers
- Ensemble multiple models
- Log-probability analysis

### Phase 3: Metadata & Watermarks
- C2PA library integration
- EXIF analysis
- Watermark detection (research-based)

### Phase 4: Multimodal
- Image detection
- Audio/video pipelines
- Cross-modal analysis

### Phase 5: Source Matching
- Web search integration
- Plagiarism detection
- Academic source matching

## Technology Stack

### Libraries & Tools
- **C2PA**: `c2pa-python` or `c2pa-rs` bindings
- **ML Models**: HuggingFace Transformers, custom BERT/RoBERTa
- **Watermarks**: Custom implementations + vendor SDKs
- **Image Analysis**: PIL, OpenCV, GAN detectors
- **Audio**: librosa, whisper (ASR), spectral analysis
- **Web Search**: SerpAPI, Google Custom Search
- **Plagiarism**: difflib, fuzzy matching algorithms

### Performance Considerations
- **Caching**: Redis cache for repeated content
- **Async Processing**: Celery for long-running tasks
- **Model Serving**: Separate microservice for ML models
- **Rate Limiting**: Prevent abuse of expensive APIs
