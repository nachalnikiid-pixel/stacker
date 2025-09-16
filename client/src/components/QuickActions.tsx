import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useToast } from "@/hooks/use-toast";
import { apiRequest } from "@/lib/queryClient";
import { Sparkles, Download, BarChart3, FileText } from "lucide-react";

interface QuickActionsProps {
  queryId: string;
  hasAnalysis: boolean;
}

export default function QuickActions({ queryId, hasAnalysis }: QuickActionsProps) {
  const [procedureName, setProcedureName] = useState("");
  const [generatedProcedure, setGeneratedProcedure] = useState("");
  const [indexDDL, setIndexDDL] = useState("");
  const { toast } = useToast();

  const generateProcedureMutation = useMutation({
    mutationFn: async (name: string) => {
      const response = await apiRequest('POST', `/api/queries/${queryId}/procedure`, { name });
      return response.json();
    },
    onSuccess: (data) => {
      setGeneratedProcedure(data.procedure);
      toast({
        title: "Процедура создана",
        description: "Хранимая процедура успешно сгенерирована",
      });
    },
    onError: (error) => {
      toast({
        title: "Ошибка генерации",
        description: error instanceof Error ? error.message : "Не удалось создать процедуру",
        variant: "destructive",
      });
    },
  });

  const exportIndexesMutation = useMutation({
    mutationFn: async () => {
      const response = await apiRequest('GET', `/api/queries/${queryId}/indexes`);
      return response.json();
    },
    onSuccess: (data) => {
      setIndexDDL(data.ddl);
      toast({
        title: "DDL экспортирован",
        description: "Скрипты создания индексов готовы",
      });
    },
    onError: (error) => {
      toast({
        title: "Ошибка экспорта",
        description: error instanceof Error ? error.message : "Не удалось экспортировать индексы",
        variant: "destructive",
      });
    },
  });

  const handleGenerateProcedure = () => {
    if (!procedureName.trim()) {
      toast({
        title: "Укажите имя",
        description: "Введите имя для хранимой процедуры",
        variant: "destructive",
      });
      return;
    }
    generateProcedureMutation.mutate(procedureName);
  };

  const copyToClipboard = async (text: string, description: string) => {
    try {
      await navigator.clipboard.writeText(text);
      toast({
        title: "Скопировано",
        description,
      });
    } catch (error) {
      toast({
        title: "Ошибка копирования",
        description: "Не удалось скопировать в буфер обмена",
        variant: "destructive",
      });
    }
  };

  return (
    <Card data-testid="card-quick-actions">
      <CardHeader>
        <CardTitle>Быстрые действия</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        
        {/* Generate Stored Procedure */}
        <Dialog>
          <DialogTrigger asChild>
            <Button 
              variant="secondary" 
              className="w-full justify-start"
              disabled={!hasAnalysis}
              data-testid="button-generate-procedure"
            >
              <Sparkles className="h-4 w-4 mr-3" />
              <div className="text-left">
                <div className="font-medium">Генерировать хранимую процедуру</div>
                <div className="text-xs text-muted-foreground">С параметрами даты и фильтрации</div>
              </div>
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-4xl" data-testid="dialog-generate-procedure">
            <DialogHeader>
              <DialogTitle>Генерация хранимой процедуры</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="procedure-name">Имя процедуры</Label>
                <Input
                  id="procedure-name"
                  value={procedureName}
                  onChange={(e) => setProcedureName(e.target.value)}
                  placeholder="sp_optimized_query"
                  className="col-span-3"
                  data-testid="input-procedure-name"
                />
              </div>
              <div className="flex space-x-2">
                <Button 
                  onClick={handleGenerateProcedure}
                  disabled={generateProcedureMutation.isPending}
                  data-testid="button-create-procedure"
                >
                  {generateProcedureMutation.isPending ? "Генерирую..." : "Создать процедуру"}
                </Button>
                {generatedProcedure && (
                  <Button 
                    variant="outline" 
                    onClick={() => copyToClipboard(generatedProcedure, "Хранимая процедура скопирована")}
                    data-testid="button-copy-procedure"
                  >
                    Копировать
                  </Button>
                )}
              </div>
              {generatedProcedure && (
                <ScrollArea className="h-96 w-full border rounded-md" data-testid="scroll-procedure-content">
                  <div className="p-4 font-mono text-sm">
                    <pre className="whitespace-pre-wrap">{generatedProcedure}</pre>
                  </div>
                </ScrollArea>
              )}
            </div>
          </DialogContent>
        </Dialog>

        {/* Export Index DDL */}
        <Dialog>
          <DialogTrigger asChild>
            <Button 
              variant="secondary" 
              className="w-full justify-start"
              disabled={!hasAnalysis}
              onClick={() => exportIndexesMutation.mutate()}
              data-testid="button-export-indexes"
            >
              <Download className="h-4 w-4 mr-3" />
              <div className="text-left">
                <div className="font-medium">Экспорт DDL индексов</div>
                <div className="text-xs text-muted-foreground">Скрипт создания индексов</div>
              </div>
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-4xl" data-testid="dialog-export-indexes">
            <DialogHeader>
              <DialogTitle>DDL скрипты индексов</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              {indexDDL && (
                <>
                  <div className="flex justify-end">
                    <Button 
                      variant="outline" 
                      onClick={() => copyToClipboard(indexDDL, "DDL скрипты скопированы")}
                      data-testid="button-copy-ddl"
                    >
                      Копировать все
                    </Button>
                  </div>
                  <ScrollArea className="h-96 w-full border rounded-md" data-testid="scroll-ddl-content">
                    <div className="p-4 font-mono text-sm bg-muted">
                      <pre className="whitespace-pre-wrap">{indexDDL}</pre>
                    </div>
                  </ScrollArea>
                </>
              )}
              {exportIndexesMutation.isPending && (
                <div className="text-center py-8" data-testid="loading-export">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                  <div className="mt-2 text-sm text-muted-foreground">Экспортирую индексы...</div>
                </div>
              )}
            </div>
          </DialogContent>
        </Dialog>

        {/* Execution Plan */}
        <Button 
          variant="secondary" 
          className="w-full justify-start"
          disabled={!hasAnalysis}
          data-testid="button-execution-plan"
        >
          <BarChart3 className="h-4 w-4 mr-3" />
          <div className="text-left">
            <div className="font-medium">План выполнения</div>
            <div className="text-xs text-muted-foreground">EXPLAIN анализ</div>
          </div>
        </Button>

        {/* Generate Documentation */}
        <Button 
          variant="secondary" 
          className="w-full justify-start"
          disabled={!hasAnalysis}
          data-testid="button-generate-docs"
        >
          <FileText className="h-4 w-4 mr-3" />
          <div className="text-left">
            <div className="font-medium">Документация</div>
            <div className="text-xs text-muted-foreground">Отчет по оптимизации</div>
          </div>
        </Button>
      </CardContent>
    </Card>
  );
}
