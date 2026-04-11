import { Badge } from "@/components/ui/badge";

interface SkillBadgeProps {
  skill: string;
  variant?: "default" | "matched" | "missing";
}

export function SkillBadge({ skill, variant = "default" }: SkillBadgeProps) {
  const styles = {
    default: "bg-[#1E2433] text-[#F1F5F9] border-[#2a3044]",
    matched: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    missing: "bg-[#1E2433] text-[#94A3B8] border-[#2a3044] opacity-60",
  };

  return (
    <Badge className={`${styles[variant]} border text-xs font-medium`}>
      {skill}
    </Badge>
  );
}
