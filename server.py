#!/usr/bin/env python3
"""
LinkedIn Outreach MCP Server
===============================
AI-powered content generation for LinkedIn outreach. Helps sales teams and
recruiters craft personalized connection requests, InMails, posts, comments,
and multi-touch outreach sequences.

IMPORTANT: This tool does NOT scrape, automate, or interact with LinkedIn
directly. It generates text content that humans then copy into LinkedIn.
This keeps usage fully within LinkedIn's Terms of Service.

By MEOK AI Labs | https://meok.ai

Install: pip install mcp
Run:     python server.py
"""

import json
import re
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional

from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------
FREE_DAILY_LIMIT = 20
_usage: dict[str, list[datetime]] = defaultdict(list)


def _check_rate_limit(caller: str = "anonymous") -> Optional[str]:
    now = datetime.now()
    cutoff = now - timedelta(days=1)
    _usage[caller] = [t for t in _usage[caller] if t > cutoff]
    if len(_usage[caller]) >= FREE_DAILY_LIMIT:
        return (
            f"Free tier limit reached ({FREE_DAILY_LIMIT}/day). "
            "Upgrade to Pro ($19/mo) for unlimited generations: "
            "https://mcpize.com/linkedin-outreach-mcp/pro"
        )
    _usage[caller].append(now)
    return None


# ---------------------------------------------------------------------------
# Content generation helpers
# ---------------------------------------------------------------------------

def _build_connection_request(
    name: str,
    title: str,
    company: str,
    shared_interests: str,
    context: str = "",
) -> dict:
    """Generate a personalized LinkedIn connection request (max 300 chars)."""
    first_name = name.strip().split()[0] if name.strip() else "there"

    # Build opener based on available context
    openers = []
    if shared_interests:
        interests = [i.strip() for i in shared_interests.split(",")]
        if interests:
            openers.append(f"our shared interest in {interests[0]}")
    if company:
        openers.append(f"your work at {company}")
    if title:
        openers.append(f"your role as {title}")

    opener = openers[0] if openers else "your profile"
    context_line = f" {context.strip()}" if context else ""

    # Generate a few variants, all under 300 chars
    variants = []

    v1 = (
        f"Hi {first_name}, I came across your profile and was impressed by {opener}. "
        f"Would love to connect and exchange ideas.{context_line}"
    )
    variants.append(v1[:300])

    v2 = (
        f"Hi {first_name} -- {opener} caught my attention. "
        f"I'd enjoy connecting and learning more about what you're building at {company or 'your company'}.{context_line}"
    )
    variants.append(v2[:300])

    v3 = (
        f"{first_name}, great to find someone focused on {shared_interests.split(',')[0].strip() if shared_interests else 'similar challenges'}. "
        f"Let's connect -- always good to expand the network with thoughtful people in {_infer_industry(title)}.{context_line}"
    )
    variants.append(v3[:300])

    return {
        "status": "ok",
        "variants": variants,
        "char_counts": [len(v) for v in variants],
        "max_allowed": 300,
        "tip": "Pick the variant that feels most natural to your voice. Edit freely before sending.",
    }


def _infer_industry(title: str) -> str:
    """Rough industry guess from job title."""
    title_lower = title.lower()
    if any(w in title_lower for w in ["engineer", "developer", "cto", "devops", "architect"]):
        return "tech"
    if any(w in title_lower for w in ["sales", "account", "bdm", "revenue"]):
        return "sales"
    if any(w in title_lower for w in ["market", "brand", "growth", "cmo"]):
        return "marketing"
    if any(w in title_lower for w in ["recruit", "talent", "hr", "people"]):
        return "talent & HR"
    if any(w in title_lower for w in ["ceo", "founder", "managing director", "president"]):
        return "leadership"
    if any(w in title_lower for w in ["finance", "cfo", "analyst", "investment"]):
        return "finance"
    if any(w in title_lower for w in ["product", "pm", "product manager"]):
        return "product"
    if any(w in title_lower for w in ["design", "ux", "creative"]):
        return "design"
    return "our space"


