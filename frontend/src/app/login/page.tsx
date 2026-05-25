"use client";

import { FormEvent, useEffect, useState } from "react";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { ErrorMessage } from "@/components/states/ErrorMessage";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { useAuth } from "@/lib/auth";

const featureItems = [
  { label: "Gestión académica integral", icon: AcademicCapIcon },
  { label: "Información en tiempo real", icon: ChartIcon },
  { label: "Seguridad y confidencialidad", icon: ShieldIcon },
  { label: "Historial y trayectoria", icon: DocumentIcon },
];

export default function LoginPage() {
  const { user, loading, login, error } = useAuth();
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!loading && user) router.replace("/dashboard");
  }, [loading, user, router]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    try {
      await login(username, password);
      setPassword("");
      router.replace("/dashboard");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="relative min-h-screen overflow-x-hidden bg-[#f7f1e7] text-[#152b25]">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_16%_18%,rgba(188,149,92,0.20),transparent_23rem),radial-gradient(circle_at_76%_8%,rgba(255,255,255,0.98),transparent_34rem),linear-gradient(115deg,#fffaf1_0%,#f5efe4_54%,#fffaf4_100%)]" />
      <CircuitTopLeft />
      <CircuitBottomRight />
      <ContourLines />
      <div className="absolute -right-24 bottom-0 hidden h-[42vh] w-[40vw] min-w-[420px] bg-[#0d3a30] lg:block" style={{ clipPath: "polygon(35% 22%, 100% 0, 100% 100%, 0 100%)" }} />
      <div className="absolute -right-12 bottom-[15vh] hidden h-[30vh] w-[36vw] min-w-[390px] bg-[#7b123d] lg:block" style={{ clipPath: "polygon(50% 0, 100% 0, 100% 100%, 0 100%)" }} />

      <div className="relative mx-auto grid min-h-screen w-full max-w-[1440px] grid-cols-1 gap-8 px-4 py-6 sm:px-6 lg:grid-cols-[1.04fr_0.96fr] lg:gap-10 lg:px-12 lg:py-8 xl:px-16">
        <section className="relative flex min-h-0 flex-col justify-start pb-0 pt-2 text-center sm:text-left md:min-h-[680px] md:pb-52 lg:min-h-[calc(100vh-4rem)] lg:justify-center lg:pb-64 lg:pt-4">
          <header className="flex flex-col items-center gap-5 sm:flex-row sm:flex-wrap sm:items-center sm:justify-start">
            <div className="flex items-center justify-center gap-4 sm:justify-start sm:gap-5">
              <Image
                src="/brand/institutions/emi-escudo.png"
                alt="Escudo de la Escuela Militar de Ingeniería"
                width={72}
                height={88}
                className="h-16 w-auto object-contain sm:h-20"
                priority
              />
              <div>
                <p className="text-base font-black uppercase tracking-[0.18em] text-[#8b642d] sm:text-xl">Escuela Militar</p>
                <p className="mt-1 text-base font-black uppercase tracking-[0.18em] text-[#8b642d] sm:text-xl">de Ingeniería</p>
              </div>
            </div>
            <div className="hidden h-16 w-px bg-[#b6aa98] sm:block" />
            <Image
              src="/brand/institutions/sedena.png"
              alt="Secretaría de la Defensa Nacional"
              width={278}
              height={57}
              className="h-auto w-48 object-contain sm:w-64"
              priority
            />
          </header>

          <div className="mx-auto mt-10 max-w-3xl sm:mx-0 sm:mt-14">
            <p className="text-sm font-black uppercase tracking-[0.30em] text-[#8b642d] sm:text-base sm:tracking-[0.34em]">Bienvenido al</p>
            <h1 className="mt-4 text-4xl font-black leading-[1.08] tracking-tight text-[#12332b] sm:mt-5 sm:text-5xl xl:text-6xl">
              Sistema de Control Académico <span className="text-[#7a123d]">EMI</span>
            </h1>
            <p className="mx-auto mt-5 max-w-2xl text-base leading-7 text-[#565f5c] sm:mx-0 sm:mt-6 sm:text-xl sm:leading-8">
              Plataforma institucional para el seguimiento de calificaciones, carga académica, actas y trayectoria escolar.
            </p>
          </div>

          <div className="mt-8 hidden max-w-3xl grid-cols-2 gap-4 sm:grid sm:grid-cols-4 sm:gap-6 lg:mt-10">
            {featureItems.map(({ label, icon: Icon }) => (
              <div key={label} className="text-center">
                <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-[#fffaf1]/85 text-[#8b642d] shadow-sm ring-1 ring-[#dfceb3] lg:h-16 lg:w-16">
                  <Icon className="h-7 w-7 lg:h-8 lg:w-8" />
                </div>
                <p className="mt-3 text-xs font-semibold leading-5 text-[#1d2b27] lg:mt-4 lg:text-sm lg:leading-6">{label}</p>
              </div>
            ))}
          </div>

          <div className="pointer-events-none absolute inset-x-[-1.5rem] bottom-0 hidden h-56 overflow-hidden md:block lg:h-72">
            <Image
              src="/brand/login/emi-campus.png"
              alt="Edificio institucional de la Escuela Militar de Ingeniería"
              fill
              className="object-cover object-bottom opacity-95"
              priority
            />
            <div className="absolute inset-0 bg-gradient-to-t from-transparent via-transparent to-[#f7f1e7]/78" />
            <div className="absolute inset-y-0 right-0 w-1/3 bg-gradient-to-l from-[#f7f1e7] to-transparent" />
          </div>
        </section>

        <section className="relative z-10 flex items-center justify-center pb-8 pt-0 lg:py-4">
          <div className="w-full max-w-[560px] rounded-[1.6rem] border border-white/90 bg-white/92 px-5 py-7 shadow-2xl shadow-[#6d5b43]/20 backdrop-blur sm:rounded-[2rem] sm:px-10 sm:py-9 lg:px-12 lg:py-11">
            <div className="mx-auto flex h-24 w-24 items-center justify-center rounded-full border border-[#eadbc4] bg-white shadow-lg shadow-[#6d5b43]/10 sm:h-28 sm:w-28">
              <div className="relative flex h-16 w-16 items-center justify-center rounded-full border border-[#eadbc4] text-[#7a123d] sm:h-20 sm:w-20">
                <ShieldLockIcon className="h-10 w-10 sm:h-12 sm:w-12" />
                <span className="absolute -left-1 top-1 h-1.5 w-1.5 rounded-full bg-[#d3b178]" />
                <span className="absolute -right-1 top-7 h-1.5 w-1.5 rounded-full bg-[#d3b178]" />
                <span className="absolute bottom-1 left-4 h-1.5 w-1.5 rounded-full bg-[#d3b178]" />
              </div>
            </div>

            <div className="mt-7 text-center sm:mt-9">
              <p className="text-xs font-black uppercase tracking-[0.30em] text-[#7a123d] sm:text-sm sm:tracking-[0.34em]">Acceso institucional</p>
              <h2 className="mt-3 text-3xl font-black tracking-tight text-[#12332b] sm:mt-4 sm:text-4xl">Iniciar sesión</h2>
              <p className="mx-auto mt-4 max-w-sm text-sm leading-6 text-[#565f5c] sm:mt-5 sm:text-base sm:leading-7">
                Ingresa con tu usuario autorizado para consultar tu perfil académico.
              </p>
            </div>

            {error ? (
              <div className="mt-6">
                <ErrorMessage message={error} />
              </div>
            ) : null}

            <form onSubmit={handleSubmit} className="mt-6 space-y-5 sm:mt-7 sm:space-y-6">
              <label className="block">
                <span className="mb-2 block text-sm font-black text-[#152b25]">Usuario</span>
                <div className="relative">
                  <UserIcon className="pointer-events-none absolute left-5 top-1/2 h-6 w-6 -translate-y-1/2 text-[#8a8f8d]" />
                  <Input
                    value={username}
                    onChange={(event) => setUsername(event.target.value)}
                    autoComplete="username"
                    placeholder="Usuario institucional"
                    required
                    className="h-14 rounded-xl border-[#d9d6ce] bg-white pl-14 pr-4 text-base shadow-sm focus:border-[#7a123d] focus:ring-[#7a123d]/10"
                  />
                </div>
              </label>
              <label className="block">
                <span className="mb-2 block text-sm font-black text-[#152b25]">Contraseña</span>
                <div className="relative">
                  <LockIcon className="pointer-events-none absolute left-5 top-1/2 h-6 w-6 -translate-y-1/2 text-[#8a8f8d]" />
                  <Input
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    type="password"
                    autoComplete="current-password"
                    placeholder="Contraseña"
                    required
                    className="h-14 rounded-xl border-[#d9d6ce] bg-white pl-14 pr-4 text-base shadow-sm focus:border-[#7a123d] focus:ring-[#7a123d]/10"
                  />
                </div>
              </label>
              <Button type="submit" className="h-14 w-full rounded-xl bg-gradient-to-r from-[#6b1238] via-[#8b1748] to-[#7a123d] text-base font-black shadow-xl shadow-[#7a123d]/25 hover:from-[#5c0f30] hover:via-[#7a123d] hover:to-[#651032] sm:h-16 sm:text-lg">
                {submitting ? "Validando acceso..." : "Iniciar sesión"}
                <span className="ml-4 text-3xl leading-none">→</span>
              </Button>
            </form>

            <div className="mt-7 flex items-start gap-4 rounded-xl border border-[#eadbc4] bg-[#fffaf8] p-4 text-sm leading-6 text-[#565f5c] shadow-sm sm:mt-9 sm:p-5">
              <ShieldCheckIcon className="mt-0.5 h-7 w-7 flex-none text-[#8b642d] sm:h-8 sm:w-8" />
              <p>Tu información está protegida bajo estándares institucionales de seguridad y confidencialidad.</p>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}

function AcademicCapIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="m3 8.5 9-4 9 4-9 4-9-4Z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
      <path d="M7 10.5v4.2c0 1.1 2.2 2.8 5 2.8s5-1.7 5-2.8v-4.2" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      <path d="M21 8.5v5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

function ChartIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M5 18V11M12 18V7M19 18V4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      <path d="M4 18h16" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      <path d="M4 21h16" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

function ShieldIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M12 3.5 19 6v5.5c0 4.5-3 7.8-7 9-4-1.2-7-4.5-7-9V6l7-2.5Z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
    </svg>
  );
}

function DocumentIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M7 3.5h7l4 4V20H7V3.5Z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
      <path d="M14 3.5V8h4M10 12h5M10 16h5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

function ShieldLockIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 64 64" fill="none" aria-hidden="true">
      <path d="M32 7 51 14v14c0 12.8-8.3 22.6-19 27-10.7-4.4-19-14.2-19-27V14l19-7Z" stroke="currentColor" strokeWidth="3" strokeLinejoin="round" />
      <path d="M24 30h16v14H24V30Z" fill="currentColor" />
      <path d="M27.5 30v-5a4.5 4.5 0 0 1 9 0v5" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
      <path d="M32 35v4" stroke="#fff" strokeWidth="2.4" strokeLinecap="round" />
    </svg>
  );
}

function UserIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8ZM4.5 21a7.5 7.5 0 0 1 15 0" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

function LockIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M7 10V8a5 5 0 0 1 10 0v2" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      <path d="M6 10h12v10H6V10Z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
      <path d="M12 14v2" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

function ShieldCheckIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M12 3.5 19 6v5.5c0 4.5-3 7.8-7 9-4-1.2-7-4.5-7-9V6l7-2.5Z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
      <path d="m8.7 12.2 2.2 2.2 4.6-5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function CircuitTopLeft() {
  return (
    <svg className="pointer-events-none absolute left-0 top-0 h-48 w-48 text-[#d0ad72] opacity-35 sm:h-72 sm:w-72 sm:opacity-55" viewBox="0 0 288 288" fill="none" aria-hidden="true">
      <path d="M0 80h24l35-35h52M0 122h34l55-55h84M0 164h56l74-74h96M0 204h78l85-85h62" stroke="currentColor" strokeWidth="1" />
      {[24, 59, 111, 34, 89, 173, 56, 130, 226, 78, 163, 225].map((value, index) => (
        <circle key={`${value}-${index}`} cx={index % 3 === 0 ? value : value + 4} cy={index < 3 ? 80 - index * 17 : index < 6 ? 122 - (index - 3) * 28 : index < 9 ? 164 - (index - 6) * 37 : 204 - (index - 9) * 42} r="4" stroke="currentColor" strokeWidth="1" />
      ))}
    </svg>
  );
}

