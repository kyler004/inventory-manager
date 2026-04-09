import client from "./client";
import type { Product } from "@/types/product.types";
import type { PaginatedResponse, ApiResponse } from "@/types/api.types";
// import { partial } from 'node_modules/zod/v4/core/util.d.cts';

export const productsApi = {
  getProducts: async (params?: Record<string, unknown>) => {
    const response = await client.get<PaginatedResponse<Product>>(
      "/products/",
      { params },
    );
    return response.data;
  },

  getProduct: async (id: number) => {
    const response = await client.get<ApiResponse<Product>>(`/products/${id}/`);
    return response.data.data;
  },

  createProduct: async (data: Partial<Product>) => {
    const response = await client.post<ApiResponse<Product>>(
      "/products/",
      data,
    );

    return response.data.data;
  },

  updateProduct: async (id: number, data: Partial<Product>) => {
    const response = await client.patch<ApiResponse<Product>>(
      `/products/${id}/`,
      data,
    );
    return response.data.data;
  },

  deleteProduct: async (id: number) => {
    await client.delete(`/products/${id}/`);
  },

  getCategories: async () => {
    const response = await client.get(`/products/categories`);
    return response.data;
  },

  exportProducts: async () => {
    const response = await client.get("/products/export", {
      responseType: "blob", // For file downloads
    });
    return response.data;
  },
};
