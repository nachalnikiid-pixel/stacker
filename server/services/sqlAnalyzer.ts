import type { AnalysisResult } from "@shared/schema";

export class SqlAnalyzer {
  static analyzeQuery(query: string): Omit<AnalysisResult, "id" | "queryId" | "createdAt"> {
    const issues = this.detectIssues(query);
    const indexRecommendations = this.generateIndexRecommendations(query);
    const optimizations = this.generateOptimizations(query);
    const complexity = this.calculateComplexity(query);
    const estimatedTime = this.estimateExecutionTime(query, complexity);

    return {
      complexity,
      estimatedTime,
      issues,
      indexRecommendations,
      optimizations,
    };
  }

  private static detectIssues(query: string) {
    const issues = [];
    const upperQuery = query.toUpperCase();

    // Detect multiple LIKE operations
    const likeMatches = query.match(/LIKE\s+['"]/gi);
    if (likeMatches && likeMatches.length > 3) {
      issues.push({
        type: "error" as const,
        severity: "Высокий приоритет" as const,
        title: "Множественные LIKE операции",
        description: `Обнаружено ${likeMatches.length} LIKE операций. Использование OR с LIKE замедляет выполнение`,
        line: this.findLineNumber(query, "LIKE"),
      });
    }

    // Detect JSON operations in ARGS column
    if (query.includes("ARGS") && query.includes("LIKE") && query.includes("sp\":\"warehouse\"")) {
      issues.push({
        type: "info" as const,
        severity: "Средний приоритет" as const,
        title: "Возможность JSON оптимизации",
        description: "ARGS колонка содержит JSON - используйте JSON функции MySQL 5.7+",
      });
    }

    // Detect missing indexes for large tables
    if (query.includes("item") && !query.includes("INDEX")) {
      issues.push({
        type: "warning" as const,
        severity: "Высокий приоритет" as const,
        title: "Отсутствующий составной индекс",
        description: "Таблица item: (ARGS, itemId, login) - создайте составной индекс",
      });
    }

    // Detect correlated subqueries
    if (upperQuery.includes("SELECT") && upperQuery.includes("WHERE") && upperQuery.includes("IN (SELECT")) {
      issues.push({
        type: "warning" as const,
        severity: "Средний приоритет" as const,
        title: "Коррелированный подзапрос",
        description: "Подзапрос может быть заменен на JOIN для лучшей производительности",
      });
    }

    return issues;
  }

  private static generateIndexRecommendations(query: string) {
    const recommendations = [];

    // Recommend composite index for ARGS operations
    if (query.includes("ARGS") && query.includes("itemId")) {
      recommendations.push({
        tableName: "item",
        columns: ["ARGS", "itemId", "login"],
        type: "Составной индекс" as const,
        ddl: "CREATE INDEX idx_item_args_itemid_login ON item (ARGS(255), itemId, login);",
        impact: "Ускорит выполнение подзапроса на ~80%",
        priority: "Высокий приоритет" as const,
      });
    }

    // Recommend JSON functional index
    if (query.includes("ARGS") && query.includes("sp\":\"warehouse\"")) {
      recommendations.push({
        tableName: "item",
        columns: ["JSON_EXTRACT(ARGS, '$.sp')"],
        type: "Функциональный индекс" as const,
        ddl: "CREATE INDEX idx_item_json_sp ON item ((JSON_EXTRACT(ARGS, '$.sp')));",
        impact: "Функциональный индекс для JSON поля",
        priority: "Средний приоритет" as const,
      });
    }

    // Date range index
    if (query.includes("DATE") && query.includes("BETWEEN")) {
      recommendations.push({
        tableName: "item",
        columns: ["DATE"],
        type: "Обычный индекс" as const,
        ddl: "CREATE INDEX idx_item_date_range ON item (DATE);",
        impact: "Ускорит фильтрацию по датам",
        priority: "Средний приоритет" as const,
      });
    }

    return recommendations;
  }

  private static generateOptimizations(query: string) {
    const optimizations = [];

    // JSON optimization for LIKE operations
    if (query.includes("ARGS LIKE") && query.includes("sp\":\"warehouse\"")) {
      optimizations.push({
        title: "Замена LIKE на JSON функции",
        description: "Заменить множественные LIKE операции на JSON_EXTRACT для лучшей производительности",
        before: `sub_items.ARGS LIKE '%"sp":"warehouse","si":1,%'`,
        after: `JSON_EXTRACT(sub_items.ARGS, '$.sp') = 'warehouse' AND JSON_EXTRACT(sub_items.ARGS, '$.si') IN (1,2,3,4,5,6,7)`,
        impact: "Улучшение производительности на 60-80%",
      });
    }

    // REGEXP optimization for NOT LIKE
    if (query.includes("NOT LIKE '%PR %'") || query.includes("NOT LIKE '%pr %'")) {
      optimizations.push({
        title: "Замена NOT LIKE на REGEXP",
        description: "Использование REGEXP более эффективно для сложных паттернов",
        before: `((login NOT LIKE '%PR %') OR (login NOT LIKE '%pr %'))`,
        after: `login NOT REGEXP '^(PR |pr )'`,
        impact: "Упрощение логики и улучшение читаемости",
      });
    }

    // Subquery to JOIN optimization
    if (query.includes("IN (SELECT")) {
      optimizations.push({
        title: "Замена подзапроса на JOIN",
        description: "JOIN обычно работает быстрее коррелированных подзапросов",
        before: "WHERE column IN (SELECT ...)",
        after: "INNER JOIN (SELECT ...) AS subq ON table.column = subq.column",
        impact: "Улучшение производительности на 20-40%",
      });
    }

    return optimizations;
  }

  private static calculateComplexity(query: string): "Низкая" | "Средняя" | "Высокая" {
    let score = 0;
    const upperQuery = query.toUpperCase();

    // Count complexity factors
    if (upperQuery.includes("TEMPORARY TABLE")) score += 2;
    if (upperQuery.includes("LIKE")) score += 1;
    if ((upperQuery.match(/OR/g) || []).length > 5) score += 2;
    if (upperQuery.includes("COALESCE")) score += 1;
    if (upperQuery.includes("CASE")) score += 1;
    if ((upperQuery.match(/JOIN/g) || []).length > 2) score += 1;

    if (score >= 5) return "Высокая";
    if (score >= 3) return "Средняя";
    return "Низкая";
  }

  private static estimateExecutionTime(query: string, complexity: string): number {
    // Base time estimation based on complexity and operations
    let baseTime = 1.0;
    
    if (complexity === "Высокая") baseTime = 15.3;
    else if (complexity === "Средняя") baseTime = 5.2;
    else baseTime = 0.8;

    // Adjust for specific operations
    if (query.includes("item") && query.includes("27584857")) {
      baseTime *= 1.5; // Large table factor
    }

    return Math.round(baseTime * 10) / 10;
  }

  private static findLineNumber(query: string, searchTerm: string): number {
    const lines = query.split('\n');
    for (let i = 0; i < lines.length; i++) {
      if (lines[i].toUpperCase().includes(searchTerm.toUpperCase())) {
        return i + 1;
      }
    }
    return 1;
  }
}
