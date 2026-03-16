import { z } from 'zod';

export const ForgotPasswordSchema = z.object({
  email: z.string().min(1, 'emailRequired').email('emailInvalid'),
});

export type ForgotPasswordFormValues = z.infer<typeof ForgotPasswordSchema>;

export const ResetPasswordSchema = z.object({
  password: z
    .string()
    .min(8, 'passwordMinLength')
    .regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^a-zA-Z\d\s]).{8,}$/, 'passwordStrength'),
  confirmPassword: z.string().min(1, 'required'),
}).refine((data) => data.password === data.confirmPassword, {
  message: 'passwordMismatch',
  path: ['confirmPassword'],
});

export type ResetPasswordFormValues = z.infer<typeof ResetPasswordSchema>;

export const ProfileUpdateSchema = z.object({
  username: z.string().min(3, 'usernameMinLength').max(50, 'usernameMaxLength'),
  phone: z.string().regex(/^09\d{8}$/, 'phoneInvalid').optional().or(z.literal('')),
  address: z.string().optional().or(z.literal('')),
  carrier_type: z.string().optional().or(z.literal('')),
  carrier_number: z.string().optional().or(z.literal('')),
  tax_id: z.string().regex(/^\d{8}$/, 'taxIdInvalid').optional().or(z.literal('')),
});

export type ProfileUpdateFormValues = z.infer<typeof ProfileUpdateSchema>;

export const ChangePasswordSchema = z.object({
  old_password: z.string().min(1, 'passwordRequired'),
  new_password: z
    .string()
    .min(8, 'passwordMinLength')
    .regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^a-zA-Z\d\s]).{8,}$/, 'passwordStrength'),
  confirm_password: z.string().min(1, 'required'),
}).refine((data) => data.new_password === data.confirm_password, {
  message: 'passwordMismatch',
  path: ['confirm_password'],
});

export type ChangePasswordFormValues = z.infer<typeof ChangePasswordSchema>;
