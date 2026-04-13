# LinkedIn Outreach MCP Server
**By MEOK AI Labs** | [meok.ai](https://meok.ai)

AI-powered content generation for LinkedIn outreach. Helps sales teams and recruiters craft personalized connection requests, InMails, posts, comments, and multi-touch outreach sequences.

**This is a content assistant, not a scraper or bot.** It does NOT interact with LinkedIn's API, scrape profiles, or automate any actions. It generates text that humans review, edit, and send manually. Fully compliant with LinkedIn's Terms of Service.

## Tools

| Tool | Description |
|------|-------------|
| `generate_connection_request` | Personalized connection request (3 variants, 300 char limit) |
| `generate_inmessage` | Professional InMail/DM with tone control (casual, professional, sales, recruiting) |
| `generate_post` | Engaging LinkedIn post with hashtags (thought-leadership, announcement, question, story) |
| `analyze_profile` | Extract industry, seniority, pain points, and conversation starters from profile text |
| `generate_outreach_sequence` | Full 5-touch outreach sequence with timing (connection -> value -> case study -> soft ask -> direct ask) |
| `generate_comment` | Insightful post comment that adds value (not "Great post!") |

## Installation

```bash
pip install mcp
```

No additional dependencies. Pure Python, no API keys required.

## Usage

### Run the server

```bash
python server.py
```

### Claude Desktop config

```json
{
  "mcpServers": {
    "linkedin-outreach": {
      "command": "python",
      "args": ["/path/to/linkedin-outreach-mcp/server.py"]
    }
  }
}
```

### Example calls

**Generate a connection request:**
```
Tool: generate_connection_request
Input: {"name": "Sarah Chen", "title": "VP of Engineering", "company": "Stripe", "shared_interests": "AI infrastructure, developer tools"}
Output: 3 personalized variants, all under 300 characters
```

**Generate an InMail (sales tone):**
```
Tool: generate_inmessage
Input: {"recipient_name": "James Park", "recipient_title": "CTO", "goal": "book a demo of our observability platform", "tone": "sales"}
Output: Value-first sales message with soft CTA
```

**Generate a LinkedIn post:**
```
Tool: generate_post
Input: {"topic": "AI in sales enablement", "key_points": "personalization at scale, shorter sales cycles, better lead scoring", "style": "thought-leadership"}
Output: Engaging post with hook, numbered points, CTA, and hashtags
```

**Analyze a profile before outreach:**
```
Tool: analyze_profile
Input: {"profile_text": "VP of Engineering at Stripe. Building payments infrastructure for the internet economy. Previously Google, MIT CS. Passionate about developer experience and distributed systems."}
Output: Industry (Technology), Seniority (VP/Executive), pain points, conversation starters, interest areas
```

**Generate a 5-touch outreach sequence:**
```
Tool: generate_outreach_sequence
Input: {"target_name": "Maria Rodriguez", "target_title": "Head of Talent", "target_company": "Figma", "goal": "partner on recruiting automation"}
Output: 5 messages with timing (Day 1 -> Day 25), each with strategic context
```

**Generate a thoughtful comment:**
```
Tool: generate_comment
Input: {"post_content": "Unpopular opinion: cold outreach is dead. The future is warm introductions and community-led growth. Here's why..."}
Output: 2-3 insightful comments that add a new perspective, not generic agreement
```

## How It Works

This server generates content using rule-based templates and industry heuristics. It does NOT call any external AI APIs or LinkedIn APIs. All content is generated locally and instantly.

The `analyze_profile` tool extracts signals from profile text using keyword matching to identify:
- Industry (Technology, Sales, Marketing, Finance, Healthcare, etc.)
- Seniority level (C-Suite, VP, Director, Senior, Manager, Junior)
- Likely pain points based on role and industry
- Tailored conversation starters
- Mutual interest areas for common ground

## Compliance

- Does NOT access LinkedIn's API
- Does NOT scrape any LinkedIn data
- Does NOT automate sending messages
- Does NOT store any user data or profile information
- All content is generated locally -- nothing leaves your machine
- Humans review and send all messages manually

This tool is a writing assistant, similar to Grammarly or a copywriting template. It helps you write better LinkedIn messages faster.

## Pricing

| Tier | Limit | Price |
|------|-------|-------|
| Free | 20 generations/day | $0 |
| Pro | Unlimited generations + priority templates | $19/mo |
| Team | Unlimited + shared sequences + analytics | $49/mo per seat |

## License

MIT
