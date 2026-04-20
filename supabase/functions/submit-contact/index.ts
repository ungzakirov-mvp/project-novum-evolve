import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type, x-supabase-client-platform, x-supabase-client-platform-version, x-supabase-client-runtime, x-supabase-client-runtime-version",
};

interface ContactPayload {
  name: string;
  company: string;
  email: string;
  phone: string;
  message?: string;
  honeypot?: string;
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const body: ContactPayload = await req.json();

    // Honeypot anti-spam check
    if (body.honeypot) {
      return new Response(JSON.stringify({ success: true }), {
        status: 200,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    // Validation
    if (!body.name?.trim()) throw new Error("Имя обязательно");
    if (!body.company?.trim()) throw new Error("Компания обязательна");
    const hasEmail = body.email?.trim() && body.email.trim() !== "—";
    if (hasEmail && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(body.email!))
      throw new Error("Некорректный email");
    if (!body.phone?.trim()) throw new Error("Телефон обязателен");
    if (body.name.length > 100) throw new Error("Имя слишком длинное");
    if (body.company.length > 200) throw new Error("Название компании слишком длинное");
    if (body.email.length > 255) throw new Error("Email слишком длинный");
    if (body.phone.length > 30) throw new Error("Телефон слишком длинный");
    if (body.message && body.message.length > 2000) throw new Error("Сообщение слишком длинное");

    const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
    const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
    const supabase = createClient(supabaseUrl, supabaseKey);

    // Save to database
    const { error: dbError } = await supabase.from("contact_requests").insert({
      name: body.name.trim(),
      company: body.company.trim(),
      email: hasEmail ? body.email!.trim() : "",
      phone: body.phone.trim(),
      message: body.message?.trim() || null,
    });

    if (dbError) {
      console.error("DB error:", dbError);
      throw new Error("Ошибка сохранения заявки");
    }

    // Escape HTML to prevent injection in email body
    const escapeHtml = (v: string) =>
      String(v ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");

    const safeName = escapeHtml(body.name.trim());
    const safeCompany = escapeHtml(body.company.trim());
    const safeEmail = escapeHtml(hasEmail ? body.email!.trim() : "—");
    const safePhone = escapeHtml(body.phone.trim());
    const safeMessage = body.message ? escapeHtml(body.message.trim()) : "";
    // Subject must be plain text — strip newlines to prevent header injection
    const safeSubject = `Новая заявка от ${body.name.trim()} — ${body.company.trim()}`
      .replace(/[\r\n]+/g, " ")
      .slice(0, 200);

    // Send notification email via Resend (if configured)
    const resendKey = Deno.env.get("RESEND_API_KEY");
    if (resendKey) {
      try {
        const emailRes = await fetch("https://api.resend.com/emails", {
          method: "POST",
          headers: {
            Authorization: `Bearer ${resendKey}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            from: "Novum Tech <onboarding@resend.dev>",
            to: ["support@novumtech.uz"],
            subject: safeSubject,
            html: `
              <h2>Новая заявка с сайта Novum Tech</h2>
              <p><strong>Имя:</strong> ${safeName}</p>
              <p><strong>Компания:</strong> ${safeCompany}</p>
              <p><strong>Email:</strong> ${safeEmail}</p>
              <p><strong>Телефон:</strong> ${safePhone}</p>
              ${safeMessage ? `<p><strong>Комментарий:</strong> ${safeMessage}</p>` : ""}
              <hr/>
              <p style="color:#888">Отправлено с novumtech.uz</p>
            `,
          }),
        });

        if (!emailRes.ok) {
          const errData = await emailRes.text();
          console.error(`Resend API error [${emailRes.status}]:`, errData);
        }
      } catch (emailErr) {
        console.error("Email send error:", emailErr);
      }
    } else {
      console.log("RESEND_API_KEY not configured — email notification skipped");
    }

    return new Response(JSON.stringify({ success: true }), {
      status: 200,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : "Неизвестная ошибка";
    console.error("Contact form error:", message);
    return new Response(JSON.stringify({ success: false, error: message }), {
      status: 400,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
