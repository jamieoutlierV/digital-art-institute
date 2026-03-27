// Sends transcript to Claude for analysis. Key stays server-side.
export default async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  if (req.method === "OPTIONS") return res.status(200).end();
  if (req.method !== "POST") return res.status(405).json({ error: "POST only" });

  const key = process.env.ANTHROPIC_API_KEY;
  if (!key) return res.status(500).json({ error: "ANTHROPIC_API_KEY not configured" });

  const { transcript, filename } = req.body;
  if (!transcript) return res.status(400).json({ error: "Missing transcript" });

  try {
    const response = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify({
        model: "claude-3-5-sonnet-20241022",
        max_tokens: 1200,
        messages: [{
          role: "user",
          content: `You are an intelligence analyst for A(DAI) \u2014 A Digital Arts Institute. Analyze this transcript and return ONLY a JSON object (no markdown, no preamble) with these fields:
- "summary": 2-3 paragraph synthesis, written as a field signal brief. What matters, what patterns, what implications for digital arts/culture/tech.
- "tags": array of 4-8 lowercase tags (topics, themes, people, orgs, technologies)
- "signal_type": one of ["conversation", "lecture", "interview", "meeting", "field_recording", "panel", "other"]
- "key_quotes": array of 2-3 most significant verbatim quotes (with speaker if known)

Transcript from "${filename || "unknown"}":

${transcript.slice(0, 8000)}`
        }]
      })
    });

    const data = await response.json();
    if (!response.ok) return res.status(response.status).json(data);

    const text = data.content?.find(b => b.type === "text")?.text ?? "{}";
    const parsed = JSON.parse(text.replace(/```json|```/g, "").trim());
    return res.status(200).json(parsed);
  } catch (err) {
    return res.status(500).json({ error: err.message });
  }
}
