import { Badge } from "@/components/ui/badge";

interface SkillBadgeProps {
  skill: string;
  variant?: "default" | "matched" | "missing";
}

export function SkillBadge({ skill, variant = "default" }: SkillBadgeProps) {
  const styles = {
    default: "bg-[#292C37] text-[#F0F0F0] border-[#3a3d4a]",
    matched: "bg-[#B11623]/20 text-[#F0F0F0] border-[#B11623]/40",
    missing: "bg-[#292C37] text-[#CCCCCC] border-[#3a3d4a] opacity-60",
  };

  return (
    <Badge className={`${styles[variant]} border text-xs font-medium`}>
      {skill}
    </Badge>
  );
}
