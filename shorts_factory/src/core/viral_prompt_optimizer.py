"""
🧠 Viral Prompt Optimizer - Advanced LLM Prompt Engineering for Maximum Engagement
Engineered for YouTube Shorts algorithm optimization and viral content patterns
"""

import random
import logging
from typing import Dict, List, Tuple, Optional
from enum import Enum
from dataclasses import dataclass
import json

class ViralPattern(Enum):
    HOOK_AND_REVEAL = "hook_and_reveal"
    BEFORE_AND_AFTER = "before_and_after"
    SECRET_KNOWLEDGE = "secret_knowledge"
    SOCIAL_PROOF = "social_proof"
    CONTROVERSY = "controversy"
    EMOTIONAL_STORY = "emotional_story"
    MYSTERY_SOLVE = "mystery_solve"
    LIFE_HACK = "life_hack"

@dataclass
class ViralFormula:
    """Proven viral content formula with engagement metrics"""
    pattern: ViralPattern
    hook_templates: List[str]
    structure: List[str]
    emotional_triggers: List[str]
    retention_tactics: List[str]
    cta_styles: List[str]
    avg_engagement_rate: float
    optimal_duration: Tuple[int, int]  # min, max seconds

class ViralPromptOptimizer:
    """
    Advanced prompt engineering system optimized for viral YouTube Shorts
    Uses proven engagement patterns, psychological triggers, and platform-specific optimization
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.viral_formulas = self._initialize_viral_formulas()
        self.platform_metrics = self._initialize_platform_optimization()
    
    def _initialize_viral_formulas(self) -> Dict[str, Dict[ViralPattern, ViralFormula]]:
        """Initialize proven viral content formulas by theme and pattern"""
        
        return {
            "family": {
                ViralPattern.EMOTIONAL_STORY: ViralFormula(
                    pattern=ViralPattern.EMOTIONAL_STORY,
                    hook_templates=[
                        "My {family_member} did something that changed our family forever...",
                        "I thought I knew my {family_member}, but when this happened...",
                        "Growing up, I never understood why my {family_member} always...",
                        "This family secret was hidden for {time_period}, until...",
                        "My {age}-year-old {family_member} taught me something I'll never forget..."
                    ],
                    structure=[
                        "Hook (0-3s): Emotional setup with family context",
                        "Background (3-15s): Establish characters and normal situation", 
                        "Inciting incident (15-30s): The event that changes everything",
                        "Emotional climax (30-60s): The heart of the story",
                        "Resolution/lesson (60-75s): What was learned or how it ended",
                        "Universal connection (75-90s): Why viewers will relate",
                        "Engagement CTA (90s): Question that sparks family memories"
                    ],
                    emotional_triggers=["nostalgia", "love", "surprise", "gratitude", "realization"],
                    retention_tactics=[
                        "Use specific ages and timeframes",
                        "Include dialogue or direct quotes",
                        "Build suspense with 'but then...' transitions",
                        "Add unexpected twists or reveals",
                        "Create visual imagery through description"
                    ],
                    cta_styles=[
                        "What's the most important lesson your family taught you?",
                        "Share your favorite family memory in the comments!",
                        "Tag someone who needs to hear this story",
                        "What family tradition means the most to you?"
                    ],
                    avg_engagement_rate=8.7,
                    optimal_duration=(75, 120)
                ),
                
                ViralPattern.MYSTERY_SOLVE: ViralFormula(
                    pattern=ViralPattern.MYSTERY_SOLVE,
                    hook_templates=[
                        "For years, my family wondered why {family_member} always...",
                        "We found something in my {relative}'s house that explained everything...",
                        "My {family_member} had a habit that seemed weird until we discovered...",
                        "After {family_member} passed away, we found out the real reason they..."
                    ],
                    structure=[
                        "Mystery setup (0-5s): Present the puzzling behavior/situation",
                        "Family context (5-15s): Who was involved and how long it went on",
                        "Investigation (15-40s): How the truth was discovered",
                        "Big reveal (40-70s): The surprising explanation",
                        "Emotional impact (70-90s): How it changed the family's perspective"
                    ],
                    emotional_triggers=["curiosity", "surprise", "understanding", "empathy"],
                    retention_tactics=[
                        "Tease the answer early: 'The reason will shock you'",
                        "Use countdown language: 'Here's what we found...'",
                        "Build anticipation with multiple clues"
                    ],
                    cta_styles=[
                        "What family mystery did you solve?",
                        "Have you ever discovered something that changed everything?"
                    ],
                    avg_engagement_rate=9.2,
                    optimal_duration=(60, 100)
                )
            },
            
            "selfhelp": {
                ViralPattern.BEFORE_AND_AFTER: ViralFormula(
                    pattern=ViralPattern.BEFORE_AND_AFTER,
                    hook_templates=[
                        "I was failing at {goal} until I discovered this one thing...",
                        "30 days ago I was {negative_state}, today I'm {positive_state}...",
                        "This {time_period} habit changed my entire {life_area}...",
                        "I tried everything to {achieve_goal}, but this was the game-changer...",
                        "From {starting_point} to {end_point} in just {timeframe}..."
                    ],
                    structure=[
                        "Hook (0-3s): Dramatic before/after setup",
                        "Rock bottom (3-15s): Describe the struggle/failure",
                        "Discovery moment (15-30s): What method/insight changed everything",
                        "Implementation (30-50s): Specific steps taken",
                        "Results (50-70s): Concrete outcomes and measurements",
                        "Lesson (70-85s): Key insight for viewers",
                        "Action CTA (85-90s): Challenge viewers to try it"
                    ],
                    emotional_triggers=["inspiration", "hope", "motivation", "empowerment", "achievement"],
                    retention_tactics=[
                        "Use specific numbers and timeframes",
                        "Show concrete evidence of change",
                        "Include setbacks and obstacles overcome",
                        "Tease the method early: 'The technique is simple but powerful'"
                    ],
                    cta_styles=[
                        "Try this for 7 days and tell me what happens",
                        "What's your biggest challenge right now?",
                        "Share your transformation story!",
                        "Who needs to see this? Tag them!"
                    ],
                    avg_engagement_rate=9.5,
                    optimal_duration=(85, 90)
                ),
                
                ViralPattern.SECRET_KNOWLEDGE: ViralFormula(
                    pattern=ViralPattern.SECRET_KNOWLEDGE,
                    hook_templates=[
                        "Successful people know this secret that schools don't teach...",
                        "I wish someone told me this {age} years ago...",
                        "The {industry} industry doesn't want you to know this...",
                        "This psychological trick will change how you {action}...",
                        "Rich people do this differently, and here's how..."
                    ],
                    structure=[
                        "Hook (0-3s): Promise of exclusive/hidden knowledge",
                        "Authority (3-10s): Establish credibility or source",
                        "Problem (10-20s): What most people do wrong",
                        "Secret reveal (20-50s): The insider knowledge",
                        "Why it works (50-70s): Psychology/logic behind it",
                        "Implementation (70-85s): How to apply it",
                        "Exclusive CTA (85-90s): 'Now you know what they know'"
                    ],
                    emotional_triggers=["curiosity", "exclusivity", "empowerment", "insider_status"],
                    retention_tactics=[
                        "Create information gaps: 'But here's what they don't tell you...'",
                        "Use authority language: 'Experts agree...'",
                        "Build anticipation: 'The secret is at the end'"
                    ],
                    cta_styles=[
                        "How many people do you think know this?",
                        "Will you be part of the few who actually use this?",
                        "Share this secret with someone who needs it"
                    ],
                    avg_engagement_rate=8.9,
                    optimal_duration=(85, 95)
                )
            },
            
            "news": {
                ViralPattern.CONTROVERSY: ViralFormula(
                    pattern=ViralPattern.CONTROVERSY,
                    hook_templates=[
                        "Everyone's talking about {event}, but they're missing the real story...",
                        "The media won't tell you this about {current_event}...",
                        "While you were distracted by {headline}, this happened...",
                        "This {event} changes everything, and here's why...",
                        "You think you know what happened with {story}, but..."
                    ],
                    structure=[
                        "Hook (0-3s): Challenge the mainstream narrative",
                        "Context (3-10s): What everyone thinks they know",
                        "Counter-narrative (10-35s): The alternative perspective",
                        "Evidence (35-55s): Supporting facts/analysis",
                        "Implications (55-70s): Why this matters",
                        "Call to action (70-75s): Engage in the debate"
                    ],
                    emotional_triggers=["curiosity", "skepticism", "concern", "urgency"],
                    retention_tactics=[
                        "Create cognitive dissonance",
                        "Use contrarian language: 'But what if...'",
                        "Promise exclusive insights"
                    ],
                    cta_styles=[
                        "Do you agree with this take?",
                        "What do you think is really going on?",
                        "Share your perspective in the comments"
                    ],
                    avg_engagement_rate=9.8,
                    optimal_duration=(70, 80)
                )
            },
            
            "reddit": {
                ViralPattern.HOOK_AND_REVEAL: ViralFormula(
                    pattern=ViralPattern.HOOK_AND_REVEAL,
                    hook_templates=[
                        "A Redditor confessed something that broke the internet...",
                        "This Reddit thread reveals the dark side of {topic}...",
                        "Someone asked Reddit for advice, and the responses were wild...",
                        "This anonymous confession on Reddit changes everything about {subject}...",
                        "Reddit solved a mystery that stumped experts for years..."
                    ],
                    structure=[
                        "Hook (0-3s): Tease the shocking Reddit content",
                        "Setup (3-10s): Context of the Reddit post/situation",
                        "Build-up (10-30s): Lead up to the reveal",
                        "Big reveal (30-60s): The shocking confession/discovery",
                        "Reaction (60-80s): Community response and implications",
                        "Moral/lesson (80-100s): What we can learn",
                        "Engagement (100s): Ask for viewer opinions"
                    ],
                    emotional_triggers=["shock", "curiosity", "drama", "moral_intrigue"],
                    retention_tactics=[
                        "Use Reddit authenticity: 'Throwaway account posted...'",
                        "Include community reactions: 'The comments went crazy'",
                        "Build tension: 'But the story gets worse...'"
                    ],
                    cta_styles=[
                        "What would you do in this situation?",
                        "Have you seen drama like this online?",
                        "Whose side are you on?"
                    ],
                    avg_engagement_rate=9.3,
                    optimal_duration=(90, 120)
                )
            }
        }
    
    def _initialize_platform_optimization(self) -> Dict[str, Dict]:
        """Initialize YouTube Shorts algorithm optimization parameters"""
        
        return {
            "retention_optimization": {
                "hook_window": 3,  # Critical first 3 seconds
                "retention_points": [0.1, 0.3, 0.5, 0.7, 0.9],  # Points to add retention hooks
                "watch_time_target": 0.85,  # Target 85% average watch time
                "rewatchability_factors": [
                    "Include specific numbers/stats that viewers might want to remember",
                    "Create quotable moments that viewers will share",
                    "Add visual descriptions that make viewers want to see the video",
                    "Use callbacks to earlier parts of the video"
                ]
            },
            
            "engagement_optimization": {
                "comment_triggers": [
                    "Ask controversial but harmless questions",
                    "Include 'unpopular opinion' statements", 
                    "Create polls in the description",
                    "Ask for personal experiences",
                    "Include 'agree or disagree' moments"
                ],
                "share_triggers": [
                    "Include information people will want to teach others",
                    "Create 'mind-blown' moments worth sharing",
                    "Add content that validates people's experiences",
                    "Include helpful tips or life hacks"
                ],
                "like_triggers": [
                    "Include relatable experiences",
                    "Validate common struggles or feelings",
                    "Provide valuable insights or solutions",
                    "Create emotional resonance"
                ]
            },
            
            "algorithm_optimization": {
                "title_optimization": [
                    "Start with power words: This, How, Why, What, Secret",
                    "Include emotional triggers: Shocked, Amazing, Unbelievable",
                    "Use numbers: specific timeframes, quantities, lists",
                    "Create curiosity gaps: ...and what happened next will shock you"
                ],
                "thumbnail_optimization": [
                    "High contrast colors",
                    "Shocked/expressive facial expressions", 
                    "Clear, large text overlays",
                    "Bright, eye-catching backgrounds"
                ],
                "hashtag_strategy": [
                    "Use trending hashtags relevant to theme",
                    "Include platform-specific tags: #shorts, #viral, #fyp",
                    "Add niche community hashtags for targeted reach",
                    "Balance broad (#story) and specific (#familystory) tags"
                ]
            }
        }
    
    def generate_viral_optimized_prompt(
        self,
        theme: str,
        target_duration: int = 90,
        viral_pattern: Optional[ViralPattern] = None,
        custom_context: Optional[str] = None
    ) -> str:
        """
        Generate highly optimized prompt for viral content creation
        
        Args:
            theme: Content theme (family, selfhelp, news, reddit)
            target_duration: Target video duration in seconds
            viral_pattern: Specific viral pattern to use (random if None)
            custom_context: Additional context for customization
            
        Returns:
            Optimized prompt string engineered for maximum viral potential
        """
        
        # Get theme formulas
        theme_formulas = self.viral_formulas.get(theme, {})
        
        if not theme_formulas:
            raise ValueError(f"Unsupported theme: {theme}")
        
        # Select viral pattern (random if not specified)
        if viral_pattern and viral_pattern in theme_formulas:
            formula = theme_formulas[viral_pattern]
        else:
            # Weight selection by engagement rate
            patterns = list(theme_formulas.keys())
            weights = [theme_formulas[p].avg_engagement_rate for p in patterns]
            formula = theme_formulas[random.choices(patterns, weights=weights)[0]]
        
        # Optimize for duration
        optimal_min, optimal_max = formula.optimal_duration
        if target_duration < optimal_min:
            pacing = "ultra-fast pacing with immediate payoff"
            word_count_range = "120-150 words"
        elif target_duration > optimal_max:
            pacing = "extended storytelling with multiple engagement peaks"
            word_count_range = "200-280 words"
        else:
            pacing = "optimal pacing for maximum retention"
            word_count_range = f"{target_duration * 1.6:.0f}-{target_duration * 2.0:.0f} words"
        
        # Select hook template and customize
        hook_template = random.choice(formula.hook_templates)
        emotional_trigger = random.choice(formula.emotional_triggers)
        retention_tactic = random.choice(formula.retention_tactics)
        cta_style = random.choice(formula.cta_styles)
        
        # Build comprehensive prompt
        prompt = f"""Create a VIRAL YouTube Shorts script optimized for maximum engagement and algorithm performance.