def _build_inmessage(
    recipient_name: str,
    recipient_title: str,
    conversation_context: str,
    goal: str,
    tone: str = "professional",
) -> dict:
    """Generate a LinkedIn InMail or direct message."""
    first_name = recipient_name.strip().split()[0] if recipient_name.strip() else "there"
    tone = tone.lower().strip()
    if tone not in ("casual", "professional", "sales", "recruiting"):
        tone = "professional"

    tone_intros = {
        "casual": f"Hey {first_name}",
        "professional": f"Hi {first_name}",
        "sales": f"Hi {first_name}",
        "recruiting": f"Hi {first_name}",
    }

    tone_styles = {
        "casual": "friendly and conversational, like messaging a peer",
        "professional": "polished but warm, respectful of their time",
        "sales": "value-first, leading with what's in it for them",
        "recruiting": "opportunity-focused, highlighting growth and impact",
    }

    # Build the message structure based on goal and tone
    if tone == "sales":
        message = (
            f"{tone_intros[tone]},\n\n"
            f"I noticed {conversation_context.strip() or 'your background in ' + _infer_industry(recipient_title)}. "
            f"Wanted to reach out because {goal.strip() or 'I think there could be a great fit'}.\n\n"
            f"We've been helping {_infer_industry(recipient_title)} leaders solve similar challenges, "
            f"and I'd love to share a quick insight that might be relevant to what you're doing "
            f"at {'your company' if not recipient_title else 'your team'}.\n\n"
            f"Would a 15-minute call this week work? Happy to work around your schedule.\n\n"
            f"Best regards"
        )
    elif tone == "recruiting":
        message = (
            f"{tone_intros[tone]},\n\n"
            f"Your profile stood out to me -- {conversation_context.strip() or 'your experience is impressive'}. "
            f"I'm reaching out because {goal.strip() or 'we have an exciting opportunity that could be a great next step'}.\n\n"
            f"This role offers significant impact and growth in a team that values "
            f"the kind of expertise you bring as a {recipient_title or 'professional'}.\n\n"
            f"Would you be open to a brief, no-pressure conversation to learn more?\n\n"
            f"Looking forward to hearing from you"
        )
    elif tone == "casual":
        message = (
            f"{tone_intros[tone]}!\n\n"
            f"{conversation_context.strip() or 'Saw your profile and it resonated'}. "
            f"{goal.strip() or 'Thought it would be cool to connect and chat'}.\n\n"
            f"No agenda here -- just genuinely interested in what you're working on. "
            f"Let me know if you'd be up for a quick chat sometime.\n\n"
            f"Cheers"
        )
    else:  # professional
        message = (
            f"{tone_intros[tone]},\n\n"
            f"I hope this message finds you well. "
            f"{conversation_context.strip() or 'I came across your profile and was impressed by your background'}. "
            f"{goal.strip() or 'I would welcome the opportunity to connect and discuss potential synergies'}.\n\n"
            f"I believe there's meaningful overlap in our work and would appreciate "
            f"the chance to exchange perspectives.\n\n"
            f"Would you be available for a brief conversation?\n\n"
            f"Best regards"
        )

    return {
        "status": "ok",
        "message": message,
        "tone": tone,
        "tone_description": tone_styles[tone],
        "word_count": len(message.split()),
        "tip": "Personalize further with specific details about their recent posts or company news.",
    }