function CircuitBottomRight() {
  return (
    <svg className="pointer-events-none absolute bottom-0 right-0 hidden h-80 w-80 text-[#d0ad72] opacity-65 lg:block" viewBox="0 0 320 320" fill="none" aria-hidden="true">
      <path d="M320 170h-28l-44 44h-58M320 210h-44l-52 52h-86M320 252h-62l-58 58h-120" stroke="currentColor" strokeWidth="1" />
      <path d="M246 214v-34M190 214v-45M138 262v-32" stroke="currentColor" strokeWidth="1" />
      {[292, 248, 190, 276, 224, 138, 258, 200, 80].map((value, index) => (
        <circle key={`${value}-${index}`} cx={index % 3 === 0 ? value : value} cy={index < 3 ? 170 + index * 44 : index < 6 ? 210 + (index - 3) * 52 : 252 + (index - 6) * 58} r="4" stroke="currentColor" strokeWidth="1" />
      ))}
    </svg>
  );
}

function ContourLines() {
  return (
    <svg className="pointer-events-none absolute bottom-8 left-0 hidden h-56 w-[54vw] text-[#d8c6a7] opacity-45 md:block" viewBox="0 0 800 240" fill="none" aria-hidden="true">
      <path d="M0 100c90-60 160 70 250 10s150-75 250-20 180-35 300-5" stroke="currentColor" />
      <path d="M0 125c95-55 165 75 255 15s150-75 245-15 175-38 300-8" stroke="currentColor" />
      <path d="M0 150c100-50 170 80 260 20s150-70 245-12 170-35 295-5" stroke="currentColor" />
      <path d="M0 175c105-45 175 85 265 25s150-68 245-10 168-32 290-2" stroke="currentColor" />
    </svg>
  );
}
