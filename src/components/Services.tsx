import { useScrollAnimation } from "@/hooks/useScrollAnimation";
import {
  Server, ShieldCheck, Monitor, KeyRound,
  ShieldAlert, Printer, Bug, Flame,
  HardDrive, Cloud, Lock, Mail,
  Eye, Network
} from "lucide-react";

const services = [
  {
    icon: Server,
    title: "Server Management",
    subtitle: "Серверные решения",
    desc: "Проектирование, настройка и сопровождение серверной инфраструктуры. Мониторинг 24/7, резервное копирование и отказоустойчивость.",
  },
  {
    icon: ShieldCheck,
    title: "IT Security Audit",
    subtitle: "Безопасность IT",
    desc: "Комплексный аудит безопасности, выявление уязвимостей, настройка защиты данных и соответствие стандартам информационной безопасности.",
  },
  {
    icon: Monitor,
    title: "Workstation Support",
    subtitle: "Поддержка оборудования",
    desc: "Обслуживание и настройка рабочих станций, установка ПО, оперативное решение проблем пользователей и техническая поддержка.",
  },
];

const licenseCategories = [
  {
    group: "Программное обеспечение",
    items: [
      { icon: KeyRound, name: "Microsoft 365, Windows Server, Azure" },
      { icon: Mail, name: "Корпоративные почтовые решения" },
      { icon: Cloud, name: "Облачные решения и миграция" },
    ],
  },
  {
    group: "Безопасность",
    items: [
      { icon: Bug, name: "ESET NOD32 и антивирусы корпоративного уровня" },
      { icon: ShieldAlert, name: "DLP-системы и Endpoint Protection" },
      { icon: Eye, name: "SIEM-системы мониторинга" },
    ],
  },
  {
    group: "Инфраструктура",
    items: [
      { icon: Flame, name: "Firewall решения и VPN" },
      { icon: HardDrive, name: "Backup-системы и восстановление" },
      { icon: Printer, name: "Системы безопасной печати" },
      { icon: Network, name: "Сетевая инфраструктура" },
    ],
  },
];

const Services = () => {
  const ref = useScrollAnimation();
  const ref2 = useScrollAnimation();

  return (
    <section id="services" className="py-20 md:py-28">
      <div ref={ref} className="section-fade-in container mx-auto px-4 lg:px-8">
        <div className="text-center mb-14">
          <h2 className="text-3xl sm:text-4xl font-bold mb-4">Наши услуги</h2>
          <p className="text-muted-foreground max-w-xl mx-auto">
            Комплексное IT-обслуживание для стабильной работы вашего бизнеса
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6 lg:gap-8">
          {services.map((s) => (
            <div
              key={s.title}
              className="group rounded-xl border border-border bg-card p-8 transition-all duration-300 hover:-translate-y-1 hover:border-primary/40 hover:shadow-[0_8px_30px_-12px_hsl(var(--primary)/0.3)]"
            >
              <div className="w-14 h-14 rounded-lg bg-primary/10 flex items-center justify-center mb-5 group-hover:bg-primary/20 transition-colors">
                <s.icon className="text-primary" size={28} />
              </div>
              <h3 className="text-xl font-semibold mb-1">{s.title}</h3>
              <p className="text-sm text-primary mb-3">{s.subtitle}</p>
              <p className="text-muted-foreground text-sm leading-relaxed">{s.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Licenses subsection */}
      <div ref={ref2} className="section-fade-in container mx-auto px-4 lg:px-8 mt-20">
        <div className="text-center mb-14">
          <h2 className="text-3xl sm:text-4xl font-bold mb-4">Продажа и интеграция лицензий</h2>
          <p className="text-muted-foreground max-w-xl mx-auto">
            Поставка, лицензирование и внедрение корпоративного ПО и решений безопасности
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6 lg:gap-8">
          {licenseCategories.map((cat) => (
            <div key={cat.group} className="rounded-xl border border-border bg-card p-8">
              <h3 className="text-lg font-semibold mb-6 text-primary">{cat.group}</h3>
              <div className="space-y-4">
                {cat.items.map((item) => (
                  <div key={item.name} className="flex items-start gap-3">
                    <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center shrink-0">
                      <item.icon className="text-primary" size={20} />
                    </div>
                    <span className="text-sm text-foreground/90 pt-2">{item.name}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Services;
