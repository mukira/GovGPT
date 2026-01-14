import ReactMarkdown from 'react-markdown'

interface FormattedResponseProps {
    content: string
}

export function FormattedResponse({ content }: FormattedResponseProps) {
    return (
        <div className="formatted-response">
            <ReactMarkdown
                components={{
                    // Headings
                    h1: ({ children }) => (
                        <h1 className="text-xl font-bold text-emerald-400 mt-4 mb-3 pb-2 border-b border-emerald-500/30">
                            {children}
                        </h1>
                    ),
                    h2: ({ children }) => (
                        <h2 className="text-lg font-semibold text-emerald-300 mt-3 mb-2">
                            {children}
                        </h2>
                    ),
                    h3: ({ children }) => (
                        <h3 className="text-base font-semibold text-gray-200 mt-3 mb-2">
                            {children}
                        </h3>
                    ),

                    // Paragraphs
                    p: ({ children }) => (
                        <p className="text-sm text-gray-200 leading-relaxed mb-3">
                            {children}
                        </p>
                    ),

                    // Lists
                    ul: ({ children }) => (
                        <ul className="list-none space-y-2 mb-4 ml-2">
                            {children}
                        </ul>
                    ),
                    ol: ({ children }) => (
                        <ol className="list-decimal list-inside space-y-2 mb-4 ml-4 text-gray-200">
                            {children}
                        </ol>
                    ),
                    li: ({ children }) => (
                        <li className="text-sm text-gray-200 leading-relaxed pl-2 flex items-start">
                            <span className="text-emerald-400 mr-2 mt-0.5 flex-shrink-0">•</span>
                            <span className="flex-1">{children}</span>
                        </li>
                    ),

                    // Emphasis
                    strong: ({ children }) => (
                        <strong className="font-semibold text-emerald-300">
                            {children}
                        </strong>
                    ),
                    em: ({ children }) => (
                        <em className="italic text-gray-300">
                            {children}
                        </em>
                    ),

                    // Code
                    code: ({ children, className }) => {
                        const isBlock = className?.includes('language-')
                        if (isBlock) {
                            return (
                                <code className="block bg-gray-900/50 text-emerald-300 p-3 rounded mb-3 text-sm font-mono overflow-x-auto">
                                    {children}
                                </code>
                            )
                        }
                        return (
                            <code className="bg-gray-900/50 text-emerald-300 px-1.5 py-0.5 rounded text-sm font-mono">
                                {children}
                            </code>
                        )
                    },

                    // Links
                    a: ({ href, children }) => (
                        <a
                            href={href}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-emerald-400 hover:text-emerald-300 underline transition-colors"
                        >
                            {children}
                        </a>
                    ),

                    // Blockquote
                    blockquote: ({ children }) => (
                        <blockquote className="border-l-4 border-emerald-500 pl-4 py-2 mb-3 text-gray-300 italic bg-gray-800/30 rounded-r">
                            {children}
                        </blockquote>
                    ),
                }}
            >
                {content}
            </ReactMarkdown>
        </div>
    )
}
