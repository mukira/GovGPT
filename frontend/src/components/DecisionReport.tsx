/**
 * DecisionReport Component
 * Renders structured decision reports for government decision-makers
 * Following Cabinet/PS-level briefing format
 */

interface DecisionReportProps {
    report: {
        decision_required: string
        timeline: string
        accountable: string
        executive_summary: {
            recommendation: string
            rationale: string
            key_risks: string[]
            expected_impact: string
        }
        options: Array<{
            name: string
            description: string
            benefits: string[]
            risks: string[]
            tradeoffs: string
            cost: string
            impact_score: string
        }>
        recommended_option: string
        recommendation_rationale: string
        impact_breakdown: {
            economic: string
            social: string
            regional: {
                counties_benefiting: string[]
                counties_affected: string[]
                magnitude: string
            }
            population: {
                groups_affected: string[]
                total_citizens: string
                demographics: string
            }
            budget: string
            sentiment?: string
        }
        risks_mitigations: Array<{
            risk: string
            likelihood: string
            impact: string
            mitigation: string
            owner: string
        }>
        next_steps: Array<{
            action: string
            responsible: string
            deadline: string
            priority: string
        }>
        data_sources: string[]
        assumptions?: string[]
        limitations?: string
    }
}

export function DecisionReport({ report }: DecisionReportProps) {
    return (
        <div className="decision-report bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl p-6 space-y-6 border border-slate-700 shadow-2xl">
            {/* Decision Header */}
            <div className="bg-gradient-to-r from-emerald-600 to-teal-600 rounded-lg p-6 text-white">
                <div className="flex items-start justify-between">
                    <div className="flex-1">
                        <div className="text-xs uppercase tracking-wide text-emerald-100 mb-2">Decision Required</div>
                        <h2 className="text-2xl font-bold mb-3">{report.decision_required}</h2>
                        <div className="flex gap-6 text-sm">
                            <div>
                                <span className="text-emerald-100">Timeline:</span>
                                <span className="ml-2 font-semibold">{report.timeline}</span>
                            </div>
                            <div>
                                <span className="text-emerald-100">Accountable:</span>
                                <span className="ml-2 font-semibold">{report.accountable}</span>
                            </div>
                        </div>
                    </div>
                    <div className="bg-white/20 backdrop-blur px-4 py-2 rounded-lg">
                        <div className="text-xs text-emerald-100">Report Type</div>
                        <div className="text-lg font-bold">Cabinet Brief</div>
                    </div>
                </div>
            </div>

            {/* Executive Summary */}
            <ExecutiveSummary summary={report.executive_summary} />

            {/* Options Analysis */}
            <OptionsTable
                options={report.options}
                recommended={report.recommended_option}
                rationale={report.recommendation_rationale}
            />

            {/* Impact Breakdown */}
            <ImpactBreakdown impact={report.impact_breakdown} />

            {/* Risks & Mitigations */}
            <RisksTable risks={report.risks_mitigations} />

            {/* Next Steps */}
            <NextSteps steps={report.next_steps} />

            {/* Data Sources */}
            <DataSources
                sources={report.data_sources}
                assumptions={report.assumptions}
                limitations={report.limitations}
            />
        </div>
    )
}

// Executive Summary Component
function ExecutiveSummary({ summary }: { summary: DecisionReportProps['report']['executive_summary'] }) {
    return (
        <div className="bg-slate-800/50 rounded-lg p-5 border border-emerald-500/30">
            <h3 className="text-emerald-400 font-bold text-lg mb-4 flex items-center gap-2">
                <span className="text-2xl">📊</span>
                Executive Summary
            </h3>

            <div className="space-y-4">
                <div>
                    <div className="text-xs text-slate-400 uppercase tracking-wide mb-1">Recommendation</div>
                    <p className="text-white font-medium">{summary.recommendation}</p>
                </div>

                <div>
                    <div className="text-xs text-slate-400 uppercase tracking-wide mb-1">Rationale</div>
                    <p className="text-slate-300">{summary.rationale}</p>
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                    <div>
                        <div className="text-xs text-emerald-400 uppercase tracking-wide mb-2">Key Risks</div>
                        <ul className="space-y-1">
                            {summary.key_risks.map((risk, idx) => (
                                <li key={idx} className="text-slate-300 text-sm flex items-start gap-2">
                                    <span className="text-red-400 mt-1">▸</span>
                                    <span>{risk}</span>
                                </li>
                            ))}
                        </ul>
                    </div>

                    <div>
                        <div className="text-xs text-emerald-400 uppercase tracking-wide mb-2">Expected Impact</div>
                        <p className="text-white font-semibold bg-emerald-900/30 rounded p-3 border border-emerald-500/30">
                            {summary.expected_impact}
                        </p>
                    </div>
                </div>
            </div>
        </div>
    )
}

