import { DashboardCard } from "./DashboardCard";
import type { DashboardCardItem } from "@/lib/dashboard";

export function DashboardGrid({ cards }: { cards: DashboardCardItem[] }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 2xl:grid-cols-4">
      {cards.map((card, index) => <DashboardCard key={`${card.title}-${card.href ?? index}`} item={card} index={index} />)}
    </div>
  );
}
