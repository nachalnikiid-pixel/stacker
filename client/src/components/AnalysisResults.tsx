import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { AlertTriangle, AlertCircle, Info, Gauge, SortAsc, Sparkles } from "lucide-react";
import type { AnalysisResult } from "@shared/schema";

interface AnalysisResultsProps {
  analysisData: AnalysisResult;
  isLoading: boolean;
}

export default function AnalysisResults({ analysisData, isLoading }: AnalysisResultsProps) {
  if (isLoading) {
    return (
      <Card data-testid="card-analysis-loading">
        <CardHeader>
          <CardTitle>Результаты анализа</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Skeleton className="h-8 w-full" />
          <Skeleton className="h-32 w-full" />
          <Skeleton className="h-24 w-full" />
        </CardContent>
      </Card>
    );
  }

  const getIssueIcon = (type: string) => {
    switch (type) {
      case "error":
        return <AlertTriangle className="text-red-500 mt-1" />;
      case "warning":
        return <AlertCircle className="text-amber-500 mt-1" />;
      case "info":
        return <Info className="text-blue-500 mt-1" />;
      default:
        return <Info className="text-gray-500 mt-1" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "Высокий приоритет":
        return "bg-red-100 text-red-800 border-red-200";
      case "Средний приоритет":
        return "bg-amber-100 text-amber-800 border-amber-200";
      case "Низкий приоритет":
        return "bg-blue-100 text-blue-800 border-blue-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  const getComplexityColor = (complexity: string) => {
    switch (complexity) {
      case "Высокая":
        return "text-red-600";
      case "Средняя":
        return "text-amber-600";
      case "Низкая":
        return "text-green-600";
      default:
        return "text-gray-600";
    }
  };

  const getTimeColor = (time: number) => {
    if (time > 10) return "text-red-600";
    if (time > 5) return "text-amber-600";
    return "text-green-600";
  };

  return (
    <Card data-testid="card-analysis-results">
      <CardHeader>
        <CardTitle>Результаты анализа</CardTitle>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="performance" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="performance" data-testid="tab-performance">
              <Gauge className="h-4 w-4 mr-1" />
              Производительность
            </TabsTrigger>
            <TabsTrigger value="indexes" data-testid="tab-indexes">
              <SortAsc className="h-4 w-4 mr-1" />
              Индексы
            </TabsTrigger>
            <TabsTrigger value="optimization" data-testid="tab-optimization">
              <Sparkles className="h-4 w-4 mr-1" />
              Оптимизация
            </TabsTrigger>
          </TabsList>

          <TabsContent value="performance" className="space-y-4" data-testid="content-performance">
            {/* Performance Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-muted p-4 rounded-lg" data-testid="metric-complexity">
                <div className="text-sm text-muted-foreground">Сложность запроса</div>
                <div className={`text-2xl font-bold ${getComplexityColor(analysisData.complexity)}`}>
                  {analysisData.complexity}
                </div>
                <div className="text-xs text-muted-foreground mt-1">
                  {analysisData.issues.filter(i => i.type === 'error').length > 0 
                    ? "Требует внимания" 
                    : "В пределах нормы"}
                </div>
              </div>
              <div className="bg-muted p-4 rounded-lg" data-testid="metric-execution-time">
                <div className="text-sm text-muted-foreground">Время выполнения</div>
                <div className={`text-2xl font-bold ${getTimeColor(analysisData.estimatedTime)}`}>
                  ~{analysisData.estimatedTime}s
                </div>
                <div className="text-xs text-muted-foreground mt-1">
                  {analysisData.estimatedTime > 10 ? "Требуется оптимизация" : "Приемлемо"}
                </div>
              </div>
              <div className="bg-muted p-4 rounded-lg" data-testid="metric-indexes">
                <div className="text-sm text-muted-foreground">Рекомендации</div>
                <div className="text-2xl font-bold text-blue-600">
                  {analysisData.indexRecommendations.length}
                </div>
                <div className="text-xs text-muted-foreground mt-1">
                  Предложений по индексам
                </div>
              </div>
            </div>

            {/* Issues List */}
            <div className="space-y-2">
              <h3 className="font-medium text-foreground">Обнаруженные проблемы</h3>
              <div className="space-y-2">
                {analysisData.issues.length === 0 ? (
                  <div className="text-sm text-muted-foreground" data-testid="text-no-issues">
                    Критических проблем не обнаружено
                  </div>
                ) : (
                  analysisData.issues.map((issue, index) => (
                    <div 
                      key={index}
                      className={`flex items-start space-x-3 p-3 border rounded-lg ${getPriorityColor(issue.severity)}`}
                      data-testid={`issue-${index}`}
                    >
                      {getIssueIcon(issue.type)}
                      <div>
                        <div className="font-medium">{issue.title}</div>
                        <div className="text-sm">{issue.description}</div>
                        {issue.line && (
                          <div className="text-xs mt-1">Строка: {issue.line}</div>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </TabsContent>

          <TabsContent value="indexes" className="space-y-4" data-testid="content-indexes">
            <h3 className="font-medium text-foreground">Рекомендуемые индексы</h3>
            <div className="space-y-3">
              {analysisData.indexRecommendations.length === 0 ? (
                <div className="text-sm text-muted-foreground" data-testid="text-no-indexes">
                  Дополнительные индексы не требуются
                </div>
              ) : (
                analysisData.indexRecommendations.map((rec, index) => (
                  <div key={index} className="border border-border rounded-lg p-4" data-testid={`index-recommendation-${index}`}>
                    <div className="flex items-center justify-between mb-2">
                      <div className="font-medium text-foreground">
                        {rec.type} для {rec.tableName}
                      </div>
                      <Badge variant="outline" className={getPriorityColor(rec.priority)}>
                        {rec.priority}
                      </Badge>
                    </div>
                    <div className="bg-muted p-3 rounded font-mono text-sm" data-testid={`ddl-${index}`}>
                      {rec.ddl}
                    </div>
                    <div className="text-sm text-muted-foreground mt-2">
                      {rec.impact}
                    </div>
                  </div>
                ))
              )}
            </div>
          </TabsContent>

          <TabsContent value="optimization" className="space-y-4" data-testid="content-optimization">
            <h3 className="font-medium text-foreground">Предложения по оптимизации</h3>
            <div className="space-y-3">
              {analysisData.optimizations.length === 0 ? (
                <div className="text-sm text-muted-foreground" data-testid="text-no-optimizations">
                  Дополнительные оптимизации не найдены
                </div>
              ) : (
                analysisData.optimizations.map((opt, index) => (
                  <div key={index} className="border border-border rounded-lg p-4" data-testid={`optimization-${index}`}>
                    <div className="font-medium text-foreground mb-2">{opt.title}</div>
                    <div className="text-sm text-muted-foreground mb-3">
                      {opt.description}
                    </div>
                    <div className="bg-muted p-3 rounded space-y-2">
                      <div>
                        <div className="text-xs text-muted-foreground mb-1">Было:</div>
                        <div className="font-mono text-sm" data-testid={`before-${index}`}>{opt.before}</div>
                      </div>
                      <div>
                        <div className="text-xs text-muted-foreground mb-1">Стало:</div>
                        <div className="font-mono text-sm" data-testid={`after-${index}`}>{opt.after}</div>
                      </div>
                    </div>
                    <div className="text-sm text-green-600 mt-2 font-medium">
                      {opt.impact}
                    </div>
                  </div>
                ))
              )}
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
