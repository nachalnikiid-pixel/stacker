import { randomUUID } from "crypto";
import type { 
  SqlQuery, 
  InsertSqlQuery,
  AnalysisResult,
  InsertAnalysisResult,
  OptimizedQuery,
  InsertOptimizedQuery,
  TableSchema
} from "@shared/schema";

export interface IStorage {
  // SQL Query methods
  createSqlQuery(query: InsertSqlQuery): Promise<SqlQuery>;
  getSqlQuery(id: string): Promise<SqlQuery | undefined>;
  getAllSqlQueries(): Promise<SqlQuery[]>;
  
  // Analysis Result methods
  createAnalysisResult(result: InsertAnalysisResult): Promise<AnalysisResult>;
  getAnalysisResult(id: string): Promise<AnalysisResult | undefined>;
  getAnalysisResultByQueryId(queryId: string): Promise<AnalysisResult | undefined>;
  
  // Optimized Query methods
  createOptimizedQuery(query: InsertOptimizedQuery): Promise<OptimizedQuery>;
  getOptimizedQuery(id: string): Promise<OptimizedQuery | undefined>;
  getOptimizedQueryByOriginalId(originalQueryId: string): Promise<OptimizedQuery | undefined>;
  
  // Database Schema methods
  getTableSchemas(): Promise<TableSchema[]>;
}

export class MemStorage implements IStorage {
  private sqlQueries: Map<string, SqlQuery> = new Map();
  private analysisResults: Map<string, AnalysisResult> = new Map();
  private optimizedQueries: Map<string, OptimizedQuery> = new Map();
  private tableSchemas: TableSchema[] = [
    {
      name: "item",
      rowCount: 27584857,
      columns: [
        { name: "transactionId", type: "int(15)", nullable: true, indexed: true, primary: false },
        { name: "source", type: "varchar(50)", nullable: true, indexed: true, primary: false },
        { name: "serial", type: "text", nullable: true, indexed: true, primary: false },
        { name: "member", type: "tinyint(4)", nullable: true, indexed: true, primary: false },
        { name: "login", type: "varchar(50)", nullable: true, indexed: true, primary: false },
        { name: "leader", type: "tinyint(4)", nullable: true, indexed: true, primary: false },
        { name: "itemSqlId", type: "int(11)", nullable: true, indexed: true, primary: false },
        { name: "itemId", type: "smallint(6)", nullable: true, indexed: true, primary: false },
        { name: "fraction", type: "tinyint(4)", nullable: true, indexed: true, primary: false },
        { name: "family", type: "smallint(6)", nullable: true, indexed: true, primary: false },
        { name: "DATE", type: "datetime", nullable: true, indexed: true, primary: false },
        { name: "comment", type: "varchar(50)", nullable: true, indexed: true, primary: false },
        { name: "args", type: "longtext", nullable: true, indexed: true, primary: false },
        { name: "amount", type: "varchar(15)", nullable: true, indexed: true, primary: false },
        { name: "accountid", type: "mediumint(9)", nullable: true, indexed: true, primary: false },
      ],
      indexes: [
        { name: "fraction", columns: ["fraction"], unique: false },
        { name: "itemSqlId", columns: ["itemSqlId"], unique: false },
        { name: "accountid", columns: ["accountid"], unique: false },
        { name: "itemId", columns: ["itemId"], unique: false },
        { name: "comment", columns: ["comment"], unique: false },
        { name: "amount", columns: ["amount"], unique: false },
        { name: "DATE", columns: ["DATE"], unique: false },
        { name: "member", columns: ["member"], unique: false },
        { name: "family", columns: ["family"], unique: false },
        { name: "leader", columns: ["leader"], unique: false },
        { name: "source", columns: ["source"], unique: false },
        { name: "transactionId", columns: ["transactionId"], unique: false },
        { name: "args", columns: ["args"], unique: false },
        { name: "login", columns: ["login"], unique: false },
        { name: "serial", columns: ["serial"], unique: false },
      ]
    },
    {
      name: "frac",
      rowCount: 82667,
      columns: [
        { name: "accountid", type: "mediumint(9)", nullable: true, indexed: true, primary: false },
        { name: "actionBy", type: "mediumint(9)", nullable: true, indexed: true, primary: false },
        { name: "TYPE", type: "varchar(50)", nullable: true, indexed: true, primary: false },
        { name: "fractionid", type: "int(2)", nullable: true, indexed: true, primary: false },
        { name: "reason", type: "varchar(70)", nullable: true, indexed: true, primary: false },
        { name: "args", type: "varchar(50)", nullable: true, indexed: true, primary: false },
        { name: "DATE", type: "datetime", nullable: true, indexed: true, primary: false },
      ],
      indexes: [
        { name: "accountid", columns: ["accountid"], unique: false },
        { name: "actionBy", columns: ["actionBy"], unique: false },
        { name: "TYPE", columns: ["TYPE"], unique: false },
        { name: "reason", columns: ["reason"], unique: false },
        { name: "DATE", columns: ["DATE"], unique: false },
        { name: "args", columns: ["args"], unique: false },
        { name: "fractionid", columns: ["fractionid"], unique: false },
      ]
    }
  ];

  // SQL Query methods
  async createSqlQuery(insertQuery: InsertSqlQuery): Promise<SqlQuery> {
    const id = randomUUID();
    const query: SqlQuery = {
      ...insertQuery,
      id,
      createdAt: new Date(),
    };
    this.sqlQueries.set(id, query);
    return query;
  }

  async getSqlQuery(id: string): Promise<SqlQuery | undefined> {
    return this.sqlQueries.get(id);
  }

  async getAllSqlQueries(): Promise<SqlQuery[]> {
    return Array.from(this.sqlQueries.values());
  }

  // Analysis Result methods
  async createAnalysisResult(insertResult: InsertAnalysisResult): Promise<AnalysisResult> {
    const id = randomUUID();
    const result: AnalysisResult = {
      ...insertResult,
      id,
      createdAt: new Date(),
    };
    this.analysisResults.set(id, result);
    return result;
  }

  async getAnalysisResult(id: string): Promise<AnalysisResult | undefined> {
    return this.analysisResults.get(id);
  }

  async getAnalysisResultByQueryId(queryId: string): Promise<AnalysisResult | undefined> {
    return Array.from(this.analysisResults.values()).find(result => result.queryId === queryId);
  }

  // Optimized Query methods
  async createOptimizedQuery(insertQuery: InsertOptimizedQuery): Promise<OptimizedQuery> {
    const id = randomUUID();
    const query: OptimizedQuery = {
      ...insertQuery,
      id,
      createdAt: new Date(),
    };
    this.optimizedQueries.set(id, query);
    return query;
  }

  async getOptimizedQuery(id: string): Promise<OptimizedQuery | undefined> {
    return this.optimizedQueries.get(id);
  }

  async getOptimizedQueryByOriginalId(originalQueryId: string): Promise<OptimizedQuery | undefined> {
    return Array.from(this.optimizedQueries.values()).find(query => query.originalQueryId === originalQueryId);
  }

  // Database Schema methods
  async getTableSchemas(): Promise<TableSchema[]> {
    return this.tableSchemas;
  }
}

export const storage = new MemStorage();
