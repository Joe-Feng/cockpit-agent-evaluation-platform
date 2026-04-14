type QuickActionCardProps = {
  title: string;
  description: string;
  href: string;
};

export function QuickActionCard({ title, description, href }: QuickActionCardProps) {
  return (
    <a className="panel" href={href}>
      <p className="eyebrow">快捷动作</p>
      <h4>{title}</h4>
      <p className="body-muted">{description}</p>
    </a>
  );
}
