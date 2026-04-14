import type { ReactNode } from "react";

type DetailDrawerProps = {
  title: string;
  description?: string;
  children?: ReactNode;
};

export function DetailDrawer({ title, description, children }: DetailDrawerProps) {
  return (
    <aside className="panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">详情</p>
          <h4>{title}</h4>
          {description ? <p className="body-muted">{description}</p> : null}
        </div>
      </div>
      {children}
    </aside>
  );
}
