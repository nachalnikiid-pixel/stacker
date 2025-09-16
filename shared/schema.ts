import { z } from "zod";

// SQL Query Analysis Schema
export const sqlQuerySchema = z.object({
  id: z.string().optional(),
  query: z.string().min(1, "SQL запрос не может быть пустым"),
  name: z.string().optional(),
  createdAt: z.date().optional(),
});

export const analysisResultSchema = z.object({
  id: z.string(),
  queryId: z.string(),
  complexity: z.enum(["Низкая", "Средняя", "Высокая"]),
  estimatedTime: z.number(),
  issues: z.array(z.object({
    type: z.enum(["error", "warning", "info"]),
    severity: z.enum(["Высокий приоритет", "Средний приоритет", "Низкий приоритет"]),
    title: z.string(),
    description: z.string(),
    line: z.number().optional(),
  })),
  indexRecommendations: z.array(z.object({
    tableName: z.string(),
    columns: z.array(z.string()),
    type: z.enum(["Составной индекс", "Функциональный индекс", "Обычный индекс"]),
    ddl: z.string(),
    impact: z.string(),
    priority: z.enum(["Высокий приоритет", "Средний приоритет", "Низкий приоритет"]),
  })),
  optimizations: z.array(z.object({
    title: z.string(),
    description: z.string(),
    before: z.string(),
    after: z.string(),
    impact: z.string(),
  })),
  createdAt: z.date().optional(),
});

export const optimizedQuerySchema = z.object({
  id: z.string(),
  originalQueryId: z.string(),
  optimizedQuery: z.string(),
  improvements: z.object({
    performanceGain: z.number(),
    originalTime: z.number(),
    optimizedTime: z.number(),
  }),
  createdAt: z.date().optional(),
});

export const tableSchemaSchema = z.object({
  name: z.string(),
  rowCount: z.number(),
  columns: z.array(z.object({
    name: z.string(),
    type: z.string(),
    nullable: z.boolean(),
    indexed: z.boolean(),
    primary: z.boolean(),
  })),
  indexes: z.array(z.object({
    name: z.string(),
    columns: z.array(z.string()),
    unique: z.boolean(),
  })),
});

export const storedProcedureSchema = z.object({
  name: z.string(),
  parameters: z.array(z.object({
    name: z.string(),
    type: z.string(),
    defaultValue: z.string().optional(),
  })),
  body: z.string(),
});

// Insert schemas
export const insertSqlQuerySchema = sqlQuerySchema.omit({ id: true, createdAt: true });
export const insertAnalysisResultSchema = analysisResultSchema.omit({ id: true, createdAt: true });
export const insertOptimizedQuerySchema = optimizedQuerySchema.omit({ id: true, createdAt: true });

// Types
export type SqlQuery = z.infer<typeof sqlQuerySchema>;
export type InsertSqlQuery = z.infer<typeof insertSqlQuerySchema>;
export type AnalysisResult = z.infer<typeof analysisResultSchema>;
export type InsertAnalysisResult = z.infer<typeof insertAnalysisResultSchema>;
export type OptimizedQuery = z.infer<typeof optimizedQuerySchema>;
export type InsertOptimizedQuery = z.infer<typeof insertOptimizedQuerySchema>;
export type TableSchema = z.infer<typeof tableSchemaSchema>;
export type StoredProcedure = z.infer<typeof storedProcedureSchema>;