// Options Table Component
function OptionsTable({
    options,
    recommended,
    rationale
}: {
    options: DecisionReportProps['report']['options']
    recommended: string
    rationale: string
}) {
    return (
        <div className="bg-slate-800/50 rounded-lg p-5 border border-slate-700">
            <h3 className="text-emerald-400 font-bold text-lg mb-4 flex items-center gap-2">
                <span className="text-2xl">⚖️</span>
                Options Analysis
            </h3>

            <div className="space-y-4">
                {options.map((option, idx) => {
                    const isRecommended = option.name === recommended
                    return (
                        <div
                            key={idx}
                            className={`rounded-lg p-4 border-2 ${isRecommended
                                ? 'bg-emerald-900/20 border-emerald-500'
                                : 'bg-slate-900/50 border-slate-700'
                                }`}
                        >
                            <div className="flex items-start justify-between mb-3">
                                <div>
                                    <h4 className="text-white font-bold text-lg">{option.name}</h4>
                                    <p className="text-slate-400 text-sm mt-1">{option.description}</p>
                                </div>
                                <div className="flex flex-col items-end gap-2">
                                    {isRecommended && (
                                        <span className="bg-emerald-600 text-white px-3 py-1 rounded-full text-xs font-bold">
                                            ⭐ RECOMMENDED
                                        </span>
                                    )}
                                    <span className={`px-3 py-1 rounded-full text-xs font-bold ${option.impact_score === 'High' ? 'bg-green-600 text-white' :
                                        option.impact_score === 'Medium' ? 'bg-yellow-600 text-white' :
                                            'bg-slate-600 text-white'
                                        }`}>
                                        Impact: {option.impact_score}
                                    </span>
                                </div>
                            </div>

                            <div className="grid md:grid-cols-3 gap-4 mt-4">
                                <div>
                                    <div className="text-xs text-emerald-400 uppercase mb-2">Benefits</div>
                                    <ul className="space-y-1">
                                        {option.benefits.map((benefit, bidx) => (
                                            <li key={bidx} className="text-slate-300 text-sm flex items-start gap-2">
                                                <span className="text-green-400">✓</span>
                                                <span>{benefit}</span>
                                            </li>
                                        ))}
                                    </ul>
                                </div>

                                <div>
                                    <div className="text-xs text-red-400 uppercase mb-2">Risks</div>
                                    <ul className="space-y-1">
                                        {option.risks.map((risk, ridx) => (
                                            <li key={ridx} className="text-slate-300 text-sm flex items-start gap-2">
                                                <span className="text-red-400">✗</span>
                                                <span>{risk}</span>
                                            </li>
                                        ))}
                                    </ul>
                                </div>

                                <div>
                                    <div className="text-xs text-slate-400 uppercase mb-2">Cost & Trade-offs</div>
                                    <div className="text-white font-semibold text-lg mb-2">{option.cost}</div>
                                    <p className="text-slate-400 text-sm italic">{option.tradeoffs}</p>
                                </div>
                            </div>
                        </div>
                    )
                })}
            </div>

            {rationale && (
                <div className="mt-4 bg-emerald-900/20 border border-emerald-500/30 rounded-lg p-4">
                    <div className="text-xs text-emerald-400 uppercase mb-2">Why This Recommendation?</div>
                    <p className="text-white">{rationale}</p>
                </div>
            )}
        </div>
    )
}