def _build_post(
    topic: str,
    key_points: str,
    style: str = "thought-leadership",
) -> dict:
    """Generate an engaging LinkedIn post with hashtags."""
    style = style.lower().strip()
    valid_styles = ("thought-leadership", "announcement", "question", "story")
    if style not in valid_styles:
        style = "thought-leadership"

    points = [p.strip() for p in key_points.split(",") if p.strip()] if key_points else []

    if style == "thought-leadership":
        hook = f"Most people in {_infer_industry_from_topic(topic)} get this wrong about {topic}."
        body_lines = []
        for i, point in enumerate(points[:5], 1):
            body_lines.append(f"{i}. {point}")
        body = "\n".join(body_lines) if body_lines else f"Here's what I've learned after years of working on {topic}."
        cta = f"\nWhat's your take? I'd love to hear different perspectives."
        post = f"{hook}\n\n{body}\n{cta}"

    elif style == "announcement":
        hook = f"Excited to share some news about {topic}!"
        body_parts = []
        for point in points[:5]:
            body_parts.append(f"- {point}")
        body = "\n".join(body_parts) if body_parts else f"We've been working hard on this and can't wait to show you what's next."
        cta = f"\nStay tuned for more updates. Drop a comment if you want early access."
        post = f"{hook}\n\n{body}\n{cta}"

    elif style == "question":
        hook = f"Genuine question for my network:"
        question = f"\n\n{topic}?\n"
        context_parts = []
        for point in points[:3]:
            context_parts.append(f"- {point}")
        context = "\n".join(context_parts) if context_parts else "I've been thinking about this a lot lately."
        cta = "\nWould love your honest take in the comments."
        post = f"{hook}{question}\n{context}\n{cta}"

    else:  # story
        hook = f"A story about {topic} that changed how I think about everything."
        if points:
            narrative = f"\n\nIt started when {points[0].lower()}."
            if len(points) > 1:
                narrative += f"\n\nThen {points[1].lower()}."
            if len(points) > 2:
                narrative += f"\n\nThe lesson? {points[2]}."
        else:
            narrative = f"\n\nI didn't expect this to happen, but it taught me something I'll carry forever."
        cta = "\n\nHave you had a similar experience? Share below."
        post = f"{hook}{narrative}{cta}"

    # Generate hashtags from topic
    hashtags = _generate_hashtags(topic, points)
    post_with_tags = f"{post}\n\n{hashtags}"

    return {
        "status": "ok",
        "post": post_with_tags,
        "style": style,
        "char_count": len(post_with_tags),
        "hashtag_count": len(hashtags.split()),
        "tip": "LinkedIn's algorithm favors posts between 1200-1600 characters. Add personal anecdotes to boost engagement.",
    }


def _infer_industry_from_topic(topic: str) -> str:
    """Guess industry category from a topic string."""
    topic_lower = topic.lower()
    if any(w in topic_lower for w in ["ai", "ml", "software", "tech", "code", "data", "cloud"]):
        return "tech"
    if any(w in topic_lower for w in ["sales", "revenue", "pipeline", "deal", "quota"]):
        return "sales"
    if any(w in topic_lower for w in ["marketing", "brand", "content", "seo", "growth"]):
        return "marketing"
    if any(w in topic_lower for w in ["hiring", "recruit", "talent", "culture", "remote"]):
        return "HR"
    if any(w in topic_lower for w in ["leader", "manage", "team", "strategy", "ceo"]):
        return "leadership"
    if any(w in topic_lower for w in ["startup", "funding", "vc", "founder"]):
        return "startups"
    return "business"


def _generate_hashtags(topic: str, points: list[str]) -> str:
    """Generate relevant hashtags from topic and key points."""
    words = re.findall(r'[a-zA-Z]+', topic.lower())
    tag_candidates = set()

    # Add topic-based tags
    for word in words:
        if len(word) > 3:
            tag_candidates.add(f"#{word.capitalize()}")

    # Add common professional tags based on content
    topic_lower = topic.lower()
    if "ai" in topic_lower or "artificial" in topic_lower:
        tag_candidates.update(["#AI", "#ArtificialIntelligence", "#MachineLearning"])
    if "sales" in topic_lower:
        tag_candidates.update(["#Sales", "#B2B", "#SalesStrategy"])
    if "marketing" in topic_lower:
        tag_candidates.update(["#Marketing", "#DigitalMarketing"])
    if "leadership" in topic_lower or "leader" in topic_lower:
        tag_candidates.update(["#Leadership", "#Management"])
    if "startup" in topic_lower or "founder" in topic_lower:
        tag_candidates.update(["#Startups", "#Entrepreneurship"])
    if "career" in topic_lower:
        tag_candidates.update(["#CareerAdvice", "#ProfessionalDevelopment"])
    if "hiring" in topic_lower or "recruit" in topic_lower:
        tag_candidates.update(["#Hiring", "#Recruitment", "#TalentAcquisition"])

    # Always include a couple of broad professional tags
    tag_candidates.add("#LinkedIn")
    tag_candidates.add("#ProfessionalDevelopment")

    # Limit to 5 hashtags (LinkedIn best practice)
    tags = sorted(tag_candidates)[:5]
    return " ".join(tags)


