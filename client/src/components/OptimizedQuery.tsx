import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Copy, CheckCircle } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import type { OptimizedQuery } from "@shared/schema";

interface OptimizedQueryProps {
  optimizedQuery: OptimizedQuery;
  originalQueryId: string;
}

export default function OptimizedQuery({ optimizedQuery }: OptimizedQueryProps) {
  const [copied, setCopied] = useState(false);
  const { toast } = useToast();

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(optimizedQuery.optimizedQuery);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
      toast({
        title: "Скопировано",
        description: "Оптимизированный запрос скопирован в буфер обмена",
      });
    } catch (error) {
      toast({
        title: "Ошибка копирования",
        description: "Не удалось скопировать запрос",
        variant: "destructive",
      });
    }
  };

  return (
    <Card data-testid="card-optimized-query">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Оптимизированный запрос</CardTitle>
          <Button 
            variant="outline" 
            size="sm"
            onClick={handleCopy}
            data-testid="button-copy-query"
          >
            {copied ? <CheckCircle className="h-4 w-4 mr-1" /> : <Copy className="h-4 w-4 mr-1" />}
            {copied ? "Скопировано" : "Копировать"}
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <ScrollArea className="max-h-96">
          <div className="bg-muted p-3 rounded-lg font-mono text-sm overflow-x-auto" data-testid="optimized-query-text">
            <div className="text-green-600 mb-2">-- Оптимизированная версия с улучшениями</div>
            <pre className="whitespace-pre-wrap">{optimizedQuery.optimizedQuery}</pre>
          </div>
        </ScrollArea>
        
        <div className="mt-3 p-3 bg-green-50 dark:bg-green-950 border border-green-200 dark:border-green-800 rounded-lg" data-testid="improvement-summary">
          <div className="flex items-center space-x-2">
            <CheckCircle className="text-green-600" />
            <div className="text-sm">
              <div className="font-medium text-green-800 dark:text-green-200" data-testid="performance-gain">
                Ожидаемое улучшение производительности: {optimizedQuery.improvements.performanceGain}%
              </div>
              <div className="text-green-600" data-testid="execution-time-comparison">
                Время выполнения: ~{optimizedQuery.improvements.optimizedTime}s 
                (было ~{optimizedQuery.improvements.originalTime}s)
              </div>
            </div>
          </div>
        </div>

        {/* Performance Metrics */}
        <div className="mt-3 grid grid-cols-3 gap-2">
          <div className="text-center p-2 bg-muted rounded" data-testid="metric-original-time">
            <div className="text-xs text-muted-foreground">Было</div>
            <div className="font-bold text-red-600">{optimizedQuery.improvements.originalTime}s</div>
          </div>
          <div className="text-center p-2 bg-muted rounded" data-testid="metric-optimized-time">
            <div className="text-xs text-muted-foreground">Стало</div>
            <div className="font-bold text-green-600">{optimizedQuery.improvements.optimizedTime}s</div>
          </div>
          <div className="text-center p-2 bg-muted rounded" data-testid="metric-improvement">
            <div className="text-xs text-muted-foreground">Улучшение</div>
            <div className="font-bold text-blue-600">{optimizedQuery.improvements.performanceGain}%</div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
