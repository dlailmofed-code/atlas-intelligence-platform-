import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';
import { AlertCircle, CheckCircle2, Info, XCircle } from 'lucide-react';

const alertVariants = cva(
  'relative w-full rounded-lg border p-4 [&>svg+div]:translate-y-[-3px] [&>svg]:absolute [&>svg]:left-4 [&>svg]:top-4 [&>svg]:text-foreground [&>svg~*]:pl-7',
  {
    variants: {
      variant: {
        default: 'bg-background text-foreground',
        success: 'border-green-500/50 bg-green-50 text-green-900 dark:bg-green-900/20 dark:text-green-300',
        warning: 'border-yellow-500/50 bg-yellow-50 text-yellow-900 dark:bg-yellow-900/20 dark:text-yellow-300',
        destructive: 'border-destructive/50 bg-destructive/10 text-destructive dark:bg-destructive/20',
        info: 'border-blue-500/50 bg-blue-50 text-blue-900 dark:bg-blue-900/20 dark:text-blue-300',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
);

const icons = {
  default: Info,
  success: CheckCircle2,
  warning: AlertCircle,
  destructive: XCircle,
  info: Info,
};

interface AlertProps extends React.HTMLAttributes<HTMLDivElement>, VariantProps<typeof alertVariants> {
  title?: string;
  description?: string;
}

const Alert = React.forwardRef<HTMLDivElement, AlertProps>(
  ({ className, variant, title, description, children, ...props }, ref) => {
    const Icon = icons[variant || 'default'];
    
    return (
      <div
        ref={ref}
        role="alert"
        className={cn(alertVariants({ variant }), className)}
        {...props}
      >
        <Icon className="h-4 w-4" />
        {title && <h5 className="mb-1 font-medium leading-none tracking-tight">{title}</h5>}
        {description && <div className="text-sm [&_p]:leading-relaxed">{description}</div>}
        {children}
      </div>
    );
  }
);
Alert.displayName = 'Alert';

const AlertDescription = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn('text-sm [&_p]:leading-relaxed', className)} {...props} />
  )
);
AlertDescription.displayName = 'AlertDescription';

export { Alert, AlertDescription, alertVariants };
