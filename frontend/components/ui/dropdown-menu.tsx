'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';

interface DropdownMenuContextValue {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const DropdownMenuContext = React.createContext<DropdownMenuContextValue | undefined>(undefined);

function useDropdownMenuContext() {
  const context = React.useContext(DropdownMenuContext);
  if (!context) {
    throw new Error('DropdownMenu components must be used within a DropdownMenu');
  }
  return context;
}

interface DropdownMenuProps {
  children: React.ReactNode;
}

const DropdownMenu: React.FC<DropdownMenuProps> = ({ children }) => {
  const [open, setOpen] = React.useState(false);

  return (
    <DropdownMenuContext.Provider value={{ open, onOpenChange: setOpen }}>
      {children}
    </DropdownMenuContext.Provider>
  );
};

interface DropdownMenuTriggerProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  asChild?: boolean;
}

const DropdownMenuTrigger: React.FC<DropdownMenuTriggerProps> = ({
  children,
  asChild,
  ...props
}) => {
  const { onOpenChange } = useDropdownMenuContext();

  if (asChild && React.isValidElement(children)) {
    return React.cloneElement(children as React.ReactElement<{ onClick?: () => void }>, {
      onClick: () => onOpenChange(true),
    });
  }

  return (
    <button type="button" onClick={() => onOpenChange(true)} {...props}>
      {children}
    </button>
  );
};

const DropdownMenuPortal: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { open } = useDropdownMenuContext();
  if (!open || typeof window === 'undefined') return null;
  return <>{children}</>;
};

const DropdownMenuContent: React.FC<
  React.HTMLAttributes<HTMLDivElement> & { align?: 'start' | 'end'; forceMount?: boolean }
> = ({ className, align = 'end', forceMount, children, ...props }) => {
  const { open, onOpenChange } = useDropdownMenuContext();
  const contentRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (contentRef.current && !contentRef.current.contains(event.target as Node)) {
        onOpenChange(false);
      }
    };

    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onOpenChange(false);
      }
    };

    if (open) {
      document.addEventListener('mousedown', handleClickOutside);
      document.addEventListener('keydown', handleEscape);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, [open, onOpenChange]);

  if (!open && !forceMount) return null;

  return (
    <DropdownMenuPortal>
      <div
        ref={contentRef}
        className={cn(
          'z-50 min-w-[8rem] overflow-hidden rounded-md border bg-popover p-1 text-popover-foreground shadow-md data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2',
          align === 'end' && 'right-0',
          className
        )}
        onClick={() => onOpenChange(false)}
        {...props}
      >
        {children}
      </div>
    </DropdownMenuPortal>
  );
};

const DropdownMenuItem: React.FC<
  React.HTMLAttributes<HTMLDivElement> & { inset?: boolean }
> = ({ className, inset, children, onClick, ...props }) => {
  const handleClick = (e: React.MouseEvent<HTMLDivElement>) => {
    onClick?.(e);
    // Close dropdown after click
  };
  
  return (
    <div
      className={cn(
        'relative flex cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors focus:bg-accent focus:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50',
        inset && 'pl-8',
        className
      )}
      onClick={handleClick}
      {...props}
    >
      {children}
    </div>
  );
};

const DropdownMenuLabel: React.FC<
  React.HTMLAttributes<HTMLDivElement> & { inset?: boolean }
> = ({ className, inset, ...props }) => (
  <div
    className={cn(
      'px-2 py-1.5 text-sm font-semibold',
      inset && 'pl-8',
      className
    )}
    {...props}
  />
);

const DropdownMenuSeparator: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({
  className,
  ...props
}) => (
  <div
    className={cn('-mx-1 my-1 h-px bg-muted', className)}
    {...props}
  />
);

export {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
};
