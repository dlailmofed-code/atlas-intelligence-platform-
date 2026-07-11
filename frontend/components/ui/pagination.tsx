import * as React from 'react';
import { cn } from '@/lib/utils';
import { Button } from './button';
import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react';

interface PaginationProps extends React.HTMLAttributes<HTMLDivElement> {
  page: number;
  pageSize: number;
  total: number;
  onPageChange: (page: number) => void;
}

const Pagination: React.FC<PaginationProps> = ({
  page,
  pageSize,
  total,
  onPageChange,
  className,
  ...props
}) => {
  const totalPages = Math.ceil(total / pageSize);
  const startItem = (page - 1) * pageSize + 1;
  const endItem = Math.min(page * pageSize, total);

  const getPageNumbers = () => {
    const pages: (number | 'ellipsis')[] = [];
    const showPages = 5;
    
    if (totalPages <= showPages) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      if (page <= 3) {
        for (let i = 1; i <= 4; i++) {
          pages.push(i);
        }
        pages.push('ellipsis');
        pages.push(totalPages);
      } else if (page >= totalPages - 2) {
        pages.push(1);
        pages.push('ellipsis');
        for (let i = totalPages - 3; i <= totalPages; i++) {
          pages.push(i);
        }
      } else {
        pages.push(1);
        pages.push('ellipsis');
        pages.push(page - 1);
        pages.push(page);
        pages.push(page + 1);
        pages.push('ellipsis');
        pages.push(totalPages);
      }
    }
    
    return pages;
  };

  if (totalPages <= 1) return null;

  return (
    <div
      className={cn('flex flex-col items-center gap-4 sm:flex-row sm:justify-between', className)}
      {...props}
    >
      <div className="text-sm text-muted-foreground">
        Showing <span className="font-medium">{startItem}</span> to{' '}
        <span className="font-medium">{endItem}</span> of{' '}
        <span className="font-medium">{total}</span> results
      </div>
      
      <div className="flex items-center gap-1">
        <Button
          variant="outline"
          size="icon"
          onClick={() => onPageChange(1)}
          disabled={page === 1}
          aria-label="First page"
        >
          <ChevronsLeft className="h-4 w-4" />
        </Button>
        <Button
          variant="outline"
          size="icon"
          onClick={() => onPageChange(page - 1)}
          disabled={page === 1}
          aria-label="Previous page"
        >
          <ChevronLeft className="h-4 w-4" />
        </Button>
        
        <div className="flex items-center gap-1 px-2">
          {getPageNumbers().map((pageNum, index) =>
            pageNum === 'ellipsis' ? (
              <span
                key={`ellipsis-${index}`}
                className="flex h-10 w-10 items-center justify-center text-muted-foreground"
              >
                ...
              </span>
            ) : (
              <Button
                key={pageNum}
                variant={page === pageNum ? 'default' : 'outline'}
                size="icon"
                onClick={() => onPageChange(pageNum)}
                aria-label={`Page ${pageNum}`}
                aria-current={page === pageNum ? 'page' : undefined}
              >
                {pageNum}
              </Button>
            )
          )}
        </div>
        
        <Button
          variant="outline"
          size="icon"
          onClick={() => onPageChange(page + 1)}
          disabled={page === totalPages}
          aria-label="Next page"
        >
          <ChevronRight className="h-4 w-4" />
        </Button>
        <Button
          variant="outline"
          size="icon"
          onClick={() => onPageChange(totalPages)}
          disabled={page === totalPages}
          aria-label="Last page"
        >
          <ChevronsRight className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
};

export { Pagination };
