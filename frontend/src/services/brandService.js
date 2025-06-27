// Mock brand service for demo
const mockBrands = [
  { id: 1, name: "E-Commerce Inc.", support_email: "support@ecommerce.com", credit_balance: 2500 },
  { id: 2, name: "SaaS Platform", support_email: "help@saasplatform.com", credit_balance: 1800 },
  { id: 3, name: "Tech Corp", support_email: "support@techcorp.com", credit_balance: 3200 },
];

const getBrands = async () => {
  await new Promise(resolve => setTimeout(resolve, 300));
  return mockBrands;
};

const createBrand = async (brandData) => {
  await new Promise(resolve => setTimeout(resolve, 500));
  const newBrand = {
    ...brandData,
    id: mockBrands.length + 1,
    credit_balance: 0,
  };
  mockBrands.push(newBrand);
  return newBrand;
};

const updateBrand = async (brandId, brandData) => {
  await new Promise(resolve => setTimeout(resolve, 500));
  const brandIndex = mockBrands.findIndex(b => b.id === parseInt(brandId));
  if (brandIndex !== -1) {
    mockBrands[brandIndex] = { ...mockBrands[brandIndex], ...brandData };
    return mockBrands[brandIndex];
  }
  throw new Error('Brand not found');
};

export default {
  getBrands,
  createBrand,
  updateBrand,
};