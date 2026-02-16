import { getRiskColor, getRiskLevel } from '../utils/helpers';

interface RiskScoreProps {
    score: number;
    size?: 'sm' | 'md' | 'lg';
}

export function RiskScore({ score, size = 'md' }: RiskScoreProps) {
    const sizeClasses = {
        sm: 'w-16 h-16 text-lg',
        md: 'w-24 h-24 text-2xl',
        lg: 'w-32 h-32 text-4xl',
    };

    const color = getRiskColor(score);
    const level = getRiskLevel(score);

    return (
        <div className="flex flex-col items-center gap-2">
            <div
                className={`${sizeClasses[size]} rounded-full border-4 flex items-center justify-center font-bold ${color}`}
                style={{ borderColor: 'currentColor' }}
            >
                {score.toFixed(1)}
            </div>
            <span className={`text-sm font-medium ${color}`}>{level} Risk</span>
        </div>
    );
}
