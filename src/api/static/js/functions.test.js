import { validatePassword_logic, validateRepeat_logic } from "./validation";

describe('Unit Test Category UI', () => {
    it('Validation for password is correct', async () => {
      expect(validatePassword_logic("fasdf")).toBe(1);
    });
    it('Validation for password repeat is correct', async () => {
      expect(validateRepeat_logic("test", "not")).toBe(false);
    });
    
  });