def _analyze_profile(profile_text: str) -> dict:
    """Analyze a LinkedIn profile description and extract actionable insights."""
    text_lower = profile_text.lower()

    # Detect industry
    industry = "General"
    industry_keywords = {
        "Technology": ["software", "engineer", "developer", "saas", "cloud", "ai", "data", "devops", "cto", "architect"],
        "Sales": ["sales", "account executive", "business development", "bdm", "revenue", "quota"],
        "Marketing": ["marketing", "brand", "content", "seo", "growth", "cmo", "digital marketing"],
        "Finance": ["finance", "investment", "banking", "cfo", "analyst", "portfolio", "hedge"],
        "Healthcare": ["health", "medical", "pharma", "clinical", "patient", "hospital", "biotech"],
        "Consulting": ["consulting", "advisory", "consultant", "strategy", "mckinsey", "deloitte"],
        "HR & Recruiting": ["recruiting", "talent", "hr", "human resources", "people operations"],
        "Product": ["product manager", "product management", "pm", "product lead", "product owner"],
        "Education": ["education", "university", "professor", "teacher", "academic", "research"],
        "Legal": ["legal", "attorney", "lawyer", "law firm", "counsel", "compliance"],
    }
    for ind, keywords in industry_keywords.items():
        if any(kw in text_lower for kw in keywords):
            industry = ind
            break

    # Detect seniority
    seniority = "Mid-level"
    if any(w in text_lower for w in ["ceo", "founder", "co-founder", "president", "managing director", "partner", "owner"]):
        seniority = "C-Suite / Founder"
    elif any(w in text_lower for w in ["vp", "vice president", "svp", "evp", "chief", "cto", "cmo", "cfo", "coo"]):
        seniority = "VP / Executive"
    elif any(w in text_lower for w in ["director", "head of", "senior director"]):
        seniority = "Director"
    elif any(w in text_lower for w in ["senior", "sr.", "lead", "principal", "staff"]):
        seniority = "Senior"
    elif any(w in text_lower for w in ["manager", "team lead"]):
        seniority = "Manager"
    elif any(w in text_lower for w in ["junior", "jr.", "associate", "entry", "intern", "graduate"]):
        seniority = "Junior / Entry"

    # Infer pain points based on industry and seniority
    pain_points = _infer_pain_points(industry, seniority)

    # Generate conversation starters
    conversation_starters = _generate_conversation_starters(profile_text, industry, seniority)

    # Identify mutual interest areas
    interest_areas = []
    interest_map = {
        "AI & Automation": ["ai", "automation", "machine learning", "chatbot", "llm", "gpt"],
        "Scaling & Growth": ["scale", "growth", "expand", "Series", "funding"],
        "Remote Work": ["remote", "distributed", "hybrid", "work from"],
        "Leadership": ["leadership", "team building", "culture", "mentoring"],
        "Innovation": ["innovation", "disrupt", "transform", "cutting-edge"],
        "Sustainability": ["sustainability", "green", "climate", "esg"],
        "Data & Analytics": ["data", "analytics", "insights", "metrics", "dashboard"],
        "Customer Success": ["customer success", "retention", "churn", "nps"],
        "Open Source": ["open source", "oss", "github", "community"],
        "Diversity & Inclusion": ["diversity", "inclusion", "dei", "equity"],
    }
    for area, keywords in interest_map.items():
        if any(kw in text_lower for kw in keywords):
            interest_areas.append(area)
    if not interest_areas:
        interest_areas = ["Professional Networking", "Industry Trends"]

    return {
        "status": "ok",
        "industry": industry,
        "seniority": seniority,
        "pain_points": pain_points,
        "conversation_starters": conversation_starters,
        "mutual_interest_areas": interest_areas,
        "profile_length": len(profile_text),
        "tip": "Use these insights to personalize your connection request or InMail. Reference specific pain points for higher response rates.",
    }


