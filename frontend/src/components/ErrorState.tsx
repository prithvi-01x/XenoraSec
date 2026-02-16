import { AlertCircle } from 'lucide-react';

interface ErrorStateProps {
    message: string;
    onRetry?: () => void;
}

export function ErrorState({ message, onRetry }: ErrorStateProps) {
    return (
        <div className="flex flex-col items-center justify-center py-12">
            <AlertCircle className="w-12 h-12 text-danger mb-4" />
            <p className="text-gray-300 mb-4">{message}</p>
            {onRetry && (
                <button onClick={onRetry} className="btn btn-primary">
                    Retry
                </button>
            )}
        </div>
    );
}
