import { useState } from "react";
import { useScrollAnimation } from "@/hooks/useScrollAnimation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { Send } from "lucide-react";
import { useLanguage } from "@/i18n/LanguageContext";

interface FormData {
  name: string;
  company: string;
  email: string;
  phone: string;
  message: string;
  selected_plan: string;
}

const initialForm: FormData = { name: "", company: "", email: "", phone: "", message: "", selected_plan: "" };

const PLANS = [
  { value: "MICRO", label: "MICRO — до 5 ПК (4 500 000 сум)" },
  { value: "START", label: "START — до 20 ПК (9 000 000 сум)" },
  { value: "BUSINESS", label: "BUSINESS — до 40 ПК (14 000 000 сум)" },
  { value: "ENTERPRISE", label: "ENTERPRISE — до 60 ПК (21 000 000 сум)" },
  { value: "PRO", label: "PRO — инженер в офисе, до 75 ПК (от 45 000 000 сум)" },
];

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
  const { t } = useLanguage();

  const [form, setForm] = useState<FormData>(initialForm);
  const [errors, setErrors] = useState<Partial<FormData>>({});
  const [submitting, setSubmitting] = useState(false);
  const [honeypot, setHoneypot] = useState("");

  const validate = (): boolean => {
    const e: Partial<FormData> = {};
    if (!form.name.trim()) e.name = t("contact.err_name");
    if (form.name.trim().length > 100) e.name = t("contact.err_name_long");
    if (!form.company.trim()) e.company = t("contact.err_company");
    if (form.company.trim().length > 200) e.company = t("contact.err_company_long");
    if (!form.email.trim() || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) e.email = t("contact.err_email");
    if (!form.phone.trim() || form.phone.replace(/\D/g, "").length < 9) e.phone = t("contact.err_phone");
    if (form.message && form.message.length > 2000) e.message = t("contact.err_message");
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    setSubmitting(true);

    try {
      const planInfo = form.selected_plan ? `\nИнтересующий тариф: ${form.selected_plan}` : "";
      const fullMessage = (form.message.trim() + planInfo).trim();

      const resp = await fetch("/api/audit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: form.name.trim(),
          company: form.company.trim(),
          email: form.email.trim(),
          phone: form.phone.trim(),
          message: fullMessage,
          selected_plan: form.selected_plan,
          honeypot,
        }),
      });

      const data = await resp.json();
      if (!resp.ok) throw new Error((data as any)?.error || "Ошибка отправки");

      toast({ title: t("contact.success"), description: t("contact.success_desc") });
      setForm(initialForm);
      setErrors({});
    } catch (err: any) {
      toast({
        title: t("contact.error"),
        description: err?.message || "Ошибка отправки",
        variant: "destructive",
      });
    } finally {
      setSubmitting(false);
    }
  };

  const set = (key: keyof FormData, val: string) => {
    setForm((p) => ({ ...p, [key]: val }));
    if (errors[key]) setErrors((p) => ({ ...p, [key]: undefined }));
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* ТУТ МОЖЕШЬ ОСТАВИТЬ СВОЙ JSX БЕЗ ИЗМЕНЕНИЙ */}
    </form>
  );
};

export default ContactForm;