def _infer_pain_points(industry: str, seniority: str) -> list[str]:
    """Infer likely pain points based on industry and seniority."""
    base_points = {
        "Technology": [
            "Hiring and retaining top engineering talent",
            "Keeping up with rapid technology changes",
            "Technical debt vs. feature velocity trade-offs",
        ],
        "Sales": [
            "Pipeline generation and qualification",
            "Longer sales cycles and more stakeholders in deals",
            "Standing out in a crowded, noisy market",
        ],
        "Marketing": [
            "Proving ROI on marketing spend",
            "Content fatigue and declining organic reach",
            "Aligning marketing and sales on lead quality",
        ],
        "Finance": [
            "Regulatory compliance and reporting burden",
            "Risk management in volatile markets",
            "Digital transformation of legacy processes",
        ],
        "Healthcare": [
            "Balancing patient outcomes with operational efficiency",
            "Regulatory compliance (HIPAA, FDA)",
            "Staff burnout and retention challenges",
        ],
        "Consulting": [
            "Differentiating in a commoditized advisory market",
            "Scaling expertise without burning out partners",
            "Client retention and expanding accounts",
        ],
        "HR & Recruiting": [
            "Talent shortage in key technical roles",
            "Employer brand and candidate experience",
            "Retention and employee engagement",
        ],
        "Product": [
            "Prioritization and stakeholder alignment",
            "Measuring product-market fit objectively",
            "Balancing user needs with business goals",
        ],
        "Education": [
            "Adapting curriculum to industry demands",
            "Student engagement and outcomes measurement",
            "Funding and resource constraints",
        ],
        "Legal": [
            "Efficiency pressure on billable hour model",
            "AI disruption of routine legal work",
            "Client expectation for faster, cheaper delivery",
        ],
    }

    points = base_points.get(industry, [
        "Scaling operations efficiently",
        "Staying competitive in a changing market",
        "Building and retaining a strong team",
    ])

    # Add seniority-specific pain points
    if seniority in ("C-Suite / Founder", "VP / Executive"):
        points.append("Board/investor reporting and strategic alignment")
    elif seniority in ("Director", "Senior"):
        points.append("Cross-functional alignment and execution speed")
    elif seniority in ("Manager",):
        points.append("Developing team members while hitting targets")
    elif seniority in ("Junior / Entry",):
        points.append("Career growth and visibility within the organization")

    return points


def _generate_conversation_starters(profile_text: str, industry: str, seniority: str) -> list[str]:
    """Generate personalized conversation starters."""
    starters = []

    if "founder" in profile_text.lower() or "co-founder" in profile_text.lower():
        starters.append("What inspired you to start your company? I'd love to hear the founding story.")
    if "author" in profile_text.lower() or "speaker" in profile_text.lower():
        starters.append("I saw you're a speaker/author -- what's the most surprising audience reaction you've had?")
    if "mentor" in profile_text.lower() or "coach" in profile_text.lower():
        starters.append("What's the most common advice you find yourself giving to people you mentor?")
    if any(w in profile_text.lower() for w in ["podcast", "blog", "newsletter"]):
        starters.append("I noticed you create content -- what topic gets the most engagement from your audience?")

    # Industry-specific starters
    industry_starters = {
        "Technology": "How is your team approaching the AI shift in your engineering workflow?",
        "Sales": "What's working best for your team in the current selling environment?",
        "Marketing": "How are you thinking about content strategy given the algorithm changes?",
        "Finance": "How is your team navigating the current regulatory landscape?",
        "Healthcare": "What innovations are you most excited about in healthcare right now?",
        "HR & Recruiting": "How are you adapting your hiring strategy in today's market?",
        "Product": "What frameworks do you use for prioritization? Always curious how others approach it.",
    }
    if industry in industry_starters:
        starters.append(industry_starters[industry])

    # Add a generic but genuine one
    starters.append(f"What's the biggest challenge you're tackling this quarter at your {industry.lower()} company?")

    return starters[:5]


