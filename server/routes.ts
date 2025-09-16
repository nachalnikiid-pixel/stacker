import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { SqlAnalyzer } from "./services/sqlAnalyzer";
import { QueryOptimizer } from "./services/queryOptimizer";
import { IndexOptimizer } from "./services/indexOptimizer";
import { insertSqlQuerySchema, insertAnalysisResultSchema, insertOptimizedQuerySchema } from "@shared/schema";

export async function registerRoutes(app: Express): Promise<Server> {
  
  // Analyze SQL Query
  app.post("/api/queries/analyze", async (req, res) => {
    try {
      const { query } = insertSqlQuerySchema.parse(req.body);
      
      // Create and store the query
      const sqlQuery = await storage.createSqlQuery({ query });
      
      // Analyze the query
      const analysisData = SqlAnalyzer.analyzeQuery(query);
      const analysisResult = await storage.createAnalysisResult({
        ...analysisData,
        queryId: sqlQuery.id!,
      });
      
      // Generate optimized query
      const optimization = QueryOptimizer.optimizeQuery(query);
      const optimizedQuery = await storage.createOptimizedQuery({
        originalQueryId: sqlQuery.id!,
        optimizedQuery: optimization.optimizedQuery,
        improvements: optimization.improvements,
      });
      
      res.json({
        query: sqlQuery,
        analysis: analysisResult,
        optimizedQuery,
      });
    } catch (error) {
      console.error("Error analyzing query:", error);
      res.status(400).json({ 
        message: error instanceof Error ? error.message : "Failed to analyze query" 
      });
    }
  });
  
  // Get query analysis
  app.get("/api/queries/:id/analysis", async (req, res) => {
    try {
      const { id } = req.params;
      const query = await storage.getSqlQuery(id);
      
      if (!query) {
        return res.status(404).json({ message: "Query not found" });
      }
      
      const analysis = await storage.getAnalysisResultByQueryId(id);
      const optimizedQuery = await storage.getOptimizedQueryByOriginalId(id);
      
      res.json({
        query,
        analysis,
        optimizedQuery,
      });
    } catch (error) {
      console.error("Error getting analysis:", error);
      res.status(500).json({ message: "Failed to get analysis" });
    }
  });
  
  // Get database schema
  app.get("/api/schema", async (req, res) => {
    try {
      const schemas = await storage.getTableSchemas();
      res.json(schemas);
    } catch (error) {
      console.error("Error getting schema:", error);
      res.status(500).json({ message: "Failed to get database schema" });
    }
  });
  
  // Generate stored procedure
  app.post("/api/queries/:id/procedure", async (req, res) => {
    try {
      const { id } = req.params;
      const { name } = req.body;
      
      if (!name) {
        return res.status(400).json({ message: "Procedure name is required" });
      }
      
      const optimizedQuery = await storage.getOptimizedQueryByOriginalId(id);
      if (!optimizedQuery) {
        return res.status(404).json({ message: "Optimized query not found" });
      }
      
      const procedure = QueryOptimizer.generateStoredProcedure(
        optimizedQuery.optimizedQuery,
        name
      );
      
      res.json({ procedure });
    } catch (error) {
      console.error("Error generating procedure:", error);
      res.status(500).json({ message: "Failed to generate stored procedure" });
    }
  });
  
  // Export index DDL
  app.get("/api/queries/:id/indexes", async (req, res) => {
    try {
      const { id } = req.params;
      const analysis = await storage.getAnalysisResultByQueryId(id);
      
      if (!analysis) {
        return res.status(404).json({ message: "Analysis not found" });
      }
      
      const ddlStatements = analysis.indexRecommendations.map(rec => rec.ddl);
      
      res.json({
        ddl: ddlStatements.join('\n\n'),
        recommendations: analysis.indexRecommendations,
      });
    } catch (error) {
      console.error("Error getting indexes:", error);
      res.status(500).json({ message: "Failed to get index recommendations" });
    }
  });
  
  // Get all queries
  app.get("/api/queries", async (req, res) => {
    try {
      const queries = await storage.getAllSqlQueries();
      res.json(queries);
    } catch (error) {
      console.error("Error getting queries:", error);
      res.status(500).json({ message: "Failed to get queries" });
    }
  });

  const httpServer = createServer(app);
  return httpServer;
}