🎯 VIRAL OPTIMIZATION PARAMETERS:
Theme: {theme.upper()}
Pattern: {formula.pattern.value.upper().replace('_', ' ')}
Target Duration: {target_duration} seconds
Engagement Target: {formula.avg_engagement_rate}+/10
Primary Emotion: {emotional_trigger.upper()}

🎬 MANDATORY VIRAL STRUCTURE:
{chr(10).join([f"{i+1}. {step}" for i, step in enumerate(formula.structure)])}

🔥 HOOK OPTIMIZATION (0-3 seconds):
Start with: "{hook_template}"
- Must capture attention within first 3 seconds
- Use specific numbers, ages, timeframes for credibility
- Create immediate emotional investment or curiosity gap
- Avoid generic openings - be specific and intriguing

⚡ RETENTION OPTIMIZATION:
- {retention_tactic}
- Add mid-video hooks at 25%, 50%, 75% to prevent drop-off
- Use transition phrases: "But here's what happened next...", "The crazy part is...", "What I discovered will shock you..."
- Include callback references to hook throughout video
- End with satisfying payoff that rewards viewers for watching

💡 CONTENT REQUIREMENTS:
Word Count: {word_count_range}
Pacing: {pacing}
Perspective: First-person narrative (more engaging/authentic)
Language: Conversational, accessible, punchy sentences
Tone: {emotional_trigger.title()} but authentic

