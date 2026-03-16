export interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  imageUrl: string;
  tags: string[];
  is_featured?: boolean;
  categoryId?: string;
  stockQuantity?: number;
  isActive?: boolean;
  isLowStock?: boolean;
  categoryIds?: number[];
  categoryNames?: string[];
  imageUrls?: string[];
  images?: { url: string; is_primary: boolean }[];
  createdAt?: string;
}

export interface AdminProductCreate {
  name: string;
  description?: string;
  price: number;
  stock_quantity: number;
  is_active?: boolean;
  category_ids?: number[];
  image_urls?: string[];
}

export interface AdminProductUpdate {
  name?: string;
  description?: string;
  price?: number;
  stock_quantity?: number;
  is_active?: boolean;
  category_ids?: number[];
  images?: { url: string; is_primary: boolean }[];
}

export interface ProductListResponse {
  products: Product[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface AdminProductListParams {
  page?: number;
  limit?: number;
  search?: string;
  category_id?: number | null;
  sort?: 'created_desc' | 'created_asc';
}

export interface ProductSearchParams {
  query?: string;
  tag?: string;
  tags?: string[];
  categoryId?: number;
  page?: number;
  limit?: number;
}
