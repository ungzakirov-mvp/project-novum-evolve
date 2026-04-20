function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function isValidEmail(email) {
  return typeof email === 'string' && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Only POST allowed' });
  }

  const { name, email, phone, message } = req.body || {};

  // Input validation
  if (!name || typeof name !== 'string' || name.trim().length === 0 || name.length > 200) {
    return res.status(400).json({ error: 'Invalid name' });
  }
  if (!email || !isValidEmail(email) || email.length > 320) {
    return res.status(400).json({ error: 'Invalid email' });
  }
  if (!phone || typeof phone !== 'string' || phone.trim().length === 0 || phone.length > 50) {
    return res.status(400).json({ error: 'Invalid phone' });
  }
  if (message && (typeof message !== 'string' || message.length > 5000)) {
    return res.status(400).json({ error: 'Invalid message' });
  }

  const safeName = escapeHtml(name.trim());
  const safeEmail = escapeHtml(email.trim());
  const safePhone = escapeHtml(phone.trim());
  const safeMessage = message ? escapeHtml(message.trim()) : '';

  const response = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.RESEND_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      from: process.env.MAIL_FROM,
      to: ['support@novumtech.uz'],
      subject: 'New Audit Request',
      html: `
        <h2>New Audit Request</h2>
        <p><b>Name:</b> ${safeName}</p>
        <p><b>Email:</b> ${safeEmail}</p>
        <p><b>Phone:</b> ${safePhone}</p>
        <p><b>Message:</b> ${safeMessage}</p>
      `
    }),
  });

  if (!response.ok) {
    return res.status(500).json({ error: 'Email failed' });
  }

  return res.status(200).json({ success: true });
}
