import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiRequest } from "@/lib/queryClient";
import SqlEditor from "../components/SqlEditor";
import AnalysisResults from "../components/AnalysisResults";
import DatabaseSchema from "../components/DatabaseSchema";
import OptimizedQuery from "../components/OptimizedQuery";
import QuickActions from "../components/QuickActions";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { Database, Settings, HelpCircle, Play, Upload } from "lucide-react";

export default function SqlOptimizer() {
  const [currentQuery, setCurrentQuery] = useState("");
  const [analysisData, setAnalysisData] = useState<any>(null);
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const { data: schemaData, isLoading: schemaLoading } = useQuery<any>({
    queryKey: ['/api/schema'],
  });

  const analyzeQueryMutation = useMutation({
    mutationFn: async (query: string) => {
      const response = await apiRequest('POST', '/api/queries/analyze', { query });
      return response.json();
    },
    onSuccess: (data) => {
      setAnalysisData(data);
      toast({
        title: "Анализ завершен",
        description: "SQL запрос успешно проанализирован",
      });
      queryClient.invalidateQueries({ queryKey: ['/api/queries'] });
    },
    onError: (error) => {
      toast({
        title: "Ошибка анализа",
        description: error instanceof Error ? error.message : "Не удалось проанализировать запрос",
        variant: "destructive",
      });
    },
  });

  const handleAnalyze = () => {
    if (!currentQuery.trim()) {
      toast({
        title: "Пустой запрос",
        description: "Введите SQL запрос для анализа",
        variant: "destructive",
      });
      return;
    }
    analyzeQueryMutation.mutate(currentQuery);
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result as string;
        setCurrentQuery(content);
      };
      reader.readAsText(file);
    }
  };

  return (
    <div className="h-full bg-background text-foreground font-sans">
      {/* Header */}
      <header className="border-b border-border bg-card" data-testid="header">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Database className="text-primary text-xl" />
                <h1 className="text-xl font-semibold text-foreground">SQL Optimizer Pro</h1>
              </div>
              <div className="text-sm text-muted-foreground hidden sm:block">
                Анализатор и оптимизатор SQL запросов
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Button variant="ghost" size="sm" data-testid="button-settings">
                <Settings className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="sm" data-testid="button-help">
                <HelpCircle className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Layout */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-7rem)]">
          
          {/* Left Panel - Input & Analysis */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* SQL Input Section */}
            <div className="bg-card border border-border rounded-lg shadow-sm">
              <div className="px-4 py-3 border-b border-border">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-medium text-foreground">SQL Запрос</h2>
                  <div className="flex items-center space-x-2">
                    <Button 
                      variant="secondary" 
                      size="sm"
                      onClick={() => document.getElementById('file-upload')?.click()}
                      data-testid="button-upload-file"
                    >
                      <Upload className="h-4 w-4 mr-1" />
                      Загрузить файл
                    </Button>
                    <input
                      id="file-upload"
                      type="file"
                      accept=".sql,.txt"
                      onChange={handleFileUpload}
                      className="hidden"
                      data-testid="input-file-upload"
                    />
                    <Button 
                      onClick={handleAnalyze}
                      disabled={analyzeQueryMutation.isPending}
                      data-testid="button-analyze-query"
                    >
                      <Play className="h-4 w-4 mr-1" />
                      {analyzeQueryMutation.isPending ? "Анализирую..." : "Анализировать"}
                    </Button>
                  </div>
                </div>
              </div>
              <div className="p-4">
                <SqlEditor
                  value={currentQuery}
                  onChange={setCurrentQuery}
                  placeholder="Вставьте ваш SQL запрос здесь..."
                />
              </div>
            </div>

            {/* Analysis Results */}
            {analysisData && (
              <AnalysisResults 
                analysisData={analysisData.analysis}
                isLoading={analyzeQueryMutation.isPending}
              />
            )}
          </div>

          {/* Right Panel - Database Schema & Optimized Query */}
          <div className="space-y-6">
            
            {/* Database Schema Visualization */}
            <DatabaseSchema 
              schemaData={schemaData || []}
              isLoading={schemaLoading}
            />

            {/* Optimized Query Preview */}
            {analysisData?.optimizedQuery && (
              <OptimizedQuery 
                optimizedQuery={analysisData.optimizedQuery}
                originalQueryId={analysisData.query.id}
              />
            )}

            {/* Quick Actions */}
            {analysisData && (
              <QuickActions
                queryId={analysisData.query.id}
                hasAnalysis={!!analysisData.analysis}
              />
            )}
          </div>
        </div>
      </div>

      {/* Status Bar */}
      <footer className="border-t border-border bg-card" data-testid="footer-status">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-10 text-sm text-muted-foreground">
            <div data-testid="text-database-info">
              MySQL 8.0 | {analysisData ? "Анализ завершен" : "Ожидание запроса"}
            </div>
            <div className="flex items-center space-x-4">
              <span data-testid="text-tables-processed">
                Обработано таблиц: {Array.isArray(schemaData) ? schemaData.length : 0}
              </span>
              <span data-testid="text-issues-found">
                Найдено проблем: {analysisData?.analysis?.issues?.length || 0}
              </span>
              <span data-testid="text-optimizations-suggested">
                Предложено оптимизаций: {analysisData?.analysis?.optimizations?.length || 0}
              </span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
