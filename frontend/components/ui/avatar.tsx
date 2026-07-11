import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn, getInitials, generateColor } from '@/lib/utils';

const avatarVariants = cva(
  'relative flex shrink-0 overflow-hidden rounded-full',
  {
    variants: {
      size: {
        sm: 'h-8 w-8 text-xs',
        md: 'h-10 w-10 text-sm',
        lg: 'h-12 w-12 text-base',
        xl: 'h-16 w-16 text-lg',
      },
    },
    defaultVariants: {
      size: 'md',
    },
  }
);

interface AvatarProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof avatarVariants> {
  src?: string;
  alt?: string;
  name?: string;
}

const Avatar = React.forwardRef<HTMLDivElement, AvatarProps>(
  ({ className, size, src, alt, name, ...props }, ref) => {
    const [imageError, setImageError] = React.useState(false);
    
    const showFallback = !src || imageError;
    const initials = name ? getInitials(name) : '?';
    const bgColor = name ? generateColor(name) : 'bg-gray-400';
    
    return (
      <div
        ref={ref}
        className={cn(avatarVariants({ size }), className)}
        {...props}
      >
        {showFallback ? (
          <div
            className={cn(
              'flex h-full w-full items-center justify-center font-medium text-white',
              bgColor
            )}
          >
            {initials}
          </div>
        ) : (
          <img
            src={src}
            alt={alt || name || 'Avatar'}
            className="aspect-square h-full w-full object-cover"
            onError={() => setImageError(true)}
          />
        )}
      </div>
    );
  }
);
Avatar.displayName = 'Avatar';

const AvatarSmall = React.forwardRef<HTMLDivElement, AvatarProps>(
  ({ className, src, alt, name, ...props }, ref) => (
    <Avatar
      ref={ref}
      size="sm"
      src={src}
      alt={alt}
      name={name}
      className={className}
      {...props}
    />
  )
);
AvatarSmall.displayName = 'AvatarSmall';

const AvatarLarge = React.forwardRef<HTMLDivElement, AvatarProps>(
  ({ className, src, alt, name, ...props }, ref) => (
    <Avatar
      ref={ref}
      size="lg"
      src={src}
      alt={alt}
      name={name}
      className={className}
      {...props}
    />
  )
);
AvatarLarge.displayName = 'AvatarLarge';

const AvatarFallback = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, children, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        'flex h-full w-full items-center justify-center rounded-full bg-muted font-medium text-muted-foreground',
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
);
AvatarFallback.displayName = 'AvatarFallback';

export { Avatar, AvatarSmall, AvatarLarge, AvatarFallback, avatarVariants };
