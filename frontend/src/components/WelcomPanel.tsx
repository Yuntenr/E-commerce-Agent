import {
    ScanSearch,
    PartyPopper,
    Search,
    LineChart,
    ShoppingBag
} from "lucide-react";

type WelcomePanelProps = {
    examples: string[];
    onUseExample: (example: string) => void;
};

const highlights = [
    { label: "智能问答", icon: Search },
    { label: "自然语言查询数据", icon: LineChart },
    { label: "电商业务智能 Agent", icon: ShoppingBag },
];

export default function WelcomePanel({ examples, onUseExample}: WelcomePanelProps) {
    return (
        <div className="mx-auto flex min-h-full max-w-5xl flex-col justify-center px-4 py-12">
            <div className="mb-10 flex justify-center">
                <div className="mb-5 inline-flex items-center gap-2 border border-moss/25 bg-moss/10 px-3 py-1.5 text-sm font-semibold text-emerald-500">
                    <PartyPopper className="h-4 w-4" aria-hidden="true" />E-commerce-Agent
                </div>
            </div>

            <div className="grid gap-3 sm:grid-cols-3">
                {highlights.map((item) => {
                    const Icon = item.icon;
                    return (
                        <div key={item.label} className=" boader border-ink/10 bg-white/55 px-4 py-4">
                            <Icon className="mb-5 h-5 w-5 text-brass" aria-hidden="true" />
                            <div className="text-sm font-semibold text-ink">{item.label}</div>
                        </div>
                    )
                })}
            </div>

            <div className="mt-6 grid gap-3 md:grid-cols-2">
                {examples.map((example) => (
                    <button
                     key={example}
                     type="button"
                     onClick={() => onUseExample(example)}
                     className="min-h-20 border border-ink/10 bg-[#fffaf1]/75 px-4 py-4 text-left text-[15px] leading-6 text-ink transition hover:-translate-y-0.5 hover:border-moss/35 hover:bg-white focus:outline-none focus:ring-2 focus:ring-moss/35">
                        {example}
                     </button>
                ))}
            </div>


        </div>
    )
}