def _build_outreach_sequence(
    target_name: str,
    target_title: str,
    target_company: str,
    target_industry: str,
    goal: str,
) -> dict:
    """Generate a 5-touch outreach sequence with timing."""
    first_name = target_name.strip().split()[0] if target_name.strip() else "there"
    industry = target_industry or _infer_industry(target_title)

    sequence = [
        {
            "touch": 1,
            "type": "Connection Request",
            "timing": "Day 1",
            "message": (
                f"Hi {first_name}, I came across your profile -- your work as {target_title} at "
                f"{target_company or 'your company'} is impressive. "
                f"Would love to connect and share ideas in {industry}."
            )[:300],
            "goal": "Get accepted. Keep it short and genuine.",
        },
        {
            "touch": 2,
            "type": "Value Message",
            "timing": "Day 3 (after connection accepted)",
            "message": (
                f"Thanks for connecting, {first_name}! I noticed you're working on some interesting "
                f"things in {industry}. I recently came across an insight on "
                f"{goal.split()[0:3] if goal else ['industry trends']} "
                f"that I thought might be relevant to what you're doing at {target_company or 'your company'}. "
                f"Happy to share if you're interested -- no strings attached."
            ),
            "goal": "Provide value first. No ask yet. Build reciprocity.",
        },
        {
            "touch": 3,
            "type": "Case Study / Social Proof",
            "timing": "Day 7-10",
            "message": (
                f"Hi {first_name}, quick thought -- we recently helped a {industry} company "
                f"similar to {target_company or 'yours'} "
                f"{'achieve ' + goal.strip() if goal else 'tackle a challenge you might relate to'}. "
                f"The results were pretty compelling. Would you be interested in seeing the case study?"
            ),
            "goal": "Introduce credibility through social proof. Ask permission to share more.",
        },
        {
            "touch": 4,
            "type": "Soft Ask",
            "timing": "Day 14-17",
            "message": (
                f"{first_name}, I've been following your recent activity and "
                f"I think there might be a genuine overlap between what we're building and "
                f"the challenges {target_title}s face at companies like {target_company or 'yours'}. "
                f"Would a 10-minute call be worth your time? I promise to keep it focused."
            ),
            "goal": "Low-commitment ask. Emphasize brevity and respect for their time.",
        },
        {
            "touch": 5,
            "type": "Direct Ask / Breakup",
            "timing": "Day 21-25",
            "message": (
                f"Hi {first_name}, I know you're busy so I'll keep this brief. "
                f"I've reached out a few times because I genuinely believe "
                f"{'we can help with ' + goal.strip() if goal else 'there is a fit here'}. "
                f"If the timing isn't right, no worries at all -- I'll follow your content regardless. "
                f"But if there's even a small chance it's worth exploring, I'd love 10 minutes on your calendar."
            ),
            "goal": "Graceful final attempt. The 'breakup' message often gets the highest response rate.",
        },
    ]

    return {
        "status": "ok",
        "target": {
            "name": target_name,
            "title": target_title,
            "company": target_company,
            "industry": industry,
        },
        "goal": goal,
        "sequence": sequence,
        "total_touches": 5,
        "estimated_duration_days": 25,
        "tips": [
            "Engage with their content (like, comment) between touches for visibility.",
            "If they view your profile after a touch, that's a buying signal -- accelerate.",
            "Customize each message with references to their recent posts or company news.",
            "Track opens/responses to learn which touch point converts best for your ICP.",
            "If no response after Touch 5, wait 60 days then restart with fresh context.",
        ],
    }