🚀 ALGORITHM OPTIMIZATION:
- Include specific details that make story feel real and shareable
- Create moments worth rewatching for details
- Design natural pause points for comments/shares
- Include universal experiences that viewers will relate to
- Build to quotable/memorable moments

💬 ENGAGEMENT ENDING:
Conclude with: "{cta_style}"
- Ask question that sparks personal memories/experiences
- Encourage sharing story with others who would relate
- Create discussion opportunity in comments

🎯 VIRAL SUCCESS METRICS TO OPTIMIZE FOR:
- Hook effectiveness (3-second retention)
- Overall watch time (target 85%+ completion)
- Comment engagement (personal stories/debates)
- Share potential (relatable/shocking content)
- Rewatchability (details worth revisiting)

{f'CUSTOM CONTEXT: {custom_context}' if custom_context else ''}

Generate ONE complete script that maximizes viral potential while maintaining authenticity. Focus on creating content that people will immediately want to share, comment on, and rewatch."""

        self.logger.info(f"Generated viral prompt for {theme} with {formula.pattern.value} pattern")
        return prompt
    
    def analyze_viral_potential(self, script: str, theme: str) -> Dict[str, float]:
        """
        Analyze script for viral potential across multiple dimensions
        
        Args:
            script: Generated script text
            theme: Content theme
            
        Returns:
            Dictionary with viral scores for different aspects
        """
        
        scores = {
            "hook_strength": 0.0,
            "emotional_impact": 0.0, 
            "retention_factors": 0.0,
            "shareability": 0.0,
            "comment_potential": 0.0,
            "authenticity": 0.0,
            "algorithm_optimization": 0.0
        }
        
        script_lower = script.lower()
        sentences = script.split('.')
        
        # Hook strength analysis
        first_sentence = sentences[0].lower() if sentences else ""
        hook_indicators = ["you won't believe", "this changed", "i never expected", "here's what happened", "the crazy part"]
        scores["hook_strength"] = sum(1 for indicator in hook_indicators if indicator in first_sentence) * 2.0
        
        # Emotional impact
        emotional_words = {
            "family": ["love", "family", "mother", "father", "child", "home", "together"],
            "selfhelp": ["success", "change", "transform", "achieve", "grow", "better", "improve"],
            "news": ["breaking", "shocking", "urgent", "important", "crisis", "impact"],
            "reddit": ["anonymous", "confession", "secret", "discovered", "revealed", "truth"]
        }
        
        theme_words = emotional_words.get(theme, [])
        word_score = sum(1 for word in theme_words if word in script_lower)
        scores["emotional_impact"] = min(word_score * 0.5, 10.0)
        
        # Retention factors
        retention_phrases = ["but then", "here's what", "the crazy part", "what happened next", "you won't believe"]
        scores["retention_factors"] = sum(1 for phrase in retention_phrases if phrase in script_lower) * 1.5
        
        # Shareability 
        shareable_elements = ["specific numbers", "shocking revelation", "life lesson", "relatable experience"]
        number_count = len([word for word in script.split() if word.isdigit()])
        scores["shareability"] = number_count * 0.3 + len([s for s in sentences if "!" in s]) * 0.5
        
        # Comment potential (questions and debate topics)
        question_count = script.count('?')
        controversial_phrases = ["unpopular opinion", "most people", "everyone thinks", "the truth is"]
        scores["comment_potential"] = question_count * 1.0 + sum(1 for phrase in controversial_phrases if phrase in script_lower) * 2.0
        
        # Authenticity (personal pronouns and specific details)
        personal_pronouns = ["i ", "my ", "me ", "we ", "our "]
        personal_score = sum(script_lower.count(pronoun) for pronoun in personal_pronouns)
        scores["authenticity"] = min(personal_score * 0.2, 10.0)
        
        # Algorithm optimization
        power_words = ["secret", "truth", "shocking", "amazing", "incredible", "unbelievable"]
        scores["algorithm_optimization"] = sum(1 for word in power_words if word in script_lower) * 1.0
        
        # Normalize all scores to 0-10 scale
        for key in scores:
            scores[key] = min(scores[key], 10.0)
        
        # Calculate overall viral score
        weights = {
            "hook_strength": 0.25,
            "emotional_impact": 0.20,
            "retention_factors": 0.20,
            "shareability": 0.15,
            "comment_potential": 0.10,
            "authenticity": 0.05,
            "algorithm_optimization": 0.05
        }
        
        overall_score = sum(scores[aspect] * weight for aspect, weight in weights.items())
        scores["overall_viral_score"] = overall_score
        
        return scores
    
    def optimize_metadata_for_viral_reach(
        self,
        script: str,
        theme: str,
        viral_scores: Dict[str, float]
    ) -> Dict[str, str]:
        """
        Generate viral-optimized metadata based on script analysis
        
        Args:
            script: The video script
            theme: Content theme
            viral_scores: Viral potential analysis scores
            
        Returns:
            Optimized title, description, and tags
        """
        
        # Extract key elements from script
        first_line = script.split('.')[0] if '.' in script else script.split('\n')[0]
        
        # Generate viral title
        title_starters = ["This", "How", "Why", "What", "Secret", "Truth"]
        emotional_amplifiers = ["Shocking", "Amazing", "Unbelievable", "Life-Changing"]
        
        if viral_scores["overall_viral_score"] > 7:
            amplifier = random.choice(emotional_amplifiers)
            title = f"{amplifier}: {first_line[:45]}..."
        else:
            starter = random.choice(title_starters)
            title = f"{starter} {theme.title()} Story Will Change How You Think"
        
        # Generate description with SEO optimization
        description = f"""🔥 VIRAL {theme.upper()} STORY (Viral Score: {viral_scores['overall_viral_score']:.1f}/10)

