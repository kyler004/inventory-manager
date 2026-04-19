import { useQuery } from "@tanstack/react-query";
import { reportsApi } from "@/api/reports.api";

export const useStockValuation = (params?: Record<string, unknown>) =>
  useQuery({
    queryKey: ["reports", "stock-valuation", params],
    queryFn: () => reportsApi.getStockValuation(params),
    // Reports are expensive so cache for 5 minutes
    staleTime: 1000 * 60 * 5,
  });

export const useShrinkage = (params?: Record<string, unknown>) => {
  useQuery({
    queryKey: ["reports", "shrinkage", params],
    queryFn: () => reportsApi.getShrinkage(params),
    staleTime: 1000 * 60 * 5,
  });
};

export const useTurnover = (params?: Record<string, unknown>) => {
  useQuery({
    queryKey: ["reports", "turnover", params],
    queryFn: () => reportsApi.getTurnover(params),
    staleTime: 1000 * 60 * 5,
  });
};

export const useDeadStock = (params?: Record<string, unknown>) => {
  useQuery({
    queryKey: ["reports", "dead-stock", params],
    queryFn: () => reportsApi.getDeadStock(params),
    staleTime: 1000 * 60 * 5,
  });
};
