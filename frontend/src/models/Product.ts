export interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  imageUrl: string;
  tags: string[];
}

export interface ProductListResponse {
  products: Product[];
  total: number;
  page: number;
  limit: number;
}

export interface ProductSearchParams {
  query?: string;
  tag?: string;
  page?: number;
  limit?: number;
}
