// Mock admin service for demo
const mockUsers = [
  { id: 1, email: "john@example.com", full_name: "John Doe", role: "user", brand_id: null },
  { id: 2, email: "jane@example.com", full_name: "Jane Smith", role: "user", brand_id: null },
  { id: 3, email: "brand@ecommerce.com", full_name: "Brand Manager", role: "brand_user", brand_id: 1 },
  { id: 4, email: "admin@system.com", full_name: "System Admin", role: "admin", brand_id: null },
];

const getAllUsers = async () => {
  await new Promise(resolve => setTimeout(resolve, 300));
  return mockUsers;
};

const getAllBrands = async () => {
  // Reuse from brandService
  const { default: brandService } = await import('./brandService');
  return brandService.getBrands();
};

export default {
  getAllUsers,
  getAllBrands,
};