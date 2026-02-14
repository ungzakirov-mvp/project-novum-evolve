import { useState } from "react";
import { useScrollAnimation } from "@/hooks/useScrollAnimation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";
import { Send } from "lucide-react";
import { supabase } from "@/integrations/supabase/client";

interface FormData {
  name: string;
  company: string;
  email: string;
  phone: string;
  message: string;
}

const initialForm: FormData = { name: "", company: "", email: "", phone: "", message: "" };

const formatPhone = (value: string): string => {
  const digits = value.replace(/\D/g, "");
  if (digits.length <= 3) return digits.length ? `+${digits}` : "";
  if (digits.length <= 5) return `+${digits.slice(0, 3)} ${digits.slice(3)}`;
  if (digits.length <= 7) return `+${digits.slice(0, 3)} ${digits.slice(3, 5)} ${digits.slice(5)}`;
  if (digits.length <= 9) return `+${digits.slice(0, 3)} ${digits.slice(3, 5)} ${digits.slice(5, 8)}-${digits.slice(8)}`;
  return `+${digits.slice(0, 3)} ${digits.slice(3, 5)} ${digits.slice(5, 8)}-${digits.slice(8, 10)}-${digits.slice(10, 12)}`;
};

const ContactForm = () => {
  const ref = useScrollAnimation();
  const { toast } = useToast();
  const [form, setForm] = useState<FormData>(initialForm);
  const [errors, setErrors] = useState<Partial<FormData>>({});
  const [submitting, setSubmitting] = useState(false);
  const [honeypot, setHoneypot] = useState("");

  const validate = (): boolean => {
    const e: Partial<FormData> = {};
    if (!form.name.trim()) e.name = "Укажите имя";
    if (form.name.trim().length > 100) e.name = "Имя слишком длинное";
    if (!form.company.trim()) e.company = "Укажите компанию";
    if (form.company.trim().length > 200) e.company = "Название слишком длинное";
    if (!form.email.trim() || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) e.email = "Укажите корректный email";
    if (!form.phone.trim() || form.phone.replace(/\D/g, "").length < 9) e.phone = "Укажите корректный телефон";
    if (form.message && form.message.length > 2000) e.message = "Сообщение слишком длинное";
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;
    setSubmitting(true);

    try {
      const { data, error } = await supabase.functions.invoke("submit-contact", {
        body: {
          name: form.name.trim(),
          company: form.company.trim(),
          email: form.email.trim(),
          phone: form.phone.trim(),
          message: form.message.trim() || undefined,
          honeypot,
        },
      });

      if (error) throw error;
      if (data && !data.success) throw new Error(data.error || "Ошибка отправки");

      toast({ title: "Заявка отправлена!", description: "Мы свяжемся с вами в ближайшее время." });
      setForm(initialForm);
      setErrors({});
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Ошибка отправки заявки";
      toast({ title: "Ошибка", description: msg, variant: "destructive" });
    } finally {
      setSubmitting(false);
    }
  };

  const set = (key: keyof FormData, val: string) => {
    setForm((p) => ({ ...p, [key]: val }));
    if (errors[key]) setErrors((p) => ({ ...p, [key]: undefined }));
  };

  return (
    <section id="contact" className="py-20 md:py-28">
      <div ref={ref} className="section-fade-in container mx-auto px-4 lg:px-8 max-w-2xl">
        <div className="text-center mb-14">
          <h2 className="text-3xl sm:text-4xl font-bold mb-4">Запросить IT-аудит</h2>
          <p className="text-muted-foreground">Оставьте заявку — мы проведём бесплатный экспресс-аудит вашей IT-инфраструктуры</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5 rounded-xl border border-border bg-card p-8">
          {/* Honeypot */}
          <div className="absolute -left-[9999px]" aria-hidden="true">
            <input type="text" tabIndex={-1} autoComplete="off" value={honeypot} onChange={(e) => setHoneypot(e.target.value)} />
          </div>

          <div className="grid sm:grid-cols-2 gap-5">
            <div>
              <label className="text-sm font-medium mb-1.5 block">Имя *</label>
              <Input value={form.name} onChange={(e) => set("name", e.target.value)} placeholder="Ваше имя" maxLength={100} />
              {errors.name && <p className="text-xs text-destructive mt-1">{errors.name}</p>}
            </div>
            <div>
              <label className="text-sm font-medium mb-1.5 block">Компания *</label>
              <Input value={form.company} onChange={(e) => set("company", e.target.value)} placeholder="Название компании" maxLength={200} />
              {errors.company && <p className="text-xs text-destructive mt-1">{errors.company}</p>}
            </div>
          </div>
          <div className="grid sm:grid-cols-2 gap-5">
            <div>
              <label className="text-sm font-medium mb-1.5 block">Email *</label>
              <Input type="email" value={form.email} onChange={(e) => set("email", e.target.value)} placeholder="email@company.uz" maxLength={255} />
              {errors.email && <p className="text-xs text-destructive mt-1">{errors.email}</p>}
            </div>
            <div>
              <label className="text-sm font-medium mb-1.5 block">Телефон *</label>
              <Input
                value={form.phone}
                onChange={(e) => set("phone", formatPhone(e.target.value))}
                placeholder="+998 ..."
                maxLength={20}
              />
              {errors.phone && <p className="text-xs text-destructive mt-1">{errors.phone}</p>}
            </div>
          </div>
          <div>
            <label className="text-sm font-medium mb-1.5 block">Комментарий</label>
            <Textarea value={form.message} onChange={(e) => set("message", e.target.value)} placeholder="Опишите вашу задачу или вопрос..." rows={4} maxLength={2000} />
          </div>
          <Button type="submit" size="lg" className="w-full py-6" disabled={submitting}>
            {submitting ? "Отправка..." : "Отправить заявку"}
            {!submitting && <Send className="ml-2" size={18} />}
          </Button>
        </form>
      </div>
    </section>
  );
};

export default ContactForm;
