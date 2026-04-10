from typing import List, Dict, Any, Optional
from .providers import BaseProvider
import time

DEFAULT_SYSTEM_PROMPT = """You are an expert prompt engineer. Your task is to refine user prompts to be more clear, 
focused, and effective for Large Language Models. 

Guidelines for improvement:
- Make the prompt more specific and detailed
- Add necessary context and constraints
- Improve clarity and remove ambiguity
- Add structure when helpful (bullet points, numbered lists)
- Preserve the original intent and key elements

Respond ONLY with the improved prompt, no explanations."""


CRITIQUE_SYSTEM_PROMPT = """You are an expert prompt reviewer. Your task is to analyze a refined prompt and provide 
constructive criticism to further improve it.

For the given prompt, identify:
1. Remaining ambiguities or vague terms
2. Missing context that could help
3. Areas that could be more specific
4. Structural improvements possible

Provide specific, actionable feedback. If the prompt is already excellent, respond with "EXCELLENT" only."""


def self_refine_loop(
    prompt: str,
    provider: BaseProvider,
    iterations: int = 3,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    critique_provider: Optional[BaseProvider] = None
) -> Dict[str, Any]:
    """
    Self-Refine loop: generate → critique → refine → repeat
    """
    history = []
    current = prompt
    
    for i in range(iterations):
        iteration_start = time.time()
        
        # Step 1: Generate improved version
        generation_prompt = f"""Original prompt: {prompt}

Current version: {current}

Please improve this prompt to be more clear, specific, and effective. 
Focus on making it produce better outputs when used with an LLM.

Improved prompt:"""
        
        generated = provider.generate(
            generation_prompt,
            system_prompt=system_prompt,
            temperature=0.7
        )
        
        # Step 2: Generate critique (using same or different provider)
        critique_p = critique_provider if critique_provider else provider
        
        if i < iterations - 1:  # Skip critique on last iteration
            critique_prompt = f"""Original: {prompt}
Previous: {current}
Generated: {generated}

Provide brief, actionable feedback to improve this prompt further.
If excellent, say "EXCELLENT":"""
            
            critique = critique_p.generate(
                critique_prompt,
                system_prompt=CRITIQUE_SYSTEM_PROMPT,
                temperature=0.3
            )
            
            # Step 3: Refine with critique
            if critique.strip() != "EXCELLENT":
                refine_prompt = f"""Original: {prompt}
Current version: {generated}
Critique: {critique}

Apply this critique to produce an improved version:"""
                
                refined = provider.generate(
                    refine_prompt,
                    system_prompt=system_prompt,
                    temperature=0.7
                )
            else:
                refined = generated
                critique = "EXCELLENT"
        else:
            refine_prompt = f"""Original: {prompt}
Previous version: {generated}
Critique: (Final iteration - no critique needed)

This is the final iteration. Polish and return the best version:"""
            
            refined = provider.generate(
                refine_prompt,
                system_prompt=system_prompt,
                temperature=0.7
            )
            critique = "Final iteration - polished"
        
        iteration_time = time.time() - iteration_start
        
        history.append({
            "iteration": i + 1,
            "generated": generated,
            "critique": critique,
            "refined": refined,
            "time_ms": int(iteration_time * 1000)
        })
        
        current = refined
    
    return {
        "original": prompt,
        "final": current,
        "history": history,
        "technique": "self-refine",
        "iterations": iterations
    }


def tree_of_thoughts(
    prompt: str,
    provider: BaseProvider,
    n_versions: int = 3,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT
) -> Dict[str, Any]:
    """
    Tree of Thoughts: generate multiple versions, evaluate, return best
    """
    versions = []
    
    # Generate N different versions
    for i in range(n_versions):
        version_prompt = f"""Original prompt: {prompt}

Generate version {i+1} of this prompt, focusing on a different aspect or approach.
Try to make it more effective in a unique way.

Version {i+1}:"""
        
        version = provider.generate(
            version_prompt,
            system_prompt=system_prompt,
            temperature=0.9 + (i * 0.02)  # Slightly higher temp for diversity
        )
        
        versions.append(version)
    
    # Evaluate each version
    scored_versions = []
    for i, version in enumerate(versions):
        eval_prompt = f"""Original: {prompt}
Candidate: {version}

Rate this prompt from 0-100 on how effective it is for producing good LLM outputs.
Consider: clarity, specificity, structure, completeness.

Respond ONLY with a number:"""
        
        score_str = provider.generate(
            eval_prompt,
            system_prompt="You are a strict evaluator. Respond only with a number.",
            temperature=0.3
        )
        
        try:
            score = int(''.join(filter(str.isdigit, score_str.split()[0])))
        except:
            score = 50  # Default if parsing fails
        
        scored_versions.append({
            "version": i + 1,
            "text": version,
            "score": score
        })
    
    # Sort by score and get best
    scored_versions.sort(key=lambda x: x["score"], reverse=True)
    
    return {
        "original": prompt,
        "final": scored_versions[0]["text"],
        "versions": scored_versions,
        "best_score": scored_versions[0]["score"],
        "technique": "toT",
        "n_versions": n_versions
    }


def basic_improve(
    prompt: str,
    provider: BaseProvider,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT
) -> Dict[str, Any]:
    """
    Basic single-pass improvement (current behavior)
    """
    improvement_prompt = f"""Original prompt: {prompt}

Improve this prompt to be more clear, specific, and effective for LLM use.

Improved prompt:"""
    
    improved = provider.generate(
        improvement_prompt,
        system_prompt=system_prompt,
        temperature=0.7
    )
    
    return {
        "original": prompt,
        "final": improved,
        "technique": "none",
        "iterations": 1
    }