def _build_comment(post_content: str) -> dict:
    """Generate an insightful comment on a LinkedIn post."""
    # Analyze the post to generate a meaningful comment
    post_lower = post_content.lower()
    post_words = len(post_content.split())

    # Detect the post type
    is_question = "?" in post_content
    is_achievement = any(w in post_lower for w in ["excited", "thrilled", "proud", "announce", "launch", "milestone"])
    is_opinion = any(w in post_lower for w in ["think", "believe", "unpopular opinion", "hot take", "controversial"])
    is_advice = any(w in post_lower for w in ["lesson", "learned", "tip", "mistake", "advice"])
    is_story = any(w in post_lower for w in ["story", "journey", "years ago", "remember when", "experience"])

    comments = []

    if is_question:
        comments.append(
            "Great question. In my experience, the answer depends heavily on context -- "
            "but the one thing I've consistently seen work is starting with the end user's "
            "actual workflow rather than our assumptions about it. "
            "What's driving this question for you specifically?"
        )
        comments.append(
            "This is something I've been thinking about a lot recently. "
            "The short answer is nuanced, but I've found that the teams who get this right "
            "tend to prioritize speed of iteration over perfection of the first attempt. "
            "Curious to see what others think."
        )

    if is_achievement:
        comments.append(
            "Congrats -- and more importantly, the journey to get here is what makes this "
            "milestone meaningful. What was the biggest unexpected challenge along the way? "
            "Those hidden lessons are often the most valuable."
        )
        comments.append(
            "Well deserved. What I find most interesting is not just the result, but "
            "the compounding decisions that led here. Would love to hear what you'd do "
            "differently if you were starting over today."
        )

    if is_opinion:
        comments.append(
            "Appreciate you putting this out there -- takes guts to share a strong take. "
            "I'd add one nuance: the context matters enormously. "
            "What works in a 10-person startup vs. a 10,000-person enterprise are almost "
            "opposite strategies. But the underlying principle you're pointing at is spot on."
        )

    if is_advice:
        comments.append(
            "This resonates deeply. I'd add one thing from my own experience: "
            "the hardest part isn't knowing the right thing to do -- it's having the "
            "discipline to actually do it consistently when things get hectic. "
            "Thanks for the reminder."
        )

    if is_story:
        comments.append(
            "Thanks for sharing this so openly. Stories like this are why LinkedIn "
            "is worth scrolling through. The vulnerability in sharing both the wins "
            "and the struggles is what makes this relatable and actionable. "
            "What would you tell someone who's at the beginning of a similar journey?"
        )

    # Add a versatile fallback
    if not comments or len(comments) < 2:
        # Extract first meaningful sentence to reference
        sentences = [s.strip() for s in post_content.split(".") if len(s.strip()) > 20]
        reference = sentences[0] if sentences else "this"

        comments.append(
            f"This line stood out: '{reference[:80]}...' -- "
            f"I think the key insight here is that most people underestimate how much "
            f"consistency matters relative to strategy. The best framework means nothing "
            f"without disciplined execution. Great post."
        )
        comments.append(
            "Really thoughtful perspective. What I'd add is that the most successful "
            "people I know in this space combine exactly this kind of thinking with "
            "relentless experimentation. Thanks for sharing -- bookmarked this one."
        )

    return {
        "status": "ok",
        "comments": comments[:3],
        "post_type_detected": (
            "question" if is_question else
            "achievement" if is_achievement else
            "opinion" if is_opinion else
            "advice" if is_advice else
            "story" if is_story else
            "general"
        ),
        "tip": "The best comments add a new perspective or ask a follow-up question. Never just agree -- extend the conversation.",
    }


# ---------------------------------------------------------------------------
# MCP Server
# ---------------------------------------------------------------------------
mcp = FastMCP(
    "LinkedIn Outreach MCP",
    instructions=(
        "LinkedIn content generation toolkit for sales teams and recruiters. "
        "Generates personalized connection requests, InMails, posts, comments, "
        "and multi-touch outreach sequences. Does NOT scrape or automate LinkedIn -- "
        "it's a content assistant that helps humans write better messages. "
        "By MEOK AI Labs."
    ),
)


