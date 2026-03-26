import { useEffect, useMemo, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

type Project = {
  id: string;
  name: string;
  description: string;
};

type TransactionType = "income" | "expense";
type ExpenseCategory = "finance" | "material" | "service";

type Transaction = {
  id: string;
  projectId: string;
  type: TransactionType;
  category: ExpenseCategory;
  amount: number;
  date: string;
  comment: string;
};

type Credential = {
  id: string;
  projectId: string;
  service: string;
  login: string;
  password: string;
  note: string;
};

type StoredData = {
  projects: Project[];
  transactions: Transaction[];
  credentials: Credential[];
};

const STORAGE_KEY = "finance-project-tracker-v1";

const defaultData: StoredData = {
  projects: [],
  transactions: [],
  credentials: [],
};

const FinanceTrackerPage = () => {
  const [data, setData] = useState<StoredData>(defaultData);

  const [projectName, setProjectName] = useState("");
  const [projectDescription, setProjectDescription] = useState("");

  const [selectedProjectForTransaction, setSelectedProjectForTransaction] = useState("");
  const [transactionType, setTransactionType] = useState<TransactionType>("income");
  const [transactionCategory, setTransactionCategory] = useState<ExpenseCategory>("finance");
  const [transactionAmount, setTransactionAmount] = useState("");
  const [transactionDate, setTransactionDate] = useState(() => new Date().toISOString().slice(0, 10));
  const [transactionComment, setTransactionComment] = useState("");

  const [selectedProjectForCredential, setSelectedProjectForCredential] = useState("");
  const [credentialService, setCredentialService] = useState("");
  const [credentialLogin, setCredentialLogin] = useState("");
  const [credentialPassword, setCredentialPassword] = useState("");
  const [credentialNote, setCredentialNote] = useState("");

  useEffect(() => {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return;

    try {
      const parsed = JSON.parse(raw) as StoredData;
      setData(parsed);
    } catch {
      setData(defaultData);
    }
  }, []);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  }, [data]);

  useEffect(() => {
    if (!selectedProjectForTransaction && data.projects[0]) {
      setSelectedProjectForTransaction(data.projects[0].id);
    }

    if (!selectedProjectForCredential && data.projects[0]) {
      setSelectedProjectForCredential(data.projects[0].id);
    }
  }, [data.projects, selectedProjectForCredential, selectedProjectForTransaction]);

  const projectStats = useMemo(() => {
    return data.projects.map((project) => {
      const tx = data.transactions.filter((item) => item.projectId === project.id);
      const income = tx.filter((item) => item.type === "income").reduce((sum, item) => sum + item.amount, 0);
      const expense = tx.filter((item) => item.type === "expense").reduce((sum, item) => sum + item.amount, 0);

      return {
        project,
        income,
        expense,
        balance: income - expense,
      };
    });
  }, [data.projects, data.transactions]);

  const addProject = () => {
    if (!projectName.trim()) return;

    const project: Project = {
      id: crypto.randomUUID(),
      name: projectName.trim(),
      description: projectDescription.trim(),
    };

    setData((prev) => ({ ...prev, projects: [...prev.projects, project] }));
    setProjectName("");
    setProjectDescription("");
  };

  const addTransaction = () => {
    const amount = Number(transactionAmount);
    if (!selectedProjectForTransaction || Number.isNaN(amount) || amount <= 0) return;

    const transaction: Transaction = {
      id: crypto.randomUUID(),
      projectId: selectedProjectForTransaction,
      type: transactionType,
      category: transactionCategory,
      amount,
      date: transactionDate,
      comment: transactionComment.trim(),
    };

    setData((prev) => ({ ...prev, transactions: [transaction, ...prev.transactions] }));
    setTransactionAmount("");
    setTransactionComment("");
  };

  const addCredential = () => {
    if (!selectedProjectForCredential || !credentialService.trim() || !credentialLogin.trim()) return;

    const credential: Credential = {
      id: crypto.randomUUID(),
      projectId: selectedProjectForCredential,
      service: credentialService.trim(),
      login: credentialLogin.trim(),
      password: credentialPassword,
      note: credentialNote.trim(),
    };

    setData((prev) => ({ ...prev, credentials: [credential, ...prev.credentials] }));
    setCredentialService("");
    setCredentialLogin("");
    setCredentialPassword("");
    setCredentialNote("");
  };

  const getProjectName = (projectId: string) => data.projects.find((project) => project.id === projectId)?.name ?? "—";

  return (
    <main className="min-h-screen bg-slate-50 p-4 md:p-8">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Учёт финансов, материалов и услуг по проектам</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-slate-600">
            Добавляйте проекты, фиксируйте приходы/расходы и храните учётные данные (логины/пароли) по каждому проекту.
          </CardContent>
        </Card>

        <div className="grid gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Новый проект</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="project-name">Название проекта</Label>
                <Input
                  id="project-name"
                  value={projectName}
                  onChange={(event) => setProjectName(event.target.value)}
                  placeholder="Например: ЖК Север"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="project-description">Описание</Label>
                <Textarea
                  id="project-description"
                  value={projectDescription}
                  onChange={(event) => setProjectDescription(event.target.value)}
                  placeholder="Адрес, заказчик, комментарии"
                />
              </div>
              <Button onClick={addProject}>Добавить проект</Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Добавить операцию</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="tx-project">Проект</Label>
                <select
                  id="tx-project"
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={selectedProjectForTransaction}
                  onChange={(event) => setSelectedProjectForTransaction(event.target.value)}
                >
                  <option value="">Выберите проект</option>
                  {data.projects.map((project) => (
                    <option key={project.id} value={project.id}>
                      {project.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="tx-type">Тип</Label>
                  <select
                    id="tx-type"
                    className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                    value={transactionType}
                    onChange={(event) => setTransactionType(event.target.value as TransactionType)}
                  >
                    <option value="income">Приход</option>
                    <option value="expense">Расход</option>
                  </select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="tx-category">Категория</Label>
                  <select
                    id="tx-category"
                    className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                    value={transactionCategory}
                    onChange={(event) => setTransactionCategory(event.target.value as ExpenseCategory)}
                  >
                    <option value="finance">Финансы</option>
                    <option value="material">Расходные материалы</option>
                    <option value="service">Услуги</option>
                  </select>
                </div>
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="tx-amount">Сумма</Label>
                  <Input
                    id="tx-amount"
                    type="number"
                    min="0"
                    value={transactionAmount}
                    onChange={(event) => setTransactionAmount(event.target.value)}
                    placeholder="0"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="tx-date">Дата</Label>
                  <Input
                    id="tx-date"
                    type="date"
                    value={transactionDate}
                    onChange={(event) => setTransactionDate(event.target.value)}
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="tx-comment">Комментарий</Label>
                <Input
                  id="tx-comment"
                  value={transactionComment}
                  onChange={(event) => setTransactionComment(event.target.value)}
                  placeholder="Номер счета, примечание"
                />
              </div>
              <Button onClick={addTransaction}>Сохранить операцию</Button>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Баланс по проектам</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-slate-500">
                    <th className="px-2 py-2">Проект</th>
                    <th className="px-2 py-2">Приход</th>
                    <th className="px-2 py-2">Расход</th>
                    <th className="px-2 py-2">Баланс</th>
                  </tr>
                </thead>
                <tbody>
                  {projectStats.map((item) => (
                    <tr key={item.project.id} className="border-b">
                      <td className="px-2 py-2">
                        <div className="font-medium">{item.project.name}</div>
                        <div className="text-xs text-slate-500">{item.project.description}</div>
                      </td>
                      <td className="px-2 py-2 text-emerald-600">{item.income.toLocaleString("ru-RU")}</td>
                      <td className="px-2 py-2 text-rose-600">{item.expense.toLocaleString("ru-RU")}</td>
                      <td className={`px-2 py-2 font-semibold ${item.balance >= 0 ? "text-emerald-700" : "text-rose-700"}`}>
                        {item.balance.toLocaleString("ru-RU")}
                      </td>
                    </tr>
                  ))}
                  {projectStats.length === 0 && (
                    <tr>
                      <td className="px-2 py-6 text-center text-slate-500" colSpan={4}>
                        Пока нет проектов.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        <div className="grid gap-6 lg:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Учётные записи по проектам</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="cred-project">Проект</Label>
                <select
                  id="cred-project"
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={selectedProjectForCredential}
                  onChange={(event) => setSelectedProjectForCredential(event.target.value)}
                >
                  <option value="">Выберите проект</option>
                  {data.projects.map((project) => (
                    <option key={project.id} value={project.id}>
                      {project.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="cred-service">Сервис / сайт</Label>
                <Input
                  id="cred-service"
                  value={credentialService}
                  onChange={(event) => setCredentialService(event.target.value)}
                  placeholder="Например: supplier.example.com"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="cred-login">Логин</Label>
                <Input
                  id="cred-login"
                  value={credentialLogin}
                  onChange={(event) => setCredentialLogin(event.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="cred-password">Пароль</Label>
                <Input
                  id="cred-password"
                  type="password"
                  value={credentialPassword}
                  onChange={(event) => setCredentialPassword(event.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="cred-note">Примечание</Label>
                <Input
                  id="cred-note"
                  value={credentialNote}
                  onChange={(event) => setCredentialNote(event.target.value)}
                  placeholder="Для чего нужна эта учётка"
                />
              </div>
              <Button onClick={addCredential}>Сохранить учётку</Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Список операций и учёток</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h3 className="mb-2 font-medium">Последние операции</h3>
                <div className="max-h-64 space-y-2 overflow-auto">
                  {data.transactions.map((item) => (
                    <div key={item.id} className="rounded-md border p-2 text-sm">
                      <div className="font-medium">{getProjectName(item.projectId)}</div>
                      <div>
                        {item.type === "income" ? "Приход" : "Расход"} · {item.category} · {item.amount.toLocaleString("ru-RU")} · {item.date}
                      </div>
                      {item.comment && <div className="text-slate-500">{item.comment}</div>}
                    </div>
                  ))}
                  {data.transactions.length === 0 && <p className="text-sm text-slate-500">Операций пока нет.</p>}
                </div>
              </div>

              <div>
                <h3 className="mb-2 font-medium">Учётные данные</h3>
                <div className="max-h-64 space-y-2 overflow-auto">
                  {data.credentials.map((item) => (
                    <div key={item.id} className="rounded-md border p-2 text-sm">
                      <div className="font-medium">{getProjectName(item.projectId)}</div>
                      <div>{item.service}</div>
                      <div>Логин: {item.login}</div>
                      <div>Пароль: {item.password ? "••••••••" : "(не указан)"}</div>
                      {item.note && <div className="text-slate-500">{item.note}</div>}
                    </div>
                  ))}
                  {data.credentials.length === 0 && <p className="text-sm text-slate-500">Учёток пока нет.</p>}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </main>
  );
};

export default FinanceTrackerPage;
