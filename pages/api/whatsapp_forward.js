export default function handler(req, res) {
  const secret = process.env.WEBHOOK_SECRET || "";
  if (req.method !== "POST") return res.status(405).end();
  if (req.headers["x-webhook-secret"] !== secret) return res.status(401).json({ error: "unauthorized" });
  return res.status(200).json({ status: "received", receivedText: req.body?.text ?? null });
}
