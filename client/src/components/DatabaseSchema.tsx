import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import type { TableSchema } from "@shared/schema";

interface DatabaseSchemaProps {
  schemaData: TableSchema[];
  isLoading: boolean;
}

export default function DatabaseSchema({ schemaData, isLoading }: DatabaseSchemaProps) {
  if (isLoading) {
    return (
      <Card data-testid="card-schema-loading">
        <CardHeader>
          <CardTitle>Структура БД</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <Skeleton className="h-20 w-full" />
            <Skeleton className="h-20 w-full" />
          </div>
        </CardContent>
      </Card>
    );
  }

  const formatRowCount = (count: number): string => {
    if (count >= 1000000) {
      return `${(count / 1000000).toFixed(1)}M rows`;
    } else if (count >= 1000) {
      return `${(count / 1000).toFixed(1)}K rows`;
    }
    return `${count} rows`;
  };

  const getColumnTypeColor = (type: string): string => {
    if (type.includes('longtext') || type.includes('text')) {
      return "text-amber-600";
    }
    if (type.includes('int')) {
      return "text-blue-600";
    }
    if (type.includes('varchar')) {
      return "text-green-600";
    }
    if (type.includes('datetime')) {
      return "text-purple-600";
    }
    return "text-muted-foreground";
  };

  return (
    <Card data-testid="card-database-schema">
      <CardHeader>
        <CardTitle>Структура БД</CardTitle>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-64">
          <div className="space-y-3">
            {schemaData?.map((table, index) => (
              <div key={index} className="border border-border rounded-lg p-3" data-testid={`table-${table.name}`}>
                <div className="flex items-center justify-between mb-2">
                  <div className="font-medium text-foreground">{table.name}</div>
                  <Badge variant="outline" data-testid={`row-count-${table.name}`}>
                    {formatRowCount(table.rowCount)}
                  </Badge>
                </div>
                <div className="space-y-1 text-sm">
                  {table.columns.slice(0, 5).map((column, colIndex) => (
                    <div key={colIndex} className="flex items-center justify-between" data-testid={`column-${table.name}-${column.name}`}>
                      <span className="font-mono">{column.name}</span>
                      <div className="flex items-center space-x-1">
                        <span className={getColumnTypeColor(column.type)}>
                          {column.type}
                        </span>
                        {column.indexed && (
                          <span className="text-muted-foreground">↗</span>
                        )}
                      </div>
                    </div>
                  ))}
                  {table.columns.length > 5 && (
                    <div className="text-xs text-muted-foreground" data-testid={`more-columns-${table.name}`}>
                      +{table.columns.length - 5} больше колонок
                    </div>
                  )}
                </div>
                {table.indexes.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-border">
                    <div className="text-xs text-muted-foreground mb-1">Индексы:</div>
                    <div className="flex flex-wrap gap-1">
                      {table.indexes.slice(0, 3).map((index, idxIndex) => (
                        <Badge key={idxIndex} variant="secondary" className="text-xs" data-testid={`index-${table.name}-${idxIndex}`}>
                          {index.columns.join(', ')}
                        </Badge>
                      ))}
                      {table.indexes.length > 3 && (
                        <Badge variant="outline" className="text-xs" data-testid={`more-indexes-${table.name}`}>
                          +{table.indexes.length - 3}
                        </Badge>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