@mcp.tool()
def generate_connection_request(
    name: str,
    title: str = "",
    company: str = "",
    shared_interests: str = "",
    context: str = "",
) -> dict:
    """Generate a personalized LinkedIn connection request (max 300 characters).

    Returns 3 variants to choose from. Edit and personalize before sending.

    Args:
        name: Target person's full name
        title: Their job title (e.g. "VP of Engineering")
        company: Their company name
        shared_interests: Comma-separated shared interests or topics
        context: Optional extra context (e.g. "met at SaaStr conference")
    """
    err = _check_rate_limit()
    if err:
        return {"error": err}
    return _build_connection_request(name, title, company, shared_interests, context)


@mcp.tool()
def generate_inmessage(
    recipient_name: str,
    recipient_title: str = "",
    conversation_context: str = "",
    goal: str = "",
    tone: str = "professional",
) -> dict:
    """Generate a professional LinkedIn InMail or direct message.

    Args:
        recipient_name: Recipient's full name
        recipient_title: Their job title
        conversation_context: Any prior context (e.g. "they liked my post about AI")
        goal: What you want to achieve (e.g. "book a demo call", "discuss job opportunity")
        tone: Message tone -- one of: casual, professional, sales, recruiting
    """
    err = _check_rate_limit()
    if err:
        return {"error": err}
    return _build_inmessage(recipient_name, recipient_title, conversation_context, goal, tone)


@mcp.tool()
def generate_post(
    topic: str,
    key_points: str = "",
    style: str = "thought-leadership",
) -> dict:
    """Generate an engaging LinkedIn post with hashtags.

    Args:
        topic: The main topic or theme of the post
        key_points: Comma-separated key points to include
        style: Post style -- one of: thought-leadership, announcement, question, story
    """
    err = _check_rate_limit()
    if err:
        return {"error": err}
    return _build_post(topic, key_points, style)


@mcp.tool()
def analyze_profile(profile_text: str) -> dict:
    """Analyze a LinkedIn profile description to extract actionable outreach insights.

    Extracts: industry, seniority level, likely pain points, conversation starters,
    and mutual interest areas. Use this before crafting your outreach.

    Args:
        profile_text: The person's LinkedIn headline, summary, or About section text
    """
    err = _check_rate_limit()
    if err:
        return {"error": err}
    if not profile_text or len(profile_text.strip()) < 10:
        return {"error": "Please provide at least a headline or short bio to analyze."}
    return _analyze_profile(profile_text)


@mcp.tool()
def generate_outreach_sequence(
    target_name: str,
    target_title: str = "",
    target_company: str = "",
    target_industry: str = "",
    goal: str = "",
) -> dict:
    """Generate a 5-touch LinkedIn outreach sequence with timing recommendations.

    Sequence: connection request -> value message -> case study -> soft ask -> direct ask.
    Each touch includes the message text, timing, and strategic goal.

    Args:
        target_name: Target person's full name
        target_title: Their job title
        target_company: Their company
        target_industry: Their industry (auto-detected from title if blank)
        goal: Your outreach goal (e.g. "book a demo", "recruit for senior role")
    """
    err = _check_rate_limit()
    if err:
        return {"error": err}
    return _build_outreach_sequence(target_name, target_title, target_company, target_industry, goal)


@mcp.tool()
def generate_comment(post_content: str) -> dict:
    """Generate an insightful comment for a LinkedIn post.

    Analyzes the post type (question, achievement, opinion, advice, story) and
    generates comments that add genuine value -- not generic "Great post!" fluff.

    Args:
        post_content: The text content of the LinkedIn post you want to comment on
    """
    err = _check_rate_limit()
    if err:
        return {"error": err}
    if not post_content or len(post_content.strip()) < 20:
        return {"error": "Please provide the post content (at least a sentence) to generate a meaningful comment."}
    return _build_comment(post_content)


if __name__ == "__main__":
    mcp.run()
