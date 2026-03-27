// A(DAI) query engine — conversational sensemaking against the graph.
export default async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  if (req.method === "OPTIONS") return res.status(200).end();
  if (req.method !== "POST") return res.status(405).json({ error: "POST only" });

  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) return res.status(500).json({ error: "ANTHROPIC_API_KEY not configured" });

  const { message, graphSummary, history } = req.body;
  if (!message) return res.status(400).json({ error: "message is required" });

  const system = `You are the A(DAI) sensemaking engine — a conversational intelligence for the digital arts field, from 1960s pioneers to today.

You have access to the collective intelligence graph below. Speak like a peer in the studio who's seen a lot: direct, warm, unhurried. Not academic, not dramatic. Say what you see.

Your role:
- Surface patterns and connections across the graph
- Name blind spots — what's missing, underrepresented, or assumed
- Provoke gently — ask back, reframe, offer an angle
- Keep it SHORT: 2-4 sentences per turn. One thought at a time.

Never: bullet points, long paragraphs, flattery, hedging, numbered lists.
Always: specific, grounded in what the graph actually contains, honest about what's not there yet.

If the graph is small or early-stage, say so honestly. Don't invent data.

CURRENT GRAPH STATE:
${graphSummary || "No graph data available yet."}`;

  // Build conversation: last 6 exchanges max
  const messages = [];
  if (Array.isArray(history)) {
    history.slice(-12).forEach(function (m) {
      messages.push({ role: m.role, content: m.content });
    });
  }
  messages.push({ role: "user", content: message });

  try {
    const response = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "x-api-key": apiKey,
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify({
        model: "claude-3-5-sonnet-20241022",
        max_tokens: 300,
        system: system,
        messages: messages,
      }),
    });

    if (!response.ok) {
      const err = await response.json();
      return res.status(response.status).json({ error: err.error?.message || "Claude API error" });
    }

    const data = await response.json();
    const reply = data.content?.[0]?.text || "";

    return res.status(200).json({ ok: true, reply });
  } catch (err) {
    return res.status(500).json({ error: err.message });
  }
}
