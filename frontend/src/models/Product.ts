export interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  imageUrl: string;
  tags: string[];
  is_featured?: boolean;
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
  tags?: string[];
  page?: number;
  limit?: number;
}
