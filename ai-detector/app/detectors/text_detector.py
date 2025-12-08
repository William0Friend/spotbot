"""
AI Text Detection Engine

Deployment: Hostinger VPS → DigitalOcean (when scaling)

Why this approach:
- Pattern matching is fast and requires no ML training (perfect for MVP)
- Each AI model has distinct "tells" - vocabulary, formatting, structure
- Multi-factor scoring prevents false positives from single pattern matches
- Two-tier confidence: (1) is it AI? (2) which AI made it?

How confidence works:
- Overall confidence: weighted combo of 5 detection methods
- Model confidence: proportion of overall that can be attributed to specific model
- Example: 45% overall, Claude patterns strongest → "45% AI, 30% likely Claude"
- Model confidence CANNOT exceed overall confidence (logic constraint)

Detection strategy:
1. Model-specific patterns (40% weight) - unique vocabulary per AI
2. General AI characteristics (25%) - common tells across all models  
3. Unnatural phrasing (20%) - awkward expressions humans rarely use
4. Linguistic analysis (10%) - sentence length, consistency, structure
5. Formatting (5%) - markdown, lists, paragraph breaks
"""

import re
from typing import Dict, Any, Optional, List, Tuple

class TextDetector:
    """
    Pattern-based AI text detector supporting GPT, Claude, Gemini, Llama, Mistral.
    
    Returns two-tier confidence:
    - Tier 1: Overall AI probability (0-100%)
    - Tier 2: Which model likely created it (0-100%, but ≤ Tier 1)
    
    Threshold: 40% overall confidence = "is_ai_generated: true"
    """
    
    def __init__(self):
        """
        Initialize detector with pattern libraries for each major AI model.
        
        Why patterns work:
        - Each AI has training biases that leak into output
        - GPT loves em dashes, hedging, and "it's worth noting"
        - Claude is polite, ethical, uses casual-professional mix
        - Gemini references its training data explicitly
        - Llama has open-source project tells
        - Mistral has efficiency-focused language
        
        Pattern design philosophy:
        - Regex for flexibility (handles variations, typos)
        - Multiple patterns per tell (increases recall)
        - Weight by rarity (common phrases score lower)
        """
        
        # Model-specific pattern libraries
        # Each pattern maps to tells that distinguish this AI from others
        self.ai_patterns = {
            "gpt": [
                # OpenAI's training makes GPT excessively polite and self-referential
                # These patterns rarely appear in human writing at this frequency
                r"as an ai language model",  # Dead giveaway - humans never say this
                r"i don't have personal (feelings|opinions|experiences|access)",
                r"i (can't|cannot) (provide|offer|give|access|browse)",
                r"i'm (sorry|afraid) i (can't|cannot)",
                r"i apologize, but",  # Over-apologetic
                
                # GPT's distinctive vocabulary - these appear in clusters
                r"certainly[!,.]",  # Formal agreement
                r"absolutely[!,.]",  # Emphatic agreement
                r"it's worth noting that",  # Meta-commentary tell
                r"it'?s important to (note|remember|understand|consider|recognize)",
                r"keep in mind that",  # Instructional framing
                r"bear in mind",
                r"take into (account|consideration)",
                
                # Typography tells - GPT uses em dash (—) not hyphen (-)
                # This is because of how its training data was formatted
                r"—",  # Em dash character
                r"\s—\s",  # Em dash with spaces (very GPT-specific)
                
                # Structural tells - GPT loves organized explanations
                r"here'?s (what|how|why|a|an)",  # Intro framing
                r"let'?s (explore|dive into|break down|examine)",  # Invitational tone
                r"in this (article|post|guide)",  # Self-referential
                r"first and foremost",  # Formal ordering
                r"at the end of the day",  # Summary cliché
                
                # Hedging language - GPT avoids definitive statements
                # This is from RLHF training to be "safe"
                r"(it|this) (would|could|might|may) (be|seem|appear)",
                r"arguably",  # Academic hedge
                r"to some extent",  # Qualification
                r"one could argue",  # Distancing phrase
            ],
            
            "claude": [
                # Anthropic trained Claude to be helpful AND transparent about limitations
                # This creates a distinctive polite-but-direct tone
                r"i aim to (be|provide)",  # Mission-oriented language
                r"i should (clarify|note|mention|emphasize|point out)",  # Meta-transparency
                r"i'd be (happy|glad|pleased) to",  # Enthusiastic helpfulness
                r"let me (help|assist|explain|clarify)",  # Service framing
                r"i appreciate your",  # Gratitude tells
                
                # Claude's collaborative style - treats user as peer
                r"that'?s a (great|good|interesting|thoughtful) (question|point)",
                r"thinking (about|through|carefully about)",  # Reasoning transparency
                r"from (my|an) (perspective|understanding|analysis)",  # Viewpoint framing
                r"i notice that",  # Observation sharing
                r"it seems (like|that)",  # Tentative assertion
                r"i want to be (clear|careful|thoughtful|honest)",  # Explicit values
                
                # Anthropic's Constitutional AI makes ethics prominent
                # Claude mentions these more than other models
                r"(ethical|moral) (implications|considerations|concerns)",
                r"it'?s worth considering (the )?(ethical|moral|privacy)",
                r"responsible (use|approach|handling)",
                
                # Problem-solving structure - Claude breaks down complexity
                r"breaking (this|that|it) down",  # Deconstruction tell
                r"let'?s think (about|through)",  # Thinking out loud
                r"step back and",  # Meta-cognition
                
                # Casual professional tone - unique Claude signature
                # These patterns match modern startup/tech communication style
                r"\bnice (idea|question|point)\b",  # Informal validation
                r"high-impact",  # Business value framing
                r"hard in (all )?the right ways",  # Nuanced assessment
                r"i'll lay out",  # Action-oriented (note contraction)
                r"(concrete|practical) (plan|approach|system|architecture)",  # Pragmatic focus
                r"citation-backed",  # Evidence-based reasoning
                r"(what|how|why) .{5,30} (actually )?works",  # Reality-grounded
                r"and its limits",  # Limitation awareness (key Claude trait)
                r"reality check:",  # Direct interjection style
                r"why this is (hard|challenging|difficult)",  # Problem acknowledgment
                r"status of the field",  # Academic survey framing
                r"(detection|attribution) (actually )?works( today)?",  # Current state focus
                r"(in|with) all the right ways",  # Qualifier nuance
                r"roadmap",  # Planning/timeline language
                r"(mvp|minimum viable product).{0,20}(production|scale)",  # Product thinking
                r"tooling choices",  # Technical decision framing
                r"arms race",  # Competition metaphor
                r"provenance",  # Authenticity/origin term
                r"probabilistic",  # Statistical precision language
            ],
            
            "gemini": [
                # Gemini/Bard patterns
                r"based on (my training|the) (data|information)",
                r"according to (my|the) (knowledge|information|training)",
                r"as (of|per) (my|the) (knowledge cutoff|last update)",
                r"i'm (bard|gemini)",
                r"as a large language model",
                
                # Google-style patterns
                r"i can (help you|assist you|provide information)",
                r"i have access to and process information from",
                r"my knowledge is based on",
                r"i'm still learning",
                r"i'm constantly learning",
                
                # Bullet points and structured lists
                r"^\s*[•\*\-]\s+",  # Bullet points
                r"^\s*\d+[\.)]\s+",  # Numbered lists
            ],
            
            "llama": [
                # Meta Llama patterns
                r"as a helpful (ai )?assistant",
                r"i'm (here to|designed to|programmed to) (help|assist)",
                r"based on (my|the) training",
                r"i don't have the ability to",
                
                # Llama's formal tone
                r"in regards to",
                r"with (respect|regard) to",
                r"it is (my|the) understanding that",
                r"i would (recommend|suggest|advise)",
            ],
            
            "mistral": [
                # Mistral AI patterns
                r"as (an|a) mistral",
                r"i'm (a )?mistral (ai|model)",
                r"based on (mistral|my) (training|capabilities)",
                
                # European/formal English patterns
                r"whilst",
                r"amongst",
                r"in order to",
            ],
        }
        
        # Universal AI writing characteristics (used by most models)
        self.ai_characteristics = [
            # Transition words (overused by AI)
            r"\b(however|moreover|furthermore|additionally|consequently|therefore|thus|hence|nevertheless|nonetheless)\b",
            
            # Formal transitions
            r"\b(in (conclusion|summary|addition|contrast|comparison|essence|fact))\b",
            r"\b(on the other hand|that being said|in other words)\b",
            
            # Emphatic phrases
            r"it is (important|crucial|essential|vital|critical|imperative|necessary) to",
            r"(plays?|played) a (crucial|vital|key|significant|important) role",
            r"(plays?|played) an important part",
            
            # Generic opening phrases
            r"^in (today'?s|our|this) (world|society|era|age)",
            r"^(it is|it's) (important|crucial|essential|worth|interesting) to (note|understand|consider)",
            
            # Structured content indicators
            r"(step-by-step|step by step)",
            r"(first(ly)?|second(ly)?|third(ly)?|finally)[,:]",
            r"to (begin|start) with",
            r"(in|to) (sum|summarize|conclude)",
            
            # Hedging and uncertainty (AI is often cautious)
            r"(might|may|could|would|should) (be|seem|appear|suggest|indicate)",
            r"(it is|it's) (possible|likely|probable|conceivable) that",
            r"(tend|tends) to",
            r"(can|could) (potentially|possibly)",
            
            # Overly balanced statements
            r"(both|each) (has|have) (its|their) (own)? (advantages?|benefits?|drawbacks?|pros?|cons?)",
            r"on one hand.*on the other hand",
            r"(advantages? and disadvantages?|pros and cons)",
            
            # Academic/formal language
            r"it is (noteworthy|notable|significant|clear|evident) that",
            r"(research|studies|evidence) (shows?|suggests?|indicates?)",
            r"according to (research|studies|experts)",
            
            # AI's love for comprehensiveness
            r"(wide|broad|vast) (range|variety|array|spectrum) of",
            r"(numerous|various|multiple|several|many) (ways|methods|approaches|factors)",
            r"it is worth (noting|mentioning|considering)",
            
            # Repetitive structures
            r"not only.*but also",
            r"while.*it is (also|important|crucial)",
        ]
        
        # Special symbols and formatting AI models commonly use
        self.formatting_patterns = [
            r"—",  # Em dash (GPT favorite)
            r"–",  # En dash
            r"^\s*[\*\-•]\s+",  # Bullet points
            r"^\s*\d+[\.)]\s+",  # Numbered lists
            r"\*\*[^*]+\*\*",  # Bold markdown
            r"\*[^*]+\*",  # Italic markdown
            r"`[^`]+`",  # Code backticks
        ]
        
        # Unnatural word choices and stilted language
        self.unnatural_phrases = [
            r"\b(utilize|utilization)\b",  # Instead of "use"
            r"\b(commence)\b",  # Instead of "start"
            r"\b(prior to)\b",  # Instead of "before"
            r"\b(in order to)\b",  # Instead of "to"
            r"\b(with regards? to|in regards? to)\b",  # Awkward
            r"\b(at this point in time)\b",  # Instead of "now"
            r"\b(due to the fact that)\b",  # Instead of "because"
            r"\b(in the event that)\b",  # Instead of "if"
            r"\b(for the purpose of)\b",  # Instead of "to"
            r"\b(in the process of)\b",  # Wordy
            r"\b(take into consideration)\b",  # Instead of "consider"
            r"\b(make a decision)\b",  # Instead of "decide"
            r"\b(provide assistance)\b",  # Instead of "help"
            r"\b(in close proximity to)\b",  # Instead of "near"
        ]
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Main detection pipeline - analyzes text through 5 parallel detection methods.
        
        Args:
            text: Content to analyze
            
        Returns:
            Detection result with two-tier confidence (overall AI % + specific model %)
            
        Pipeline:
        1. Model-specific patterns (40% weight) - unique tells per AI
        2. General AI characteristics (25%) - common across all models
        3. Unnatural phrases (20%) - stilted language humans avoid
        4. Linguistic heuristics (10%) - statistical text analysis
        5. Formatting patterns (5%) - markdown, structure, symbols
        
        Why multi-factor:
        - Single pattern match could be coincidence
        - Need convergence of multiple signals for confidence
        - Different patterns have different false positive rates
        - Weighted combination balances precision vs recall
        """
        
        # Empty text guard
        if not text or len(text.strip()) == 0:
            return {
                "is_ai_generated": None,
                "confidence_score": 0.0,
                "detected_model": None,
                "model_confidence": None,
                "analysis_details": {"error": "No text provided"}
            }
        
        text_lower = text.lower()  # Normalized for case-insensitive matching
        
        # Track all pattern matches for transparency/debugging
        all_matched_patterns = []
        
        # === PHASE 1: Model-Specific Pattern Detection (40% weight) ===
        # Why this matters: Each AI has training biases that leak into output
        # - GPT overuses em dashes (—) because of training data formatting
        # - Claude mentions ethics because of Constitutional AI training
        # - Gemini references "my training data" explicitly
        model_scores = {}
        for model, patterns in self.ai_patterns.items():
            score = 0
            matched_patterns = []
            for pattern in patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                if matches:
                    match_count = len(matches)
                    # Weight by uniqueness and frequency
                    pattern_score = min(match_count * 15, 50)  # Cap per pattern
                    score += pattern_score
                    matched_patterns.append({
                        "pattern": pattern,
                        "matches": match_count,
                        "score": pattern_score
                    })
                    all_matched_patterns.append(f"{model}: {pattern} ({match_count}x)")
            
            model_scores[model] = {
                "score": min(score, 100),
                "patterns": matched_patterns
            }
        
        # 2. Check for general AI characteristics (medium weight)
        ai_characteristic_score = 0
        matched_characteristics = []
        for pattern in self.ai_characteristics:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            if matches:
                match_count = len(matches)
                # Multiple matches increase suspicion
                score_increment = min(match_count * 3, 15)
                ai_characteristic_score += score_increment
                matched_characteristics.append({
                    "pattern": pattern,
                    "matches": match_count
                })
                all_matched_patterns.append(f"AI characteristic: {pattern} ({match_count}x)")
        
        # 3. Check formatting patterns (light weight)
        formatting_score = 0
        matched_formatting = []
        for pattern in self.formatting_patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            if matches:
                match_count = len(matches)
                formatting_score += min(match_count * 2, 10)
                matched_formatting.append({
                    "pattern": pattern,
                    "matches": match_count
                })
        
        # 4. Check unnatural phrases (medium-high weight)
        unnatural_score = 0
        matched_unnatural = []
        for pattern in self.unnatural_phrases:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            if matches:
                match_count = len(matches)
                unnatural_score += min(match_count * 5, 20)
                matched_unnatural.append({
                    "pattern": pattern,
                    "matches": match_count
                })
                all_matched_patterns.append(f"Unnatural: {pattern} ({match_count}x)")
        
        # 5. Linguistic heuristics
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        words = text.split()
        word_count = len(words)
        sentence_count = max(len(sentences), 1)
        avg_sentence_length = word_count / sentence_count
        
        # Analyze sentence length distribution
        sentence_lengths = [len(s.split()) for s in sentences]
        length_variance = 0
        if len(sentence_lengths) > 1:
            mean_len = sum(sentence_lengths) / len(sentence_lengths)
            length_variance = sum((l - mean_len) ** 2 for l in sentence_lengths) / len(sentence_lengths)
        
        linguistic_score = 0
        linguistic_details = []
        
        # AI tends to have very consistent sentence lengths (low variance)
        if length_variance < 20 and sentence_count > 3:
            linguistic_score += 10
            linguistic_details.append("Low sentence length variance (AI-like consistency)")
        
        # AI often uses longer, more complex sentences
        if avg_sentence_length > 20:
            linguistic_score += 15
            linguistic_details.append(f"Long average sentence length: {avg_sentence_length:.1f} words")
        elif avg_sentence_length > 15:
            linguistic_score += 8
            linguistic_details.append(f"Above-average sentence length: {avg_sentence_length:.1f} words")
        
        # Count paragraph breaks (AI often uses structured paragraphs)
        paragraph_breaks = text.count('\n\n') + text.count('\n\n\n')
        if paragraph_breaks > 2:
            linguistic_score += 5
            linguistic_details.append(f"Structured paragraphs: {paragraph_breaks} breaks")
        
        # Check for excessive use of commas (AI loves complex sentences)
        comma_ratio = text.count(',') / max(sentence_count, 1)
        if comma_ratio > 3:
            linguistic_score += 8
            linguistic_details.append(f"High comma usage: {comma_ratio:.1f} per sentence")
        
        # 6. Detect best matching model
        # IMPORTANT: Model confidence must be ≤ overall confidence
        # Logic: can't be 100% sure which model if only 45% sure it's AI at all
        detected_model = None
        model_raw_score = 0.0  # Raw pattern match score (0-100)
        model_details = {}
        
        if model_scores:
            # Sort models by pattern match score
            sorted_models = sorted(model_scores.items(), key=lambda x: x[1]["score"], reverse=True)
            best_model = sorted_models[0]
            
            if best_model[1]["score"] > 0:
                detected_model = best_model[0]
                model_raw_score = min(best_model[1]["score"], 100)
                
                # Rank top models for transparency
                for i, (model, data) in enumerate(sorted_models[:3]):
                    if data["score"] > 0:
                        model_details[model] = {
                            "score": data["score"],
                            "pattern_count": len(data["patterns"]),
                            "rank": i + 1
                        }
        
        # 7. Calculate overall AI confidence score
        # Weighted combination of all 5 detection factors
        # Each factor contributes proportionally based on reliability
        total_confidence = (
            (model_raw_score * 0.40) +           # Model-specific patterns: 40% (most reliable)
            (min(ai_characteristic_score, 100) * 0.25) +  # General AI tells: 25%
            (min(unnatural_score, 100) * 0.20) +  # Unnatural phrasing: 20%
            (min(linguistic_score, 100) * 0.10) + # Statistical analysis: 10%
            (min(formatting_score, 100) * 0.05)   # Formatting quirks: 5%
        )
        
        # Cap at 100%
        total_confidence = min(total_confidence, 100)
        
        # Calculate model-specific confidence (Tier 2)
        # LOGIC: Can't be MORE confident which model than whether it's AI at all
        # Example: If 45% confident it's AI, can be AT MOST 45% confident it's Claude
        # 
        # Why this makes sense:
        # - Overall confidence = "Is this AI-generated?" (45%)
        # - Model confidence = "Which AI made this?" (≤ 45%)
        # - Can't know source more confidently than knowing it's AI in first place
        #
        # Formula: Scale the model's dominance by overall confidence
        # If Claude has 100% of patterns and overall is 45%, model_confidence = 45%
        # If Claude has 50% of patterns and overall is 45%, model_confidence = 22.5%
        if detected_model and total_confidence > 0:
            model_contribution = model_raw_score * 0.40  # How much this model contributed
            # Scale model dominance by overall confidence
            model_dominance = model_contribution / total_confidence  # 0.0 to 1.0
            model_confidence = total_confidence * model_dominance
        else:
            model_confidence = 0.0
        
        # Determine if AI-generated (threshold: 40%)
        # Why 40%: balances false positives vs false negatives
        # Below 40% = not enough signals, could be human
        # Above 40% = clear AI patterns detected
        is_ai = total_confidence >= 40
        
        # Human-readable confidence labels
        confidence_label = "Very High" if total_confidence >= 80 else \
                          "High" if total_confidence >= 60 else \
                          "Moderate" if total_confidence >= 40 else \
                          "Low" if total_confidence >= 20 else "Very Low"
        
        return {
            "is_ai_generated": is_ai,
            "confidence_score": round(total_confidence, 2),
            "confidence_label": confidence_label,
            "detected_model": detected_model,
            "model_confidence": round(model_confidence, 2) if model_confidence > 0 else None,
            "analysis_details": {
                "text_length": len(text),
                "word_count": word_count,
                "sentence_count": sentence_count,
                "avg_sentence_length": round(avg_sentence_length, 2),
                "sentence_length_variance": round(length_variance, 2),
                "model_scores": {k: round(v["score"], 2) for k, v in model_scores.items() if v["score"] > 0},
                "model_details": model_details,
                "scoring_breakdown": {
                    "model_specific": round(model_raw_score * 0.40, 2),
                    "ai_characteristics": round(min(ai_characteristic_score, 100) * 0.25, 2),
                    "unnatural_phrases": round(min(unnatural_score, 100) * 0.20, 2),
                    "linguistic_patterns": round(min(linguistic_score, 100) * 0.10, 2),
                    "formatting": round(min(formatting_score, 100) * 0.05, 2)
                },
                "matched_pattern_count": len(all_matched_patterns),
                "matched_patterns_sample": all_matched_patterns[:10],  # Top 10 matches
                "linguistic_details": linguistic_details,
                "detection_factors": {
                    "ai_characteristics": len(matched_characteristics),
                    "unnatural_phrases": len(matched_unnatural),
                    "formatting_indicators": len(matched_formatting)
                },
                "method": "multi_factor_pattern_analysis_v2"
            }
        }