// Impact Breakdown Component
function ImpactBreakdown({ impact }: { impact: DecisionReportProps['report']['impact_breakdown'] }) {
    return (
        <div className="bg-slate-800/50 rounded-lg p-5 border border-slate-700">
            <h3 className="text-emerald-400 font-bold text-lg mb-4 flex items-center gap-2">
                <span className="text-2xl">📈</span>
                Impact Breakdown
            </h3>

            <div className="space-y-4">
                {/* Economic & Social */}
                <div className="grid md:grid-cols-2 gap-4">
                    <div className="bg-slate-900/50 rounded p-4">
                        <div className="text-xs text-blue-400 uppercase mb-2">Economic Impact</div>
                        <p className="text-slate-300">{impact.economic}</p>
                    </div>
                    <div className="bg-slate-900/50 rounded p-4">
                        <div className="text-xs text-purple-400 uppercase mb-2">Social Impact</div>
                        <p className="text-slate-300">{impact.social}</p>
                    </div>
                </div>

                {/* Regional */}
                <div className="bg-slate-900/50 rounded p-4">
                    <div className="text-xs text-emerald-400 uppercase mb-3">Regional Distribution</div>
                    <div className="grid md:grid-cols-2 gap-4">
                        <div>
                            <div className="text-xs text-green-400 mb-2">Counties Benefiting</div>
                            <div className="flex flex-wrap gap-2">
                                {impact.regional.counties_benefiting.map((county, idx) => (
                                    <span key={idx} className="bg-green-900/30 border border-green-500/30 text-green-300 px-2 py-1 rounded text-xs">
                                        {county}
                                    </span>
                                ))}
                            </div>
                        </div>
                        {impact.regional.counties_affected.length > 0 && (
                            <div>
                                <div className="text-xs text-orange-400 mb-2">Counties Affected</div>
                                <div className="flex flex-wrap gap-2">
                                    {impact.regional.counties_affected.map((county, idx) => (
                                        <span key={idx} className="bg-orange-900/30 border border-orange-500/30 text-orange-300 px-2 py-1 rounded text-xs">
                                            {county}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                    <p className="text-slate-400 text-sm mt-3 italic">{impact.regional.magnitude}</p>
                </div>

                {/* Population */}
                <div className="bg-slate-900/50 rounded p-4">
                    <div className="text-xs text-pink-400 uppercase mb-3">Population Impact</div>
                    <div className="grid md:grid-cols-3 gap-4 text-sm">
                        <div>
                            <div className="text-white font-bold text-2xl mb-1">{impact.population.total_citizens}</div>
                            <div className="text-slate-400">Total Citizens Affected</div>
                        </div>
                        <div>
                            <div className="text-xs text-slate-400 mb-2">Groups Affected</div>
                            <div className="space-y-1">
                                {impact.population.groups_affected.map((group, idx) => (
                                    <div key={idx} className="text-slate-300">{group}</div>
                                ))}
                            </div>
                        </div>
                        <div>
                            <div className="text-xs text-slate-400 mb-2">Demographics</div>
                            <p className="text-slate-300">{impact.population.demographics}</p>
                        </div>
                    </div>
                </div>

                {/* Budget */}
                <div className="bg-blue-900/20 border border-blue-500/30 rounded p-4">
                    <div className="text-xs text-blue-400 uppercase mb-2">Budget Implications</div>
                    <p className="text-white font-semibold">{impact.budget}</p>
                </div>

                {/* Sentiment */}
                {impact.sentiment && (
                    <div className="bg-purple-900/20 border border-purple-500/30 rounded p-4">
                        <div className="text-xs text-purple-400 uppercase mb-2">Public Sentiment</div>
                        <p className="text-white">{impact.sentiment}</p>
                    </div>
                )}
            </div>
        </div>
    )
}

// Risks Table Component
function RisksTable({ risks }: { risks: DecisionReportProps['report']['risks_mitigations'] }) {
    return (
        <div className="bg-slate-800/50 rounded-lg p-5 border border-slate-700">
            <h3 className="text-emerald-400 font-bold text-lg mb-4 flex items-center gap-2">
                <span className="text-2xl">⚠️</span>
                Risks & Mitigations
            </h3>

            <div className="space-y-3">
                {risks.map((risk, idx) => (
                    <div key={idx} className="bg-slate-900/50 rounded p-4 border border-slate-700">
                        <div className="flex items-start justify-between mb-3">
                            <h4 className="text-white font-semibold flex-1">{risk.risk}</h4>
                            <div className="flex gap-2">
                                <span className={`px-2 py-1 rounded text-xs font-bold ${risk.likelihood === 'High' ? 'bg-red-600 text-white' :
                                    risk.likelihood === 'Medium' ? 'bg-yellow-600 text-white' :
                                        'bg-green-600 text-white'
                                    }`}>
                                    Likelihood: {risk.likelihood}
                                </span>
                                <span className={`px-2 py-1 rounded text-xs font-bold ${risk.impact === 'High' ? 'bg-red-600 text-white' :
                                    risk.impact === 'Medium' ? 'bg-yellow-600 text-white' :
                                        'bg-green-600 text-white'
                                    }`}>
                                    Impact: {risk.impact}
                                </span>
                            </div>
                        </div>

                        <div className="grid md:grid-cols-2 gap-4 text-sm">
                            <div>
                                <div className="text-xs text-blue-400 uppercase mb-1">Mitigation Strategy</div>
                                <p className="text-slate-300">{risk.mitigation}</p>
                            </div>
                            <div>
                                <div className="text-xs text-emerald-400 uppercase mb-1">Responsible Owner</div>
                                <p className="text-white font-semibold">{risk.owner}</p>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}

// Next Steps Component
function NextSteps({ steps }: { steps: DecisionReportProps['report']['next_steps'] }) {
    return (
        <div className="bg-slate-800/50 rounded-lg p-5 border border-slate-700">
            <h3 className="text-emerald-400 font-bold text-lg mb-4 flex items-center gap-2">
                <span className="text-2xl">🎯</span>
                Next Steps
            </h3>

            <div className="space-y-3">
                {steps.map((step, idx) => (
                    <div key={idx} className="flex items-start gap-4 bg-slate-900/50 rounded p-4">
                        <div className="text-2xl font-bold text-emerald-500">{idx + 1}</div>
                        <div className="flex-1">
                            <h4 className="text-white font-semibold mb-2">{step.action}</h4>
                            <div className="flex gap-4 text-sm">
                                <div>
                                    <span className="text-slate-400">Responsible:</span>
                                    <span className="ml-2 text-white">{step.responsible}</span>
                                </div>
                                <div>
                                    <span className="text-slate-400">Deadline:</span>
                                    <span className="ml-2 text-white">{step.deadline}</span>
                                </div>
                                <span className={`px-2 py-1 rounded text-xs font-bold ${step.priority === 'High' ? 'bg-red-600 text-white' :
                                    step.priority === 'Medium' ? 'bg-yellow-600 text-white' :
                                        'bg-blue-600 text-white'
                                    }`}>
                                    {step.priority} Priority
                                </span>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}

// Data Sources Component
function DataSources({
    sources,
    assumptions,
    limitations
}: {
    sources: string[]
    assumptions?: string[]
    limitations?: string
}) {
    return (
        <div className="bg-slate-800/50 rounded-lg p-5 border border-slate-700">
            <h3 className="text-emerald-400 font-bold text-lg mb-4 flex items-center gap-2">
                <span className="text-2xl">📚</span>
                Data Sources & Transparency
            </h3>

            <div className="space-y-4">
                <div>
                    <div className="text-xs text-blue-400 uppercase mb-2">Data Sources</div>
                    <ul className="space-y-1">
                        {sources.map((source, idx) => (
                            <li key={idx} className="text-slate-300 text-sm flex items-start gap-2">
                                <span className="text-blue-400">📄</span>
                                <span>{source}</span>
                            </li>
                        ))}
                    </ul>
                </div>

                {assumptions && assumptions.length > 0 && (
                    <div>
                        <div className="text-xs text-yellow-400 uppercase mb-2">Key Assumptions</div>
                        <ul className="space-y-1">
                            {assumptions.map((assumption, idx) => (
                                <li key={idx} className="text-slate-300 text-sm flex items-start gap-2">
                                    <span className="text-yellow-400">▸</span>
                                    <span>{assumption}</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                )}

                {limitations && (
                    <div className="bg-orange-900/20 border border-orange-500/30 rounded p-3">
                        <div className="text-xs text-orange-400 uppercase mb-2">Limitations</div>
                        <p className="text-slate-300 text-sm italic">{limitations}</p>
                    </div>
                )}
            </div>
        </div>
    )
}
