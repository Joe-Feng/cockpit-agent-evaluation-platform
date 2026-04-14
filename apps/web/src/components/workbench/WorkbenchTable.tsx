import type { ReactNode } from "react";

type Column<Row extends { id: string }> = {
  key: keyof Row;
  label: string;
  sticky?: boolean;
  render?: (row: Row) => ReactNode;
};

type WorkbenchTableProps<Row extends { id: string }> = {
  ariaLabel: string;
  columns: Array<Column<Row>>;
  rows: Row[];
};

export function WorkbenchTable<Row extends { id: string }>({
  ariaLabel,
  columns,
  rows,
}: WorkbenchTableProps<Row>) {
  return (
    <div className="panel">
      <table aria-label={ariaLabel} className="workbench-table">
        <thead>
          <tr>
            {columns.map((column) => (
              <th
                className={column.sticky ? "workbench-table__sticky" : undefined}
                key={String(column.key)}
                scope="col"
              >
                {column.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.id}>
              {columns.map((column) => (
                <td
                  className={column.sticky ? "workbench-table__sticky" : undefined}
                  key={String(column.key)}
                >
                  {column.render ? column.render(row) : String(row[column.key] ?? "")}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