{first_line}

This story demonstrates the power of {theme} experiences and how they shape our lives. With high engagement potential and authentic storytelling, this content is optimized for maximum reach and impact.

Key highlights:
✅ Authentic personal experience
✅ Emotionally engaging narrative  
✅ High shareability factor
✅ Comment-driving ending

#shorts #{theme} #viral #story #trending #fyp #relatable #authentic

What's your {theme} story? Share in the comments below! 👇

---
Created with advanced viral optimization for YouTube Shorts algorithm."""

        # Generate trending tags
        theme_tags = {
            "family": "familystory,familytime,parenting,relationships,wholesome",
            "selfhelp": "selfimprovement,motivation,productivity,success,mindset", 
            "news": "breaking,current,analysis,opinion,society",
            "reddit": "storytime,anonymous,confession,internet,community"
        }
        
        base_tags = f"shorts,viral,{theme},story,trending,fyp,relatable"
        specific_tags = theme_tags.get(theme, "lifestyle,content")
        all_tags = f"{base_tags},{specific_tags}"
        
        return {
            "title": title[:60],  # YouTube title limit
            "description": description,
            "tags": all_tags,
            "viral_score": viral_scores["overall_viral_score"]
        }

# Example usage and testing
def test_viral_prompt_optimizer():
    """Test the viral prompt optimizer with different themes"""
    
    optimizer = ViralPromptOptimizer()
    
    themes = ["family", "selfhelp", "news", "reddit"]
    
    for theme in themes:
        print(f"\n{'='*60}")
        print(f"TESTING VIRAL OPTIMIZATION FOR: {theme.upper()}")
        print('='*60)
        
        # Generate optimized prompt
        prompt = optimizer.generate_viral_optimized_prompt(
            theme=theme,
            target_duration=90,
            custom_context="Focus on shocking but believable story"
        )
        
        print("GENERATED PROMPT:")
        print("-" * 40)
        print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
        
        # Test script analysis (mock script for testing)
        mock_script = f"You won't believe what happened to me in my {theme} journey. I was struggling with challenges when something amazing occurred. The transformation was incredible and changed everything. What would you do in this situation?"
        
        scores = optimizer.analyze_viral_potential(mock_script, theme)
        
        print(f"\nVIRAL ANALYSIS SCORES:")
        print("-" * 40)
        for aspect, score in scores.items():
            print(f"{aspect.replace('_', ' ').title()}: {score:.1f}/10")
        
        # Generate optimized metadata
        metadata = optimizer.optimize_metadata_for_viral_reach(mock_script, theme, scores)
        
        print(f"\nOPTIMIZED METADATA:")
        print("-" * 40)
        print(f"Title: {metadata['title']}")
        print(f"Tags: {metadata['tags']}")
        print(f"Viral Score: {metadata['viral_score']:.1f}/10")

if __name__ == "__main__":
    test_viral_prompt_optimizer()

