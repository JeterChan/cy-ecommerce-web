export interface Category {
  id: string;
  name: string;
  parentId?: string; // Optional for root categories
  slug: string;
}
